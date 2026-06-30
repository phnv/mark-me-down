# pyrefly: ignore [missing-import]
import streamlit as st
import os
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from streamlit_markdown import st_markdown
from agents.v2.runner import run_workflow_sync
from services.clipboard_service import copy_to_clipboard
from services.filename_service import suggest_filename
from ui.widgets import render_sidebar_api_key, render_sidebar_options, get_templates

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

    # 1. Initialize state variables
    if "refactored_markdown" not in st.session_state:
        st.session_state.refactored_markdown = ""
    if "suggested_filename" not in st.session_state:
        st.session_state.suggested_filename = "untitled-note.md"
    if "markdown_edit_area" not in st.session_state:
        st.session_state.markdown_edit_area = ""
    if "last_processed_raw" not in st.session_state:
        st.session_state.last_processed_raw = ""
    if "raw_text_input" not in st.session_state:
        st.session_state.raw_text_input = ""
        
    # init sidebar options in session state
    if "refactor_mode" not in st.session_state:
        st.session_state.refactor_mode = "conservative"
    if "rewrite_style" not in st.session_state:
        st.session_state.rewrite_style = "adaptive"
    if "template_id" not in st.session_state:
        st.session_state.template_id = "auto"
    if "include_frontmatter" not in st.session_state:
        st.session_state.include_frontmatter = False

    # 2. Load Templates
    if "templates" not in st.session_state:
        st.session_state.templates = get_templates()

    # 3. Sidebar Integration (BYOK and parameters)
    provider, api_key = render_sidebar_api_key()
    render_sidebar_options()

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
            st.session_state.markdown_edit_area = ""
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
    
    st.subheader("2. Selected Template Preview")
    if st.session_state.template_id == "auto":
        st.info("Auto mode: The AI will select the best template for your note automatically.")
    else:
        selected_template = next((t for t in st.session_state.templates if str(t.get("id")) == str(st.session_state.template_id)), None)
        if selected_template and selected_template.get("preview_markdown"):
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
            with st.spinner("Processing note through ADK Workflow..."):
                request_dict = {
                    "raw_text": raw_text,
                    "refactor_mode": st.session_state.refactor_mode,
                    "rewrite_mode": st.session_state.rewrite_style,
                    "template_selection": st.session_state.template_id,
                    "include_frontmatter": st.session_state.include_frontmatter
                }

                print("request_dict:")
                print(request_dict)
                
                final_output, similarity_score, template_match = run_workflow_sync(
                    request_dict, provider, api_key
                )

                # --- Guardrail block detection ---------------------------------
                # runner returns (None, "GUARDRAIL", reason_string) when a
                # callback blocks the request. Surface this as a warning banner
                # and suppress the output section entirely.
                if similarity_score == "GUARDRAIL":
                    reason = template_match  # reason_string is in the third slot
                    st.warning(f"⚠️ Request blocked by safety guardrail: {reason}")
                    # Clear any stale output from a previous successful run
                    st.session_state.refactored_markdown = ""
                    st.session_state.markdown_edit_area = ""
                    st.session_state.suggested_filename = "untitled-note.md"
                    st.session_state.selected_template_name = None
                else:
                    # --- Normal success path ----------------------------------
                    suggested_filename = suggest_filename(final_output)
                    
                    st.session_state.refactored_markdown = final_output
                    # FIX: when st.text_area has key="markdown_edit_area", Streamlit
                    # reads the widget value from session_state["markdown_edit_area"],
                    # ignoring the value= arg after first render. We must set the key
                    # directly so the new output appears in the edit box.
                    st.session_state.markdown_edit_area = final_output
                    st.session_state.suggested_filename = suggested_filename
                    st.session_state.last_processed_raw = raw_text
                    st.session_state.similarity_score = similarity_score
                    
                    if template_match:
                        t_name = template_match.name if hasattr(template_match, 'name') else template_match.get("name")
                        st.session_state.selected_template_name = t_name
                    else:
                        st.session_state.selected_template_name = None
                
        except Exception as e:
            st.error(f"Error refactoring note: {str(e)}")

    # 6. Output Section (Display only if there is a result)
    if st.session_state.refactored_markdown:
        st.divider()
        st.subheader("2. Refactored Markdown")
        
        # Display template similarity if auto was used
        if st.session_state.get("selected_template_name"):
            score = st.session_state.get("similarity_score")
            score_text = f" (Similarity: {score:.3f})" if score is not None else ""
            st.info(f"**Template Used:** {st.session_state.selected_template_name}{score_text}")
        
        tab_edit, tab_preview = st.tabs(["✏ Edit Markdown", "👁 Preview"])
        
        with tab_edit:
            # Let users edit the raw markdown output manually
            edited_text = st.text_area(
                "Modify the markdown output if needed:",
                height=300,
                key="markdown_edit_area"  # Streamlit owns the value via this key
            )
            
        with tab_preview:
            # Rendered HTML markdown preview — read directly from the widget key
            display_text = st.session_state.get("markdown_edit_area", "")
            if display_text:
                st.markdown(display_text)
            else:
                st.info("Write or generate markdown to see preview.")
                
        # Action Buttons
        st.write("")
        act_col1, act_col2 = st.columns([1, 1])
        with act_col1:
            # Custom HTML/JS clipboard copy button
            copy_to_clipboard(st.session_state.get("markdown_edit_area", ""), label="📋 Copy to Clipboard")
        with act_col2:
            # Native download button for file saving
            st.download_button(
                label="📥 Download Markdown File",
                data=st.session_state.get("markdown_edit_area", ""),
                file_name=st.session_state.suggested_filename,
                mime="text/markdown",
                use_container_width=True
            )
            st.caption(f"Suggested filename: `{st.session_state.suggested_filename}`")
