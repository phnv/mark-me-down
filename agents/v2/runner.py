import asyncio
import os
import sys
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from google.genai import types
from agents.v2.workflow import get_refactor_workflow
from agents.v2.models import TemplateMatch
from agents.v2.guardrails import GUARDRAIL_PREFIX

# Workaround for Python Windows asyncio ProactorBasePipeTransport bug
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def _dbg(label: str, value=None):
    print(f"\n[DBG] ──── {label} ────")
    if value is not None:
        print(f"       {repr(value)}")


def run_workflow_sync(request_dict: dict, provider: str, api_key: str):
    """Synchronous wrapper to run the ADK workflow and extract the result."""

    # Set the API keys in the environment so ADK models can pick them up
    if provider.lower() == "gemini":
        os.environ["GEMINI_API_KEY"] = api_key
    elif provider.lower() == "openai":
        os.environ["OPENAI_API_KEY"] = api_key

    _dbg("run_workflow_sync: provider", provider)
    _dbg("run_workflow_sync: request_dict keys", list(request_dict.keys()))

    refactor_workflow = get_refactor_workflow(provider)
    workflow_app = App(name="mark-me-down-v2", root_agent=refactor_workflow)
    runner = InMemoryRunner(app=workflow_app)

    return asyncio.run(_run_workflow_async(runner, request_dict, provider, api_key))


async def _run_workflow_async(runner, request_dict: dict, provider: str, api_key: str):
    session = await runner.session_service.create_session(
        app_name="mark-me-down-v2", user_id="local_user"
    )
    _dbg("_run_workflow_async: session created", session.id)

    # Pre-inject provider and api_key into state so nodes can read them.
    # NOTE: InMemorySessionService keeps a reference — mutations before run_async
    # ARE visible inside ctx.state during execution.
    session.state["provider"] = provider
    session.state["api_key"] = api_key
    _dbg("_run_workflow_async: session.state pre-seeded", {"provider": provider, "api_key": bool(api_key)})

    import json

    message_content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=json.dumps(request_dict))]
    )
    _dbg("_run_workflow_async: sending message to runner")

    event_count = 0

    async for event in runner.run_async(
        user_id="local_user",
        session_id=session.id,
        new_message=message_content
    ):
        event_count += 1
        _dbg(
            f"event #{event_count}",
            {
                "author": getattr(event, "author", None),
                "output_type": type(event.output).__name__ if event.output is not None else "None",
                "output_preview": repr(event.output)[:200] if event.output is not None else None,
                "route": getattr(event, "route", None),
                "state_delta": getattr(event, "state", None),
            }
        )
        # NOTE: do NOT capture event.output here — intermediate nodes (router_node)
        # also emit output (the raw text for routing) which would overwrite the real result.
        # The note_refactor LlmAgent writes its output to state["refactored_markdown"]
        # via output_key=, not to event.output. We read state after the run instead.
        if event.output is not None and isinstance(event.output, dict) and event.output.get("status") == "error":
            _dbg(f"event #{event_count}: WARNING — received error event", event.output)

    _dbg("_run_workflow_async: all events consumed", f"total events={event_count}")

    # -------------------------------------------------------------------
    # FIX: Read state from the live session object — InMemorySessionService
    # updates the same in-memory session object referenced by session.state.
    # However, state written via Event.state deltas is applied by the runner.
    # We must re-fetch the session to get the post-run state.
    # -------------------------------------------------------------------
    updated_session = await runner.session_service.get_session(
        app_name="mark-me-down-v2",
        user_id="local_user",
        session_id=session.id,
    )

    _dbg("_run_workflow_async: updated_session.state keys", list(dict(updated_session.state)))
    _dbg("_run_workflow_async: updated_session.state", repr(dict(updated_session.state))[:800])

    # PRIMARY OUTPUT: read from state["refactored_markdown"] written by note_refactor
    # via output_key=. LlmAgent nodes do NOT emit their result via event.output —
    # they write to state. Capturing event.output would only get intermediate routing values.
    raw_refactored = updated_session.state.get("refactored_markdown")
    _dbg("_run_workflow_async: raw refactored_markdown from state", repr(raw_refactored)[:300] if raw_refactored else "None")

    if raw_refactored:
        if isinstance(raw_refactored, str):
            final_output = raw_refactored
        elif isinstance(raw_refactored, types.Content):
            final_output = raw_refactored.parts[0].text
        else:
            final_output = str(raw_refactored)
        _dbg("_run_workflow_async: final_output set from refactored_markdown", f"len={len(final_output)}")

        # --- Guardrail sentinel detection -----------------------------------
        # Both pre- and post-workflow callbacks prefix blocked responses with
        # GUARDRAIL_PREFIX so we can distinguish them from real markdown output.
        if final_output.startswith(GUARDRAIL_PREFIX):
            reason = final_output[len(GUARDRAIL_PREFIX):].strip()
            _dbg("_run_workflow_async: GUARDRAIL triggered", reason)
            return None, "GUARDRAIL", reason
        # --------------------------------------------------------------------
    else:
        final_output = None
        _dbg("_run_workflow_async: WARNING — refactored_markdown not found in state")

    raw_template_match = updated_session.state.get("template_match")
    _dbg("_run_workflow_async: raw_template_match from state", raw_template_match)

    # Reconstruct TemplateMatch from the dict ADK stored
    template_match = None
    similarity_score = None

    if raw_template_match is not None:
        if isinstance(raw_template_match, dict):
            try:
                template_match = TemplateMatch(**raw_template_match)
                _dbg("_run_workflow_async: TemplateMatch reconstructed from dict", template_match.id)
            except Exception as e:
                _dbg("_run_workflow_async: ERROR reconstructing TemplateMatch", str(e))
        elif isinstance(raw_template_match, TemplateMatch):
            template_match = raw_template_match
            _dbg("_run_workflow_async: template_match was already TemplateMatch")
        else:
            _dbg("_run_workflow_async: WARNING unexpected template_match type", type(raw_template_match))

        if template_match:
            similarity_score = template_match.similarity
            _dbg("_run_workflow_async: similarity_score", similarity_score)
    else:
        _dbg("_run_workflow_async: template_match is None — RAG found no match or auto path error")

    if not final_output:
        _dbg("_run_workflow_async: WARNING — no final_output, returning error fallback")
        final_output = "Error: No markdown output was generated by the workflow."

    _dbg("_run_workflow_async: DONE", {
        "final_output_len": len(final_output),
        "similarity_score": similarity_score,
        "template_match_id": template_match.id if template_match else None,
    })

    return final_output, similarity_score, template_match
