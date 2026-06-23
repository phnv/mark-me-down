"""Configuration constants for the Mark-me-down application."""

# OpenAI Configuration
DEFAULT_MODEL = "gpt-4o-mini"

# Refactor Modes
REFACTOR_CONSERVATIVE = "conservative"
REFACTOR_INTERPRETATIVE = "interpretative"
REFACTOR_AGGRESSIVE = "aggressive"

REFACTOR_MODES = [
    REFACTOR_CONSERVATIVE,
    REFACTOR_INTERPRETATIVE,
    REFACTOR_AGGRESSIVE,
]

# Output Styles
STYLE_ADAPTIVE = "adaptive"
STYLE_PLAIN = "plain"
STYLE_TODO = "todo"
STYLE_STRUCTURED = "structured"

OUTPUT_STYLES = [
    STYLE_ADAPTIVE,
    STYLE_PLAIN,
    STYLE_TODO,
    STYLE_STRUCTURED,
]
