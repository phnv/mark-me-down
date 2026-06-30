from google.adk.agents import LlmAgent
from google.adk.workflow import node
from google.genai import types
from agents.v2.models import UserRefactorRequest, NoteProfile, TemplateMatch
from agents.prompt_builder import build_system_prompt
from agents.v2.guardrails import pre_workflow_guardrail_callback, post_workflow_guardrail_callback


def _dbg(label: str, value=None):
    print(f"\n[DBG] ──── {label} ────")
    if value is not None:
        print(f"       {repr(value)[:300]}")


@node
def prepare_refactor_prompt(ctx, node_input) -> types.Content:
    """Prepares the prompt content for the NoteRefactorAgent."""
    _dbg("prepare_refactor_prompt ENTRY", f"node_input type={type(node_input)}")
    # _dbg("prepare_refactor_prompt: ctx.state keys", list(dict(ctx.state)))

    # FIX: ADK stores Pydantic models as dicts in state — reconstruct typed objects
    raw_request = ctx.state.get("request")
    _dbg("prepare_refactor_prompt: raw_request from state", raw_request)
    request: UserRefactorRequest = UserRefactorRequest(**raw_request) if isinstance(raw_request, dict) else raw_request
    
    # FIX: Reconstruct typed objects from state dicts
    raw_template_match = ctx.state.get("template_match")
    _dbg("prepare_refactor_prompt: raw_template_match from state", raw_template_match)
    template_match: TemplateMatch = TemplateMatch(**raw_template_match) if isinstance(raw_template_match, dict) else raw_template_match

    raw_note_profile = ctx.state.get("note_profile")
    _dbg("prepare_refactor_prompt: raw_note_profile from state", raw_note_profile)
    note_profile: NoteProfile = NoteProfile(**raw_note_profile) if isinstance(raw_note_profile, dict) else raw_note_profile
    
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

    _dbg("prepare_refactor_prompt EXIT",
         f"template_match={'yes (id=' + template_match.id + ')' if template_match else 'None'}, "
         f"note_profile={'yes' if note_profile else 'None'}, "
         f"combined_prompt_len={len(combined_prompt)}")

    return types.Content(role="user", parts=[types.Part.from_text(text=combined_prompt)])

def get_note_refactor_agent(provider: str) -> LlmAgent:
    """Returns a NoteRefactor LlmAgent configured for the selected provider."""
    if provider.lower() == "openai":
        from google.adk.models.lite_llm import LiteLlm
        model = LiteLlm(model="openai/gpt-4o-mini")
    else:
        model = "gemini-3.1-flash-lite"

        
    return LlmAgent(
        name="note_refactor",
        model=model,
        instruction="You are a markdown formatting assistant. Follow the system instructions exactly.",
        output_key="refactored_markdown",
        before_model_callback=pre_workflow_guardrail_callback,
        after_model_callback=post_workflow_guardrail_callback,
        rerun_on_resume=True
    )
