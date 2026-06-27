from google.adk.agents import LlmAgent
from google.adk.workflow import node
from google.genai import types
from agents.v2.models import UserRefactorRequest, NoteProfile, TemplateMatch
from agents.prompt_builder import build_system_prompt

@node
def prepare_refactor_prompt(ctx, node_input: dict) -> types.Content:
    """Prepares the prompt content for the NoteRefactorAgent."""
    
    # Extract the original request from state
    request: UserRefactorRequest = ctx.state.get("request")
    
    # Extract template info from state if available
    template_match: TemplateMatch = ctx.state.get("template_match")
    
    # Extract profile from state if available
    note_profile: NoteProfile = ctx.state.get("note_profile")
    
    template_instruction = None
    template_description = None
    
    if template_match:
        template_instruction = template_match.instructions
        template_description = template_match.description
    elif note_profile:
        template_instruction = note_profile.instructions
        template_description = note_profile.description
        
    system_prompt = build_system_prompt(
        mode=request.refactor_mode,
        style=request.rewrite_mode,
        template_instruction=template_instruction,
        template_description=template_description,
        include_frontmatter=request.include_frontmatter
    )
    
    if template_match and template_match.template_markdown:
        system_prompt += f"\n\nTEMPLATE TO USE:\n{template_match.template_markdown}\n"
    
    user_text = f"Here is the raw note to refactor:\n\n{request.raw_text}"
    
    # ADK LlmAgent expects types.Content if we want to pass both system and user, 
    # we can combine them into a single user message or use system instructions.
    # We will combine them as the instruction is dynamic.
    combined_prompt = f"System Instructions:\n{system_prompt}\n\nUser Request:\n{user_text}"
    
    return types.Content(role="user", parts=[types.Part.from_text(text=combined_prompt)])

def get_note_refactor_agent(provider: str) -> LlmAgent:
    """Returns a NoteRefactor LlmAgent configured for the selected provider."""
    if provider.lower() == "openai":
        from google.adk.models.lite_llm import LiteLlm
        model = LiteLlm(model="openai/gpt-4o-mini")
    else:
        model = "gemini-2.5-pro"
        
    return LlmAgent(
        name="note_refactor",
        model=model,
        instruction="You are a markdown formatting assistant. Follow the system instructions exactly.",
        output_key="refactored_markdown",
        rerun_on_resume=True
    )
