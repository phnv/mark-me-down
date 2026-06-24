import streamlit as st
import os
from dotenv import load_dotenv
from st_supabase_connection import SupabaseConnection, execute_query
from streamlit_markdown import st_markdown

from models.request_models import RefactorRequest
from services.openai_service import OpenAIService
from services.clipboard_service import copy_to_clipboard
from agents.note_refactor_agent import NoteRefactorAgent
from ui.widgets import render_sidebar_api_key, render_sidebar_options

# Load environment variables
load_dotenv()

def render_home_page():
    """Renders the main content area of the Mark-me-down application."""
    
    # 1. Custom CSS injection for premium visuals
    st.markdown("""
    <style>
    /* Styling adjustments for Title & main layouts */
    .title-container {
        padding-bottom: 1.5rem;
    }
    h1 {
        font-weight: 800 !important;
        background: linear-gradient(90deg, #818CF8 0%, #6366F1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    h2, h3 {
        font-weight: 600 !important;
        color: #E2E8F0 !important;
    }
    
    /* Clean, professional styling for text areas */
    textarea {
        font-family: 'Courier New', Courier, monospace !important;
    }
    
    /* Enhance Streamlit buttons */
    div.stButton > button {
        background-color: #6366F1 !important;
        color: #F8FAFC !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.2s ease-in-out !important;
    }
    div.stButton > button:hover {
        background-color: #4F46E5 !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Title Banner
    st.markdown('<div class="title-container"><h1>📝 Mark-me-down</h1></div>', unsafe_allow_html=True)
    st.markdown("Transform messy, unformatted, or raw notes into clean, well-formatted markdown.")
    st.divider()

    # 2. Sidebar Integration (BYOK and parameters)
    api_key = render_sidebar_api_key()
    mode, style = render_sidebar_options()

    # 3. Initialize state variables
    if "refactored_markdown" not in st.session_state:
        st.session_state.refactored_markdown = ""
    if "suggested_filename" not in st.session_state:
        st.session_state.suggested_filename = "untitled-note.md"
    if "user_edited_markdown" not in st.session_state:
        st.session_state.user_edited_markdown = ""
    if "last_processed_raw" not in st.session_state:
        st.session_state.last_processed_raw = ""
    if "raw_text_input" not in st.session_state:
        st.session_state.raw_text_input = ""

    # Fetch templates from Supabase
    templates = []
    try:
        # Initialize connection. Provide kwargs explicitly as fallback if secrets.toml isn't used.     
        conn = st.connection(
            "supabase", 
            type=SupabaseConnection, 
            url=os.environ.get("SUPABASE_URL"), 
            key=os.environ.get("SUPABASE_KEY")
        )
        rows = execute_query(conn.table("templates").select("*"),
            ttl="10m"
        )
        templates = rows.data

    except Exception as e:
        st.warning(f"Could not load templates: {e}")

    # 4. Input Section
    col_header1, col_header2 = st.columns([4, 1])
    with col_header1:
        st.subheader("1. Enter Your Messy Note")
    with col_header2:
        # Simple reset button to clear states
        clear_btn = st.button("Clear 🗑", use_container_width=True)
        if clear_btn:
            st.session_state.raw_text_input = ""
            st.session_state.refactored_markdown = ""
            st.session_state.user_edited_markdown = ""
            st.session_state.suggested_filename = "untitled-note.md"
            st.session_state.last_processed_raw = ""
            st.rerun()
    
    raw_text = st.text_area(
        "Paste your unformatted notes or rough text below:",
        height=200,
        placeholder="e.g. metting w/ bob at 2pm. discussed roadmap. need to finish widgets by friday. bob will write tests.",
        help="Paste your rough thoughts, transcripts, or unformatted text here.",
        key="raw_text_input"
    )

    # Disable button if key is missing or no text is entered
    submit_disabled = not api_key or not raw_text.strip()
    
    # Template Selection UI (placed in sidebar)
    with st.sidebar:
        st.header("📄 Template Options")
        template_options = [{"id": "none", "name": "No template"}] + templates
        selected_template_idx = st.selectbox(
            "Select Template",
            range(len(template_options)),
            format_func=lambda i: template_options[i]["name"]
        )
        include_fm = st.radio("Include frontmatter", options=["Yes", "No"], index=1, horizontal=True)
        include_frontmatter = (include_fm == "Yes")
        selected_template = template_options[selected_template_idx]
        
    st.subheader("2. Selected Template Preview")
    if selected_template["id"] != "none" and selected_template.get("preview_markdown"):
        st.markdown(f"**{selected_template['name']}**")
        st.caption(selected_template.get('description', ''))
        with st.container(border=True):
            st_markdown(selected_template["preview_markdown"])
    else:
        st.info("No template selected.")
            
    st.write("") # Spacer

    submit_btn = st.button("Clean Note 🚀", disabled=submit_disabled, use_container_width=True)

    # 5. Core Refactor Execution
    if submit_btn and not submit_disabled:
        try:
            with st.spinner("Processing note through AI..."):
                # Instantiate dependencies
                openai_service = OpenAIService(api_key=api_key)
                agent = NoteRefactorAgent(openai_service=openai_service)
                
                request_model = RefactorRequest(
                    raw_text=raw_text,
                    refactor_mode=mode,
                    output_style=style,
                    template_instruction=selected_template.get("instructions") if selected_template["id"] != "none" else None,
                    template_description=selected_template.get("description") if selected_template["id"] != "none" else None,
                    include_frontmatter=include_frontmatter
                )
                
                response = agent.refactor(request_model)
                
                # Save outputs in session state
                st.session_state.refactored_markdown = response.formatted_markdown
                st.session_state.user_edited_markdown = response.formatted_markdown
                st.session_state.suggested_filename = response.suggested_filename
                st.session_state.last_processed_raw = raw_text
                
        except Exception as e:
            st.error(f"Error refactoring note: {str(e)}")

    # 6. Output Section (Display only if there is a result)
    if st.session_state.refactored_markdown:
        st.divider()
        st.subheader("2. Refactored Markdown")
        
        tab_edit, tab_preview = st.tabs(["✏ Edit Markdown", "👁 Preview"])
        
        with tab_edit:
            # Let users edit the raw markdown output manually
            edited_text = st.text_area(
                "Modify the markdown output if needed:",
                value=st.session_state.user_edited_markdown,
                height=300,
                key="markdown_edit_area"
            )
            st.session_state.user_edited_markdown = edited_text
            
        with tab_preview:
            # Rendered HTML markdown preview
            if st.session_state.user_edited_markdown:
                st.markdown(st.session_state.user_edited_markdown)
            else:
                st.info("Write or generate markdown to see preview.")
                
        # Action Buttons
        st.write("")
        act_col1, act_col2 = st.columns([1, 1])
        with act_col1:
            # Custom HTML/JS clipboard copy button
            copy_to_clipboard(st.session_state.user_edited_markdown, label="📋 Copy to Clipboard")
        with act_col2:
            # Native download button for file saving
            st.download_button(
                label="📥 Download Markdown File",
                data=st.session_state.user_edited_markdown,
                file_name=st.session_state.suggested_filename,
                mime="text/markdown",
                use_container_width=True
            )
            st.caption(f"Suggested filename: `{st.session_state.suggested_filename}`")
