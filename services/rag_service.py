import os
# pyrefly: ignore [missing-import]
from supabase import create_client, Client
from typing import Optional
from google import genai
from google.genai import types
from agents.v2.models import NoteProfile, TemplateMatch

def get_supabase_client() -> Client:
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    if not supabase_url or not supabase_key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables")
    return create_client(supabase_url, supabase_key)

def note_profile_to_embedding_text(profile: NoteProfile) -> str:
    """Serialize a NoteProfile into a deterministic text for embeddings."""
    def yaml_list(items: list[str]) -> str:
        return "\n".join(f"  - {item}" for item in items)

    parts = []
    
    # Dump model to dict
    profile_dict = profile.model_dump()
    
    # Map of output topic header to the profile attribute name
    topics = [
        ('description','description'),
        ('instructions','instructions'),
        ('tags','tags'),
        ('purpose','purpose'),
        ('sections','sections'),
        ('organization_structure','organization_structure'),
        ('style','style')
    ]
    
    for topic_name, attr_name in topics:
        if attr_name in profile_dict:
            val = profile_dict[attr_name]
            if val is not None and val != "" and (not isinstance(val, list) or len(val) > 0):
                formatted_list = yaml_list(val) if isinstance(val, list) else f"  - {val}"
                parts.append(f"{topic_name}:\n{formatted_list}")
                
    return "\n\n".join(parts).strip()

def generate_embedding(text: str, provider: str, api_key: str) -> list[float]:
    """Generates an embedding vector using the selected provider."""
    if provider.lower() == "gemini":
        client = genai.Client(api_key=api_key)
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
            config=types.EmbedContentConfig(
                output_dimensionality=1536
            ),
        )
        return response.embeddings[0].values
    elif provider.lower() == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
    else:
        raise ValueError(f"Unsupported provider: {provider}")

def search_template(embedding_vector: list[float], match_count: int = 1) -> Optional[TemplateMatch]:
    """Searches for a matching template in Supabase using the embedding vector."""
    try:
        supabase = get_supabase_client()
        results = (
            supabase
            .rpc(
                "match_templates",
                {
                    "query_embedding": embedding_vector,
                    "match_count": match_count,
                },
            )
            .execute()
        )
        
        if results.data and len(results.data) > 0:
            best_match = results.data[0]
            return TemplateMatch(
                id=best_match.get("id"),
                name=best_match.get("name"),
                description=best_match.get("description", ""),
                instructions=best_match.get("instructions", ""),
                template_markdown=best_match.get("template_markdown", ""),
                similarity=best_match.get("similarity")
            )
        return None
    except Exception as e:
        print(f"Error in RAG search: {e}")
        return None

def fetch_all_templates() -> list[dict]:
    """Fetches all available templates from Supabase for the UI dropdown."""
    try:
        supabase = get_supabase_client()
        # We only need the id and name for the dropdown
        result = supabase.table('templates').select('id, name, template_markdown, description, instructions, preview_markdown').execute()
        return result.data
    except Exception as e:
        print(f"Error fetching templates: {e}")
        return []
