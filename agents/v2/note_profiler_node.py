import os
from google.adk.agents import LlmAgent
from agents.v2.models import NoteProfile
from agents.v2.guardrails import pre_profiler_guardrail_callback

with open(os.path.join(os.path.dirname(__file__), "..", "..", "docs", "v2-planning-implementation-artifacts", "NOTE_PROFILER_AGENT_PROMPT.md"), "r", encoding="utf-8") as f:
    PROMPT_TEXT = f.read()

def get_note_profiler_agent(provider: str = None) -> LlmAgent:
    """Returns a NoteProfiler LlmAgent. BYOK model injection happens in the guardrail callback."""
    # We set a dummy model here; it will be overwritten per-request in the before_model_callback.
    from google.adk.models.lite_llm import LiteLlm
    return LlmAgent(
        name="note_profiler",
        model=LiteLlm(model="gemini/gemini-3.1-flash-lite"),
        instruction=PROMPT_TEXT,
        output_schema=NoteProfile,
        output_key="note_profile",
        before_model_callback=pre_profiler_guardrail_callback,
        rerun_on_resume=True
    )
