# Use Cases

## Primary workflow

1. User copies some text.
2. User opens the application.
3. The application attempts to read the clipboard.
4. If clipboard access fails, the user pastes text manually.
5. Raw text is displayed.
6. User confirms the transformation.
7. The note is sent to the LLM.
8. The application returns markdown.
9. User edits the markdown manually if desired.
10. User previews the rendered markdown.
11. User copies the result or downloads a markdown file.

## Constraints

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
