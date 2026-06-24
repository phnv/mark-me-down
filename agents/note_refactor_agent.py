from models.request_models import RefactorRequest
from models.response_models import RefactorResponse
from agents.prompt_builder import build_prompt_messages
from services.openai_service import OpenAIService
from services.filename_service import suggest_filename
from config import DEFAULT_MODEL

class NoteRefactorAgent:
    """Agent that coordinates prompt construction, LLM calls, and response validation."""

    def __init__(self, openai_service: OpenAIService):
        """Initializes the agent with an OpenAIService instance."""
        self.openai_service = openai_service

    def refactor(self, request: RefactorRequest) -> RefactorResponse:
        """Processes the refactoring request, interacts with OpenAI, and returns a validated response."""
        # 1. Build chat messages
        messages = build_prompt_messages(
            raw_text=request.raw_text,
            mode=request.refactor_mode,
            style=request.output_style,
            template_instruction=request.template_instruction,
            template_description=request.template_description,
            include_frontmatter=request.include_frontmatter
        )
        
        # 2. Query OpenAI API
        formatted_markdown = self.openai_service.generate_chat_completion(
            messages=messages,
            model=DEFAULT_MODEL
        )
        
        # 3. Suggest a safe download filename from markdown output
        suggested_fn = suggest_filename(formatted_markdown)
        
        # 4. Construct and return response model
        return RefactorResponse(
            formatted_markdown=formatted_markdown,
            suggested_filename=suggested_fn
        )
