import streamlit as st
import streamlit.components.v1 as components
import json

def copy_to_clipboard(text: str, label: str = "📋 Copy Markdown"):
    """Renders a custom HTML/JS button to copy text directly to the user's browser clipboard.
    
    This works reliably across browsers and triggers visual feedback when clicked.
    """
    # Escape the text to safely inject it into JavaScript string literal
    escaped_text = json.dumps(text)
    
    html_code = f"""
    <button id="copy-btn" style="
        background-color: #6366F1;
        color: #F8FAFC;
        border: none;
        padding: 10px 18px;
        border-radius: 6px;
        cursor: pointer;
        font-weight: 600;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-size: 14px;
        transition: all 0.2s ease-in-out;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    ">
        {label}
    </button>
    <script>
    document.getElementById('copy-btn').addEventListener('click', () => {{
        const text = {escaped_text};
        navigator.clipboard.writeText(text).then(() => {{
            const btn = document.getElementById('copy-btn');
            btn.style.backgroundColor = '#10B981';
            btn.innerHTML = '✔ Copied!';
            setTimeout(() => {{
                btn.style.backgroundColor = '#6366F1';
                btn.innerHTML = '{label}';
            }}, 2000);
        }}).catch(err => {{
            console.error('Failed to copy text: ', err);
            alert('Clipboard copy failed. Please select the text and copy manually.');
        }});
    }});
    </script>
    """
    components.html(html_code, height=50)

