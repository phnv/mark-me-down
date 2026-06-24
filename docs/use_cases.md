# Use Cases

## Primary workflow

1. User copies some text.
2. User opens the application.
3. The application attempts to read the clipboard.
4. If clipboard access fails, the user pastes text manually.
5. Raw text is displayed.
6. User optionally selects a specific markdown template from the dropdown (loaded from Supabase).
7. User optionally toggles "Include frontmatter" to generate YAML metadata.
8. User previews the selected template's markdown structure in the preview block.
9. User confirms the transformation by clicking "Clean Note".
10. The note (with selected mode, style, and template instructions) is sent to the LLM.
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
