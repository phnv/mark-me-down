import os
from pathlib import Path
from dotenv import load_dotenv

# Ensure environment variables are loaded for OpenAI authentication
PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from .models import NoteProfile, TemplateProfile


PROMPT_PATH = Path(__file__).resolve().parent / "TEMPLATE_PROMPT.md"
with open(PROMPT_PATH, "r", encoding="utf-8") as f:
    instruction = f.read()

from google.adk.models import Gemini
from google.adk.workflow import Workflow

def create_agent(model_provider: str = "openai") -> Workflow:
    """
    Create the note_profiler Workflow.
    
    Args:
        model_provider (str): "openai" to use LiteLlm, or "gemini" to use built-in Gemini model.
    """
    if model_provider.lower() == "gemini":
        model = Gemini(model="gemini-2.5-flash")
    else:
        model = LiteLlm(model="openai/gpt-4o-mini")
        
    note_profiler_llm = Agent(
        name="note_profiler_llm",
        model=model,
        instruction=instruction,
        output_schema=NoteProfile,
        output_key="profile_data",
        mode="single_turn",
    )

    return Workflow(
        name="note_profiler",
        edges=[('START', note_profiler_llm)],
        output_schema=NoteProfile,
    )

root_agent = create_agent(model_provider=os.getenv("MODEL_PROVIDER", "openai"))
