# NoteProfiler Instructions

## Overview

The **NoteProfiler** is the first agent in the runtime pipeline.

Rather than rewriting notes directly, it analyzes the user's raw note and produces a structured semantic representation (`NoteProfile`) that describes the note using the same ontology as the Template Profiles stored in the vector database.

This semantic abstraction allows Retrieval-Augmented Generation (RAG) to compare notes and templates based on meaning rather than wording, significantly improving template selection.

The agent is intentionally independent of markdown generation and template selection. Its sole responsibility is to understand the user's intent and express it in a consistent semantic vocabulary.

---

# New Data Models

## UserRefactorRequest

Represents the user's original request.

Contains:

* raw note
* refactor mode
* writing style
* frontmatter option

↓

## NoteProfile

Semantic representation of the note.

Contains:

* description
* instructions
* tags
* purpose
* sections
* organization structure
* writing style

The profile is optimized for embedding generation and semantic retrieval rather than human readability.

---

# Agent Flow

```text
                 User
                  │
                  ▼
      UserRefactorRequest
                  │
                  ▼
         NoteProfiler Agent
                  │
      ┌───────────┴────────────┐
      │                        │
Extract Instructions     Infer Semantics
      │                        │
      └───────────┬────────────┘
                  ▼
          Build NoteProfile
                  │
                  ▼
            Embedding Model
                  │
                  ▼
      Vector Search (Templates)
                  │
                  ▼
         Top-K Candidate Templates
                  │
                  ▼
         Selected Template
                  │
                  ▼
          NoteRefactorAgent (v2)
                  │
                  ▼
         Markdown Output
```

---

# Conceptual Architecture

```text
Raw User Note
      │
      ▼
+----------------------+
|   NoteProfiler       |
+----------------------+
      │
      │  Semantic abstraction
      ▼
+----------------------+
|     NoteProfile      |
+----------------------+
      │
      │ Embedding
      ▼
+----------------------+
|   Template RAG       |
+----------------------+
      │
      ▼
Candidate Templates
      │
      ▼
 Selected Template
      │
      ▼
+ original UserRequest (style_mode, refactor_mode, raw_note... ) 
      │
      ▼
+----------------------+
|NoteRefactorAgent (v2)|
+----------------------+
      │
      ▼
Markdown
```

---

# Design Principle

The NoteProfiler creates a semantic boundary between **user language** and **template language**.

Instead of embedding noisy, highly variable user notes, the system embeds a normalized semantic representation. Both Note Profiles and Template Profiles are expressed using the same ontology (purpose, tags, organization, style, sections, etc.), allowing vector similarity to compare concepts rather than literal wording.

This shared semantic language is the foundation of the project's RAG strategy and enables accurate template retrieval even from short, fragmented, or highly informal notes.


'''
python

# Input Model
class UserRefactorRequest(BaseModel):
    """Model representing a request to refactor a raw note."""
    raw_text: str = Field(..., description="The raw, messy note content. May contain user provided instructions, check on that and extract user instructions.")
    refactor_mode: Optional[str] = Field(default=REFACTOR_CONSERVATIVE, description="The level of editing applied (conservative, interpretative, aggressive).")
    rewrite_mode: Optional[str] = Field(default=STYLE_ADAPTIVE, description="The desired re writing style (adaptive, plain, todo, structured).")
    include_frontmatter: bool = Field(default=False, description="Whether to include YAML frontmatter in the output.")


# Output Model

class NoteProfile(BaseModel):
    description: str = Field(..., description="A Semantic Description of the note for RAG retrieval of template") 
    instructions: str = Field(..., description="Instructions on how to refactor note") 
    tags: List[str] = Field(..., description="Semantic concepts and information types present in the note indicating topics, concepts, usage, etc.")
    purpose: List[str] = Field(..., description="Why the note exists") 
    sections: List[str] = Field(..., description="Semantic sections the note must contain") 
    organization_structure: List[str] = Field(..., description="How information is organized")
    style: List[str] = Field(..., description="How information is to be rewritten (tone, density, etc.)")
'''