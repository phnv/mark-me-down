from services.filename_service import suggest_filename

def test_suggest_filename_with_h1():
    markdown = "# Project Planning Note\nSome content here."
    filename = suggest_filename(markdown)
    assert filename == "project-planning-note.md"

def test_suggest_filename_fallback_first_line():
    markdown = "Grocery list:\n- Milk\n- Eggs"
    filename = suggest_filename(markdown)
    assert filename == "grocery-list.md"

def test_suggest_filename_empty():
    assert suggest_filename("") == "untitled-note.md"
    assert suggest_filename("   \n   ") == "untitled-note.md"

def test_suggest_filename_sanitization():
    markdown = "# Complex !@# Title (with brackets) & stuff!"
    filename = suggest_filename(markdown)
    assert filename == "complex-title-with-brackets-stuff.md"

def test_suggest_filename_long_title():
    markdown = "# This is a very long title that should be truncated to prevent filenames from being too long"
    filename = suggest_filename(markdown)
    # The first 5 words are "This is a very long"
    assert filename == "this-is-a-very-long.md"
