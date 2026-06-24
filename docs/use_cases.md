# Use Cases

## Primary workflow

1. User copies some text.
2. User opens the application.
3. User pastes text manually.
4. Raw text is displayed.
5. User optionally selects a specific markdown template from the dropdown (loaded from Supabase).
6. User optionally toggles "Include frontmatter" to generate YAML metadata.
7. User previews the selected template's markdown structure in the preview block.
8. User confirms the transformation by clicking "Clean Note".
9. The note (with selected mode, style, and template instructions) is sent to the LLM.
11. The application returns formatted markdown.
12. User edits the markdown manually if desired.
13. User previews the rendered markdown.
14. User copies the result or downloads a markdown file.

## Constraints (overwritten on user request only)

* No chat interface.
* No iterative conversations.
* No regeneration loop.
* No history.
* No memory.

## Output expectations

* Preserve information.
* Improve readability.
* Produce markdown only.
* Avoid inventing facts.
* Adapt structure to the note contents.
