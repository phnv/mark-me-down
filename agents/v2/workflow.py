from google.adk.workflow import Workflow, node
from google.adk.events.event import Event
from google.adk.agents.context import Context
from agents.v2.models import UserRefactorRequest, NoteProfile, TemplateMatch
from agents.v2.note_profiler_node import get_note_profiler_agent
from agents.v2.note_refactor_node import prepare_refactor_prompt, get_note_refactor_agent
from services.rag_service import note_profile_to_embedding_text, generate_embedding, search_template, fetch_all_templates

@node
def router_node(ctx: Context, node_input: dict) -> Event:
    """Parses initial request and routes to either auto or manual template path."""
    request = UserRefactorRequest(**node_input)
    # Store request in state for downstream nodes
    ctx.state["request"] = request
    
    if request.template_selection == "auto":
        return Event(output=request.raw_text, route="auto")
    else:
        # Manual template selection
        templates = fetch_all_templates()
        selected = next((t for t in templates if str(t.get("id")) == str(request.template_selection)), None)
        if selected:
            template_match = TemplateMatch(
                id=str(selected.get("id")),
                name=selected.get("name"),
                description=selected.get("description", ""),
                instructions=selected.get("instructions", ""),
                template_markdown=selected.get("template_markdown", ""),
                similarity=1.0
            )
            ctx.state["template_match"] = template_match
        return Event(output=request.raw_text, route="manual")

@node
def rag_search_node(ctx: Context, node_input: dict) -> dict:
    """Uses the NoteProfile to search for the best template in Supabase."""
    try:
        profile = NoteProfile(**node_input)
        ctx.state["note_profile"] = profile
        
        text_to_embed = note_profile_to_embedding_text(profile)
        
        provider = ctx.state.get("provider", "gemini")
        api_key = ctx.state.get("api_key", "")
        
        embedding = generate_embedding(text_to_embed, provider, api_key)
        match = search_template(embedding)
        
        if match:
            ctx.state["template_match"] = match
            
        return {"status": "success"}
    except Exception as e:
        print(f"Error in rag_search_node: {e}")
        return {"status": "error"}

def get_refactor_workflow(provider: str) -> Workflow:
    """Returns a Workflow instance configured with agents for the selected provider."""
    note_profiler_agent = get_note_profiler_agent(provider)
    note_refactor_agent = get_note_refactor_agent(provider)
    
    return Workflow(
        name="refactor_workflow",
        edges=[
            ('START', router_node),
            (router_node, note_profiler_agent, "auto"),
            (note_profiler_agent, rag_search_node),
            (rag_search_node, prepare_refactor_prompt),
            (router_node, prepare_refactor_prompt, "manual"),
            (prepare_refactor_prompt, note_refactor_agent)
        ]
    )
