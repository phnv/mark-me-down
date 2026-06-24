from pydantic import BaseModel, Field
from config import REFACTOR_CONSERVATIVE, STYLE_ADAPTIVE

class RefactorRequest(BaseModel):
    """Model representing a request to refactor a raw note."""
    raw_text: str = Field(..., description="The raw, messy note content.")
    refactor_mode: str = Field(default=REFACTOR_CONSERVATIVE, description="The level of editing applied (conservative, interpretative, aggressive).")
    output_style: str = Field(default=STYLE_ADAPTIVE, description="The desired presentation style (adaptive, plain, todo, structured).")
    template_instruction: str = Field(default=None, description="Instructions from the selected template.")
    template_description: str = Field(default=None, description="Description from the selected template.")
    include_frontmatter: bool = Field(default=False, description="Whether to include YAML frontmatter in the output.")
