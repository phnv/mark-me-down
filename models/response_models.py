from pydantic import BaseModel, Field

class RefactorResponse(BaseModel):
    """Model representing the refactored output and suggested metadata."""
    formatted_markdown: str = Field(..., description="The cleaned, rewritten markdown output.")
    suggested_filename: str = Field(..., description="A safe suggested file name for downloading the note.")
