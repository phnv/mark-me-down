# pyrefly: ignore [missing-import]
import streamlit as st
import os
from config import REFACTOR_MODES, STYLE_MODES, DEFAULT_MODEL

def RENAMED_render_sidebar_api_key():
    """Renders the Provider and API key input field in the sidebar and manages its session state."""
    st.sidebar.header("🔑 Authentication")
    
    # Initialize from environment variable if present
    if "api_provider" not in st.session_state:
        st.session_state.api_provider = "Gemini"
        
    if "api_key" not in st.session_state:
        st.session_state.api_key = os.environ.get("GEMINI_API_KEY", "")
        
    provider = st.sidebar.radio("Provider", options=["Gemini", "OpenAI"], index=0 if st.session_state.api_provider == "Gemini" else 1)
    
    if provider != st.session_state.api_provider:
        st.session_state.api_provider = provider
        st.session_state.api_key = os.environ.get(f"{provider.upper()}_API_KEY", "")
        st.rerun()

    api_key_input = st.sidebar.text_input(
        f"{provider} API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="Enter your key...",
        help="Bring Your Own Key (BYOK). Stored securely only in session state."
    )
    
    # If key changes, update session state and rerun
    if api_key_input != st.session_state.api_key:
        st.session_state.api_key = api_key_input
        st.rerun()
        
    if not st.session_state.api_key:
        st.sidebar.warning(f"Please enter your {provider} API key to start.")
        return None, None
        
    st.sidebar.success(f"{provider} API Key loaded! ✅")
    return st.session_state.api_provider, st.session_state.api_key

# Fetch templates from Supabase
@st.cache_data(ttl=600)
def get_templates():
    try:
        from services.rag_service import fetch_all_templates
        return fetch_all_templates()
    except Exception:
        return []

def render_sidebar_options():
    """Renders the refactor mode, output style, and template selection in the sidebar."""
    st.sidebar.header("⚙ Options")
    
    # helper for index
    def get_index(options, current_value):
        try:
            return options.index(current_value)
        except ValueError:
            return 0
            
    mode = st.sidebar.selectbox(
        "Refactor Mode",
        options=REFACTOR_MODES,
        index=get_index(REFACTOR_MODES, st.session_state.refactor_mode),
        format_func=lambda x: x.capitalize(),
        help="Conservative: fix typos only. Interpretative: clarify flow. Aggressive: complete rewrite."
    )
    if mode != st.session_state.refactor_mode:
        st.session_state.refactor_mode = mode
        # st.rerun()
    
    style = st.sidebar.selectbox(
        "Rewriting Style",
        options=STYLE_MODES,
        index=get_index(STYLE_MODES, st.session_state.rewrite_style),
        format_func=lambda x: x.capitalize(),
        help="Target rewriting style for the output markdown."
    )
    if style != st.session_state.rewrite_style:
        st.session_state.rewrite_style = style
        # st.rerun()
    
    st.sidebar.divider()

    templates = st.session_state.get("templates", [])
    
    template_options = [("auto", "Auto (Let RAG decide)")]
    for t in templates:
        template_options.append((str(t["id"]), t["name"]))
        
    template_id_str = str(st.session_state.template_id) if st.session_state.template_id else "auto"
    try:
        t_index = [t[0] for t in template_options].index(template_id_str)
    except ValueError:
        t_index = 0
        
    template_id = st.sidebar.selectbox(
        "Template Selection",
        options=[t[0] for t in template_options],
        format_func=lambda x: next((name for id, name in template_options if id == x), x),
        index=t_index,
        help="Select 'Auto' to let the AI find the best template for your note, or pick one manually."
    )
    if str(template_id) != template_id_str:
        st.session_state.template_id = template_id
        # st.rerun()
    
    frontmatter = st.sidebar.checkbox("Include Frontmatter", value=st.session_state.include_frontmatter)
    if frontmatter != st.session_state.include_frontmatter:
        st.session_state.include_frontmatter = frontmatter
        # st.rerun()
    
    st.sidebar.divider()
    st.sidebar.caption("Running on ADK V2 Workflow")
