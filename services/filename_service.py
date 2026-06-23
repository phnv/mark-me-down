import re
from utils.markdown_utils import clean_whitespace

def suggest_filename(markdown_text: str) -> str:
    """Suggests a safe, human-readable filename from the markdown content.
    
    Tries to find the first H1 header (# Title), otherwise takes the first few words of text.
    """
    cleaned = clean_whitespace(markdown_text)
    if not cleaned:
        return "untitled-note.md"
    
    # 1. Try to find the first H1 header (e.g., "# My Awesome Title")
    header_match = re.search(r'^#\s+(.+)$', cleaned, re.MULTILINE)
    if header_match:
        title = header_match.group(1).strip()
    else:
        # 2. Fallback: Take the first non-empty line
        non_empty_lines = [line.strip() for line in cleaned.split("\n") if line.strip()]
        if non_empty_lines:
            # Strip common markdown decorators to get clean text
            title = re.sub(r'[*_#`\[\]]', '', non_empty_lines[0])
        else:
            title = "untitled-note"

    # 3. Clean up title: first strip special chars, then limit to first 5 words
    title_clean = re.sub(r'[^a-zA-Z0-9\s_-]', '', title)
    words = title_clean.split()
    if len(words) > 5:
        title_clean = " ".join(words[:5])
    else:
        title_clean = " ".join(words)
        
    # 4. Sanitize to safe filename characters
    sanitized = title_clean.lower()
    sanitized = re.sub(r'\s+', '-', sanitized)

    # Remove duplicate hyphens/underscores
    sanitized = re.sub(r'-+', '-', sanitized)
    sanitized = re.sub(r'_+', '_', sanitized)
    sanitized = sanitized.strip('-_')
    
    if not sanitized:
        return "untitled-note.md"
        
    # Limit character length
    if len(sanitized) > 40:
        sanitized = sanitized[:40].rstrip('-_')
        
    return f"{sanitized}.md"
