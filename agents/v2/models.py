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
    # --- Guardrail fields: set internally by pre_profiler_guardrail_callback ---
    # The LLM never sets these; they are only written by the guardrail callback
    # when a pre-flight check blocks the request. Both default to safe values so
    # normal LLM output (which omits them) remains valid.
    blocked: bool = Field(default=False, description="True if a pre-flight guardrail blocked this request. Set by callback, not by LLM.")
    reason: str = Field(default="", description="Human-readable block reason when blocked=True. Empty otherwise.")
    # --- Semantic profiling fields (unchanged) ---
    description: str = Field(default="", description="A Semantic Description of the note for RAG retrieval of template") 
    instructions: str = Field(default="", description="Instructions on how to refactor note") 
    tags: List[str] = Field(default_factory=list, description="Semantic concepts and information types present in the note indicating topics, concepts, usage, etc.")
    purpose: List[str] = Field(default_factory=list, description="Why the note exists") 
    sections: List[str] = Field(default_factory=list, description="Semantic sections the note must contain") 
    organization_structure: List[str] = Field(default_factory=list, description="How information is organized")
    style: List[str] = Field(default_factory=list, description="How information is to be rewritten (tone, density, etc.)")

class TemplateMatch(BaseModel):
    """A matched template from the Supabase RAG search."""
    id: str
    name: str
    description: str
    instructions: str
    template_markdown: str
    similarity: Optional[float] = None
