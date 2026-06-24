# Supabase Database Structure

## Table `templates`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `id` | `text` | Primary |
| `name` | `text` |  |
| `description` | `text` |  |
| `instructions` | `text` |  Nullable |
| `category` | `text` |  Nullable |
| `difficulty` | `text` |  Nullable |
| `tags` | `_jsonb` |  Nullable |
| `version` | `int4` |  |
| `preview_markdown` | `text` |  |
| `template_markdown` | `text` |  |

## Table `examples`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `id` | `int4` | Primary Identity |
| `template_id` | `text` |  |
| `name` | `text` |  |
| `description` | `text` |  Nullable |
| `markdown` | `text` |  Nullable |
| `yaml` | `text` |  Nullable |

## Application Integration

- **Templates Table (`templates`)**: 
  - Queried at application startup using `st_supabase_connection` (cached with 10m TTL).
  - Drives the "Select Template" dropdown menu in the UI.
  - The `instructions` and `description` columns are dynamically injected into the `PromptBuilder` to guide the LLM's output.
  - The `preview_markdown` column is rendered interactively in the UI to give users a live preview of the selected format before execution.
