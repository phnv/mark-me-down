import os
from openai import OpenAI

class OpenAIService:
    """Service to handle interactions with the OpenAI API."""

    def __init__(self, api_key: str = None):
        """Initializes the OpenAI service with the provided API key or environment fallback."""
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required.")
        self.client = OpenAI(api_key=self.api_key)

    def generate_chat_completion(self, messages: list, model: str = "gpt-4o-mini", temperature: float = 0.3) -> str:
        """Call the OpenAI Chat Completions API with given messages and parameters."""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )
            content = response.choices[0].message.content
            return content if content else ""
        except Exception as e:
            # Re-raise with a clear user-friendly error message
            raise RuntimeError(f"OpenAI API Error: {str(e)}")
