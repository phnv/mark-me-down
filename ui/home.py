import streamlit as st
from models.request_models import RefactorRequest
from services.openai_service import OpenAIService
from services.clipboard_service import copy_to_clipboard
from agents.note_refactor_agent import NoteRefactorAgent
from ui.widgets import render_sidebar_api_key, render_sidebar_options

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

    # 4. Input Section
    st.subheader("1. Enter Your Messy Note")
    
    raw_text = st.text_area(
        "Paste your unformatted notes or rough text below:",
        height=200,
        placeholder="e.g. metting w/ bob at 2pm. discussed roadmap. need to finish widgets by friday. bob will write tests.",
        help="Paste your rough thoughts, transcripts, or unformatted text here."
    )

    # Disable button if key is missing or no text is entered
    submit_disabled = not api_key or not raw_text.strip()
    
    col1, col2 = st.columns([4, 1])
    with col1:
        submit_btn = st.button("Clean Note 🚀", disabled=submit_disabled, use_container_width=True)
    with col2:
        # Simple reset button to clear states
        clear_btn = st.button("Clear 🗑", use_container_width=True)
        if clear_btn:
            st.session_state.refactored_markdown = ""
            st.session_state.user_edited_markdown = ""
            st.session_state.suggested_filename = "untitled-note.md"
            st.session_state.last_processed_raw = ""
            st.rerun()

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
                    output_style=style
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
