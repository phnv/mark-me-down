# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field
from typing import List, Optional

class NoteProfile(BaseModel):
    # id: str = Field(..., description="Unique identifier for the template")
    name: str = Field(..., description="Name of the template")
    description: str = Field(..., description="A Semantic Description of the template for RAG retrieval")
    instructions: str = Field(..., description="Instructions on how to use the template")
    raw_note_text: str = Field(..., description="Rough user provided note text.")
    # To be deprecated
    # preview: str = Field(..., description="A preview of the template structure")
    
    tags: List[str] = Field(..., description="Tags indicating topics, concepts, usage, etc.")
    purpose: List[str] = Field(..., description="Why the template exists")
    sections: List[str] = Field(..., description="Semantic sections the template contains")
    organization_structure: List[str] = Field(..., description="How information is organized")
    style: List[str] = Field(..., description="How information is written (tone, density, etc.)")

class TemplateProfile(BaseModel):
    id: Optional[str]= Field(..., description="Unique identifier for the template")
    name: Optional[str]= Field(..., description="Name of the template")
    description: Optional[str] = Field(..., description="Description of the template")
    instructions: Optional[str] = Field(None, description="Instructions on how to use the template")
    category: Optional[str] = Field(None, description="Category of the template")
    tags: Optional[List[str]] = Field(None, description="Tags indicating topics, concepts, usage, etc.")
    version: Optional[int] = Field(default=1, description="Version of the template")
    preview_markdown: Optional[str] = Field(..., description="A preview of the template structure")
    template_markdown: Optional[str] = Field(..., description="The template itself in markdown format")
    purpose: Optional[List[str]] = Field(None, description="Why the template exists")
    sections: Optional[List[str]] = Field(None, description="Semantic sections the template contains")
    organization_structure: Optional[List[str]] = Field(None, description="How information is organized")
    style: Optional[List[str]] = Field(None, description="How information is written (tone, density, etc.)")
    embedding_vector: Optional[List[float]] = Field(None, description="Embedding vector for RAG retrieval")
    embedding_text: Optional[str] = Field(None, description="Semantic document for RAG retrieval")