from google.adk.workflow import Workflow, node
from google.adk.events.event import Event
from google.adk.agents.context import Context
from agents.v2.models import UserRefactorRequest, NoteProfile, TemplateMatch
from agents.v2.note_profiler_node import get_note_profiler_agent
from agents.v2.note_refactor_node import prepare_refactor_prompt, get_note_refactor_agent
from services.rag_service import note_profile_to_embedding_text, generate_embedding, search_template, fetch_all_templates

import json
from google.genai import types

# ---------------------------------------------------------------------------
# DEBUG HELPER
# ---------------------------------------------------------------------------
def _dbg(label: str, value=None):
    """Prints a clearly delimited debug line."""
    print(f"\n[DBG] ──── {label} ────")
    if value is not None:
        print(f"       {repr(value)}")


# ---------------------------------------------------------------------------
# router_node
# ---------------------------------------------------------------------------
@node
def router_node(ctx: Context, node_input) -> Event:
    """Parses initial request and routes to either auto or manual template path."""
    _dbg("router_node ENTRY", f"node_input type={type(node_input)}")

    # --- Parse raw input (types.Content, dict, or JSON string) -----------
    if hasattr(node_input, 'parts') and len(node_input.parts) > 0:
        raw_text = node_input.parts[0].text
        _dbg("router_node: parsing from Content.parts[0].text", raw_text[:200])
        data = json.loads(raw_text)
    elif isinstance(node_input, dict):
        _dbg("router_node: node_input is already a dict")
        data = node_input
    else:
        raw_str = str(node_input)
        _dbg("router_node: fallback str parse", raw_str[:200])
        data = json.loads(raw_str)

    _dbg("router_node: parsed data keys", list(data.keys()))

    request = UserRefactorRequest(**data)
    _dbg("router_node: UserRefactorRequest", request.model_dump())

    # --- Read provider/api_key from state (pre-injected by runner) --------
    provider = ctx.state.get("provider", "gemini")
    api_key = ctx.state.get("api_key", "")
    _dbg("router_node: state['provider']", provider)
    _dbg("router_node: state['api_key'] present", bool(api_key))

    route = "auto" if request.template_selection == "auto" else "manual"
    _dbg("router_node: selected route", route)

    # FIX: Use Event(state=...) instead of ctx.state[...] = ...
    # ADK only persists state that travels via Event.state deltas.
    state_delta = {"request": request.model_dump()}

    if route == "manual":
        templates = fetch_all_templates()
        _dbg("router_node: fetch_all_templates count", len(templates))
        selected = next(
            (t for t in templates if str(t.get("id")) == str(request.template_selection)),
            None,
        )
        _dbg("router_node: manual selected template", selected)
        if selected:
            template_match = TemplateMatch(
                id=str(selected.get("id")),
                name=selected.get("name"),
                description=selected.get("description", ""),
                instructions=selected.get("instructions", ""),
                template_markdown=selected.get("template_markdown", ""),
                similarity=1.0,
            )
            # Store as dict so ADK can serialize it
            state_delta["template_match"] = template_match.model_dump()
            _dbg("router_node: template_match stored in state_delta", template_match.id)
        else:
            _dbg("router_node: WARNING — manual template not found for id", request.template_selection)

    _dbg("router_node EXIT", f"route={route}, state_delta keys={list(state_delta.keys())}")
    return Event(output=request.raw_text, route=route, state=state_delta)


# ---------------------------------------------------------------------------
# rag_search_node
# ---------------------------------------------------------------------------
@node
def rag_search_node(ctx: Context, node_input) -> Event:
    """Uses the NoteProfile output from note_profiler to search for best template."""
    _dbg("rag_search_node ENTRY", f"node_input type={type(node_input)}")
    _dbg("rag_search_node: node_input value", repr(node_input)[:400])

    try:
        # LlmAgent with output_schema delivers node_input as dict (not BaseModel)
        if isinstance(node_input, dict):
            _dbg("rag_search_node: constructing NoteProfile from dict")
            profile = NoteProfile(**node_input)
        elif isinstance(node_input, NoteProfile):
            _dbg("rag_search_node: node_input is already NoteProfile")
            profile = node_input
        else:
            _dbg("rag_search_node: WARNING unexpected node_input type — trying dict cast")
            profile = NoteProfile(**dict(node_input))

        _dbg("rag_search_node: NoteProfile built", profile.model_dump())

        text_to_embed = note_profile_to_embedding_text(profile)
        _dbg("rag_search_node: text_to_embed (first 200 chars)", text_to_embed[:200])

        provider = ctx.state.get("provider", "gemini")
        api_key = ctx.state.get("api_key", "")
        _dbg("rag_search_node: provider from state", provider)
        _dbg("rag_search_node: api_key present", bool(api_key))

        embedding = generate_embedding(text_to_embed, provider, api_key)
        _dbg("rag_search_node: embedding generated, len", len(embedding) if embedding else "None")

        match = search_template(embedding)
        _dbg("rag_search_node: search_template result", match)

        state_delta = {"note_profile": profile.model_dump()}
        if match:
            _dbg("rag_search_node: template match FOUND", match)
            # Ensure match is a serializable dict
            if isinstance(match, TemplateMatch):
                state_delta["template_match"] = match.model_dump()
            elif isinstance(match, dict):
                state_delta["template_match"] = match
            else:
                _dbg("rag_search_node: WARNING unexpected match type", type(match))
        else:
            _dbg("rag_search_node: NO template match found — template_match will be None")

        _dbg("rag_search_node EXIT", f"state_delta keys={list(state_delta.keys())}")
        # FIX: propagate via Event.state instead of ctx.state mutation
        return Event(output={"status": "success"}, state=state_delta)

    except Exception as e:
        import traceback
        _dbg("rag_search_node ERROR", str(e))
        traceback.print_exc()
        return Event(output={"status": "error", "error": str(e)})


# ---------------------------------------------------------------------------
# Workflow factory
# ---------------------------------------------------------------------------
def get_refactor_workflow(provider: str) -> Workflow:
    """Returns a Workflow instance configured with agents for the selected provider."""
    _dbg("get_refactor_workflow: building workflow for provider", provider)
    note_profiler_agent = get_note_profiler_agent(provider)
    note_refactor_agent = get_note_refactor_agent(provider)

    # FIX: conditional routing uses separate edge tuples with route string,
    # NOT a dict as the target. The old `{route: node}` dict syntax is wrong.
    return Workflow(
        name="refactor_workflow",
        edges=[
            ('START', router_node),
            # Conditional routing: dict maps route value -> target node
            # This is the correct syntax for the installed ADK version
            (router_node, {
                "auto": note_profiler_agent,
                "manual": prepare_refactor_prompt,
            }),
            (note_profiler_agent, rag_search_node),
            (rag_search_node, prepare_refactor_prompt),
            (prepare_refactor_prompt, note_refactor_agent),
        ]
    )
