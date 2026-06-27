from pydantic import BaseModel, Field
from typing import List, Optional

class UserRefactorRequest(BaseModel):
    """Model representing a request to refactor a raw note."""
    raw_text: str = Field(..., description="The raw, messy note content. May contain user provided instructions, check on that and extract user instructions.")
    refactor_mode: str = Field(..., description="The level of editing applied (conservative, interpretative, aggressive).")
    rewrite_mode: str = Field(..., description="The desired re writing style (adaptive, plain, todo, structured).")
    include_frontmatter: bool = Field(default=False, description="Whether to include YAML frontmatter in the output.")
    template_selection: str = Field(default="auto", description="The ID of the template to use, or 'auto' for RAG search.")

class NoteProfile(BaseModel):
    """Semantic representation of the note, output by NoteProfiler."""
    description: str = Field(..., description="A Semantic Description of the note for RAG retrieval of template") 
    instructions: str = Field(..., description="Instructions on how to refactor note") 
    tags: List[str] = Field(..., description="Semantic concepts and information types present in the note indicating topics, concepts, usage, etc.")
    purpose: List[str] = Field(..., description="Why the note exists") 
    sections: List[str] = Field(..., description="Semantic sections the note must contain") 
    organization_structure: List[str] = Field(..., description="How information is organized")
    style: List[str] = Field(..., description="How information is to be rewritten (tone, density, etc.)")

class TemplateMatch(BaseModel):
    """A matched template from the Supabase RAG search."""
    id: str
    name: str
    description: str
    instructions: str
    template_markdown: str
    similarity: Optional[float] = None
