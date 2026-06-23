import streamlit as st
import os
from config import REFACTOR_MODES, OUTPUT_STYLES, DEFAULT_MODEL

def render_sidebar_api_key():
    """Renders the OpenAI API key input field in the sidebar and manages its session state."""
    st.sidebar.header("🔑 Authentication")
    
    # Initialize from environment variable if present, else empty
    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = os.environ.get("OPENAI_API_KEY", "")
        
    api_key_input = st.sidebar.text_input(
        "OpenAI API Key",
        value=st.session_state.openai_api_key,
        type="password",
        placeholder="sk-...",
        help="Bring Your Own Key (BYOK). Stored securely only in session state."
    )
    
    # If key changes, update session state and rerun
    if api_key_input != st.session_state.openai_api_key:
        st.session_state.openai_api_key = api_key_input
        st.rerun()
        
    if not st.session_state.openai_api_key:
        st.sidebar.warning("Please enter your OpenAI API key to start.")
        return None
        
    st.sidebar.success("API Key loaded! ✅")
    return st.session_state.openai_api_key


def render_sidebar_options():
    """Renders the refactor mode and output style parameters in the sidebar."""
    st.sidebar.header("⚙ Options")
    
    mode = st.sidebar.selectbox(
        "Refactor Mode",
        options=REFACTOR_MODES,
        index=0,
        format_func=lambda x: x.capitalize(),
        help="Conservative: fix typos only. Interpretative: clarify flow. Aggressive: complete rewrite."
    )
    
    style = st.sidebar.selectbox(
        "Output Style",
        options=OUTPUT_STYLES,
        index=0,
        format_func=lambda x: x.capitalize(),
        help="Target structure for the output markdown."
    )
    
    st.sidebar.divider()
    st.sidebar.caption(f"Running on model: `{DEFAULT_MODEL}`")
    
    return mode, style
