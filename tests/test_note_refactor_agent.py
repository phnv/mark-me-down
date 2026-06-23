from models.request_models import RefactorRequest
from agents.note_refactor_agent import NoteRefactorAgent
from services.openai_service import OpenAIService
from config import REFACTOR_CONSERVATIVE, STYLE_ADAPTIVE

def test_note_refactor_agent_refactor(mocker):
    """Verifies that NoteRefactorAgent coordinates prompt generation, OpenAI call, and filename suggestion correctly."""
    # Mock OpenAIService dependency
    mock_service = mocker.Mock(spec=OpenAIService)
    mock_service.generate_chat_completion.return_value = "# Target Document Title\n- Item 1\n- Item 2"
    
    agent = NoteRefactorAgent(openai_service=mock_service)
    
    request = RefactorRequest(
        raw_text="messy content",
        refactor_mode=REFACTOR_CONSERVATIVE,
        output_style=STYLE_ADAPTIVE
    )
    
    response = agent.refactor(request)
    
    assert response.formatted_markdown == "# Target Document Title\n- Item 1\n- Item 2"
    assert response.suggested_filename == "target-document-title.md"
    
    # Assert service was called with the compiled messages
    mock_service.generate_chat_completion.assert_called_once()
    _, kwargs = mock_service.generate_chat_completion.call_args
    messages = kwargs.get("messages")
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
