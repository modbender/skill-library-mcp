# Frontmatter & Metadata Reference

Complete reference for SKILL.md YAML frontmatter fields.

## Required fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | `string` | Skill identifier. Must match folder name. Lowercase, hyphens, max 64 chars. |
| `description` | `string` | What the skill does + when to use it. This is the primary trigger mechanism — the agent reads this to decide whether to activate the skill. Always include "Use when..." context. |

## Optional fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `metadata` | `object` | `{}` | Structured metadata for OpenClaw runtime |

## `metadata.openclaw` object

| Key | Type | Description |
|-----|------|-------------|
| `requires` | `object` | Runtime dependency declarations |
| `requires.bins` | `string[]` | Required CLI binaries (e.g., `["jq", "curl"]`). OpenClaw validates these exist at install time. |
| `requires.env` | `string[]` | Required environment variables (e.g., `["DATABASE_URL"]`). Checked at skill activation. |
| `os` | `string[]` | OS restrictions (e.g., `["linux", "darwin"]`). Skill is hidden on unsupported platforms. |

## Examples

### Minimal (no dependencies)

```yaml
---
name: my-skill
description: Do a thing. Use when the user asks to do the thing.
---
```

### With binary dependencies

```yaml
---
name: reminder
description: Set a one-shot reminder. Use when the user asks to be reminded of something at a specific time or after a duration.
metadata: {"openclaw":{"requires":{"bins":["jq"]}}}
---
```

### With environment variables

```yaml
---
name: db-query
description: Query the application database. Use when the user asks for data from the database.
metadata: {"openclaw":{"requires":{"bins":["psql"],"env":["DATABASE_URL"]}}}
---
```

### With OS restrictions

```yaml
---
name: macos-notify
description: Send a macOS notification. Use when the user wants a desktop alert.
metadata: {"openclaw":{"requires":{"bins":["osascript"]},"os":["darwin"]}}
---
```

## Inline JSON format

The `metadata` field uses inline JSON (not nested YAML) for compatibility with the OpenClaw parser:

```yaml
# Correct — inline JSON
metadata: {"openclaw":{"requires":{"bins":["jq"]}}}

# Wrong — nested YAML (not supported)
metadata:
  openclaw:
    requires:
      bins:
        - jq
```

## `{baseDir}` variable

Use `{baseDir}` in the SKILL.md body to reference files within the skill directory. It resolves to the absolute path of the skill folder at runtime.

```markdown
Load `{baseDir}/references/api-docs.md` for the full API reference.
```

```json
{
  "tool": "exec",
  "command": "bash {baseDir}/scripts/run.sh"
}
```
