import pytest
from services.openai_service import OpenAIService

def test_openai_service_init_no_key(monkeypatch):
    """Verifies that value error is raised when no API key is supplied."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OpenAI API key is required."):
        OpenAIService()

def test_openai_service_init_with_key():
    """Verifies service initialization with a custom API key."""
    service = OpenAIService(api_key="test-key")
    assert service.api_key == "test-key"

def test_openai_service_chat_completion(mocker):
    """Verifies successful API interaction and completion response parsing."""
    service = OpenAIService(api_key="test-key")
    
    # Mock client.chat.completions.create
    mock_create = mocker.patch.object(service.client.chat.completions, "create")
    mock_response = mocker.Mock()
    mock_choice = mocker.Mock()
    mock_choice.message.content = "formatted markdown"
    mock_response.choices = [mock_choice]
    mock_create.return_value = mock_response
    
    messages = [{"role": "user", "content": "raw note"}]
    res = service.generate_chat_completion(messages, model="gpt-4o-mini", temperature=0.3)
    
    assert res == "formatted markdown"
    mock_create.assert_called_once_with(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3
    )

def test_openai_service_error_handling(mocker):
    """Verifies service raises a RuntimeError when the API call fails."""
    service = OpenAIService(api_key="test-key")
    mocker.patch.object(
        service.client.chat.completions,
        "create",
        side_effect=Exception("Connection timeout")
    )
    
    with pytest.raises(RuntimeError, match="OpenAI API Error: Connection timeout"):
        service.generate_chat_completion([])
