import streamlit as st
from ui.home import render_home_page

# Page Configuration
st.set_page_config(
    page_title="Mark-me-down - Clean Markdown Notes",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="expanded"
)

if __name__ == "__main__":
    render_home_page()
