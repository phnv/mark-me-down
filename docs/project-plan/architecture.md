# Architecture

## Stack

* Streamlit
* OpenAI API
* BYOK authentication

## Directory structure

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

## Agent responsibilities

The note refactor agent performs one task:

raw note
↓
understand meaning
↓
organize ideas
↓
rewrite conservatively
↓
generate markdown

The agent does not maintain memory or history.

## PromptBuilder responsibilities

PromptBuilder constructs instructions based on:

* rewrite mode
* output style
* templates

PromptBuilder returns a prompt string.

The agent coordinates execution and calls the OpenAI service.

Prompt behavior should remain independent from orchestration code.

## UI

Input area:

* attempt clipboard read
* fallback to manual paste

Options:

Refactor mode:

* conservative
* interpretative
* aggressive

Output style:

* adaptive
* plain
* todo
* structured

Output section:

Tab 1:

Editable markdown text.

Tab 2:

Rendered markdown preview.

Actions:

* copy to clipboard
* download markdown file
