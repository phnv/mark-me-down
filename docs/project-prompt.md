# Mark-me-down Development Instructions

You are building Mark-me-down, a lightweight Streamlit application that converts messy notes into clean markdown.

Before planning or implementing anything, read all documents inside the `docs/` folder.

Priorities:

1. Keep the project intentionally simple.
2. Prefer maintainability over cleverness.
3. Avoid unnecessary abstractions.
4. Follow the documented architecture.
5. Implement features incrementally.
6. This is not a chat application.
7. There must be no conversation loop or memory.
8. Users perform a single transformation and then manually edit the output if desired.
9. Produce production-quality code with clear module boundaries.
10. Write code that is easy to extend with future features.

Implementation principles:

* Use Streamlit.
* Use the OpenAI API.
* Use BYOK (Bring Your Own Key).
* Store keys only in session state.
* Output markdown only.
* Keep transformations conservative.
* Do not introduce conversational interfaces.
* Prefer explicit code over excessive abstractions.
* Favor composable modules.

Focus on completing the MVP described in the documentation before implementing roadmap features.
