"""Utility functions for processing markdown text."""

def clean_whitespace(text: str) -> str:
    """Normalize line endings to Unix style and strip trailing whitespace from each line.
    
    Also strips leading and trailing empty lines from the overall text.
    """
    if not text:
        return ""
    # Normalize line endings
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    # Clean trailing spaces on each line and join
    lines = [line.rstrip() for line in normalized.split("\n")]
    # Strip leading and trailing empty lines from the list
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    
    return "\n".join(lines)


def ensure_ends_with_newline(text: str) -> str:
    """Ensure that the markdown string ends with exactly one newline character."""
    cleaned = text.rstrip()
    if not cleaned:
        return ""
    return cleaned + "\n"
