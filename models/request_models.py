from pydantic import BaseModel, Field, Optional
from config import REFACTOR_CONSERVATIVE, STYLE_ADAPTIVE

class RefactorRequest(BaseModel):
    """Model representing a request to refactor a raw note."""
    raw_text: str = Field(..., description="The raw, messy note content.")
    refactor_mode: Optional[str] = Field(default=REFACTOR_CONSERVATIVE, description="The level of editing applied (conservative, interpretative, aggressive).")
    output_style: Optional[str] = Field(default=STYLE_ADAPTIVE, description="The desired presentation style (adaptive, plain, todo, structured).")
    template_instruction: Optional[str] = Field(default=None, description="Instructions from the selected template.")
    template_description: Optional[str] = Field(default=None, description="Description from the selected template.")
    include_frontmatter: Optional[bool] = Field(default=False, description="Whether to include YAML frontmatter in the output.")
