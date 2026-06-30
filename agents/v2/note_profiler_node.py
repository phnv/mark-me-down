import os
from google.adk.agents import LlmAgent
from agents.v2.models import NoteProfile
from agents.v2.guardrails import pre_workflow_guardrail_callback

with open(os.path.join(os.path.dirname(__file__), "..", "..", "docs", "v2-planning-implementation-artifacts", "NOTE_PROFILER_AGENT_PROMPT.md"), "r", encoding="utf-8") as f:
    PROMPT_TEXT = f.read()

def get_note_profiler_agent(provider: str) -> LlmAgent:
    """Returns a NoteProfiler LlmAgent configured for the selected provider."""
    if provider.lower() == "openai":
        from google.adk.models.lite_llm import LiteLlm
        model = LiteLlm(model="openai/gpt-4o-mini")
    else:
        # model = "gemini-2.5-pro" #gemini-3.1-flash-lite
        model = "gemini-3.1-flash-lite"
        
    return LlmAgent(
        name="note_profiler",
        model=model,
        instruction=PROMPT_TEXT,
        output_schema=NoteProfile,
        output_key="note_profile",
        before_model_callback=pre_workflow_guardrail_callback,
        rerun_on_resume=True
    )
