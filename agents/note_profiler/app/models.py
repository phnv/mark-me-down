from pydantic import BaseModel, Field
from typing import List, Optional

class TemplateModelProfile(BaseModel):
    id: str = Field(..., description="Unique identifier for the template")
    name: str = Field(..., description="Name of the template")
    description: str = Field(..., description="Description of the template")
    instructions: str = Field(..., description="Instructions on how to use the template")
    preview: str = Field(..., description="A preview of the template structure")
    tags: List[str] = Field(..., description="Tags indicating topics, concepts, usage, etc.")
    purpose: List[str] = Field(..., description="Why the template exists")
    sections: List[str] = Field(..., description="Semantic sections the template contains")
    organization_structure: List[str] = Field(..., description="How information is organized")
    style: List[str] = Field(..., description="How information is written (tone, density, etc.)")
    embedding_text: Optional[str] = Field(None, description="Semantic document for RAG retrieval")
