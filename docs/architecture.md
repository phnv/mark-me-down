# Architecture

## Stack

* Streamlit
* OpenAI API
* Supabase (Template storage and retrieval via st_supabase_connection)
* BYOK authentication


## Agent responsibilities

The note refactor agent performs one task:

raw note
↓
Pre-Workflow Guardrails (length limit & prompt injection detection)
↓
understand meaning
↓
organize ideas
↓
rewrite conservatively
↓
generate markdown
↓
Post-Workflow Guardrails (HTML, leaked prompts, policy validation)

The agent does not maintain memory or history.

## PromptBuilder responsibilities

PromptBuilder constructs instructions based on:

* rewrite mode
* output style
* template instructions and descriptions (dynamically fetched from Supabase)
* frontmatter requirement (if toggled)

PromptBuilder returns a prompt string.

The agent coordinates execution and calls the OpenAI service.

Prompt behavior should remain independent from orchestration code.

## UI

Input area:

* manual paste

Options (Sidebar):

Refactor mode:

* conservative
* interpretative
* aggressive

Output style:

* adaptive
* plain
* todo
* structured

Template Selection:

* Dropdown menu populated from Supabase `templates` table
* Frontmatter inclusion toggle (Yes/No)

Main View:
* Text input
* Real-time template markdown preview using `streamlit_markdown` component
* Clean Note button

Output section:

Tab 1:

Editable markdown text.

Tab 2:

Rendered markdown preview.

Actions:

* copy to clipboard
* download markdown file

---
## Folder Structure Instructions for Agents

Separate **development-time agent assets** from **runtime/production agent assets**. Treat them as two independent ecosystems.

## Basic App Directory structure

mark-me-down/

app.py

config.py

ui/
home.py
widgets.py

agents/
note_refactor_agent.py
prompt_builder.py

services/
openai_service.py
clipboard_service.py
filename_service.py

models/
request_models.py
response_models.py

utils/
markdown_utils.py

tests/

### Principles

* Development instructions and skills exist only to help coding agents build and maintain the repository.
* Production instructions, skills, examples, and resources are part of the application itself and are consumed by runtime agents.
* Never mix development and production assets.
* Prefer self-contained agents and reusable skills.
* Keep local instructions close to the code they describe.

---

### Development Agent Structure

Repository-level instructions:

```text
AGENTS.md
```

Contains:

* project philosophy
* architecture overview
* coding standards
* stack decisions
* things to avoid
* testing requirements

Shared development skills:

```text
.skills/
```

Examples:

```text
.skills/
├── streamlit/
├── fastapi/
├── supabase/
├── prompt-engineering/
├── rag/
└── testing/
```

These answer:

> "How do we do X in this repository?"

Feature-local instructions may live beside the code:

```text
src/api/AGENTS.md
src/workers/AGENTS.md
src/frontend/AGENTS.md
```

These answer:

> "How does this part of the system work?"

---

### Runtime / Production Agent Structure

Runtime agents belong to the application and should be separated from development assets.

```text
agents/
```

Example:

```text
agents/
├── selector/
│   ├── system.md
│   ├── config.yaml
│   ├── skills/
│   ├── resources/
│   └── examples/
│
├── rag/
│   ├── system.md
│   ├── skills/
│   └── resources/
│
└── formatter/
    ├── system.md
    ├── skills/
    ├── resources/
    └── examples/
```

Each runtime agent should be self-contained.

---

### Shared Runtime Skills

Reusable capabilities should live in a top-level `skills/` directory:

```text
skills/
├── markdown-formatting/
│   ├── skill.md
│   ├── examples/
│   ├── resources/
│   └── scripts/
│
├── heading-normalization/
├── summarization/
└── table-generation/
```

Skills are first-class packages and may contain:

* instructions (`skill.md`)
* examples
* resources
* scripts
* templates

Agents declare which skills they use:

```yaml
name: markdown_agent

skills:
  - markdown-formatting
  - heading-normalization
  - summarization
```

---

### Recommended Repository Layout

```text
repo/
│
├── AGENTS.md                # global development instructions
├── .skills/                 # development-time skills
│
├── src/
├── tests/
├── docs/
│
├── agents/                  # runtime agents
│
├── skills/                  # runtime skills
│
├── resources/
├── prompts/
├── examples/
└── scripts/
```

---

### Mental Model

```text
Human
↓
Coding Agent
↓
Repository
↓
Production Agent
↓
End User
```

Development assets (`AGENTS.md`, `.skills/`) exist to help build the system.

Runtime assets (`agents/`, `skills/`, `resources/`, `examples/`, `scripts/`) are shipped with and consumed by the system.

Maintain a strict separation between these layers to preserve clarity and scalability.
