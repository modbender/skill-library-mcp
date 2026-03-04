# Template Customization Guide

Templates define the schema for every primitive. Customize them to match your workflow.

## How Templates Work

ClawVault loads templates in priority order:
1. **Vault templates** (`your-vault/templates/*.md`) — highest priority
2. **Builtin templates** (shipped with ClawVault) — fallback

To customize, copy a builtin template to your vault's `templates/` directory and edit it.

## Template Schema Format

```yaml
---
primitive: task
description: What this template creates.
fields:
  field_name:
    type: string          # string, number, boolean, date, datetime, string[], array
    required: true         # must be present on every document
    default: "value"       # applied when field not explicitly set
    enum: [a, b, c]       # allowed values (advisory)
    description: "..."     # human-readable explanation
---

# {{title}}

{{content}}
```

## Adding Custom Fields

Add a field to the `fields:` block in the template YAML:

```yaml
fields:
  sprint:
    type: string
    description: Sprint identifier (e.g., S24-03)
  effort:
    type: string
    default: "1h"
    description: Estimated effort (1h, 2d, 1w)
  client:
    type: string
    description: Client this task is for
```

After adding fields:
- `clawvault task add` generates files with the new fields
- Obsidian Bases views automatically pick up new columns
- Existing tasks still work (missing fields are simply absent)

## Changing Defaults

Override defaults to match your team's conventions:

```yaml
fields:
  priority:
    type: string
    default: high           # changed from no default
    enum: [critical, high, medium, low]
  status:
    type: string
    required: true
    default: backlog        # changed from "open"
    enum: [backlog, open, in-progress, blocked, done]
```

## Restricting Values

Use `enum` to limit what values are accepted:

```yaml
fields:
  category:
    type: string
    enum: [bug, feature, chore, spike]
    description: Task category for reporting
```

Validation is advisory — `validateFrontmatter()` reports violations but doesn't block creation. This keeps agents fast while letting tooling surface warnings.

## Creating New Primitive Types

Create entirely new primitives by adding a template:

```yaml
# templates/sprint.md
---
primitive: sprint
description: Sprint planning document
fields:
  number:
    type: number
    required: true
  start:
    type: date
    required: true
  end:
    type: date
    required: true
  goal:
    type: string
    description: Sprint goal statement
  velocity:
    type: number
    description: Planned story points
---

# Sprint {{title}}

## Goal
{{content}}

## Planned Work
- [ ] 

## Retro Notes
- 
```

## Modifying the Body Scaffold

The body below the YAML `---` is the document scaffold. Customize it to include sections your team needs:

```yaml
---
# ... fields ...
---

# {{title}}

{{links_line}}

## Acceptance Criteria
- [ ] 

## Technical Notes


## Dependencies
- 

## Testing
- [ ] Unit tests
- [ ] Integration tests
```

## Template Variables

Available in defaults and body:

| Variable | Expands To |
|----------|-----------|
| `{{title}}` | Document title |
| `{{date}}` | Current date (YYYY-MM-DD) |
| `{{datetime}}` | Current ISO timestamp |
| `{{type}}` | Primitive type name |
| `{{content}}` | Provided body content |
| `{{links_line}}` | Auto-generated wiki-links |

## Regenerating Bases Views

After changing templates, regenerate Obsidian Bases views:

```bash
clawvault setup --bases --force
```

This updates `.base` files to include any new fields in table/card views.

## Migration Tips

When changing schemas on an existing vault:

1. **Adding fields** — safe, existing files just won't have the field
2. **Removing fields** — safe, existing files keep the field but new ones won't have it
3. **Renaming fields** — BREAKING, existing files still use the old name. Run a find-and-replace across `tasks/*.md` if needed
4. **Changing enum values** — safe for new files, existing files keep old values
5. **Changing defaults** — only affects newly created files

**Golden rule:** Add freely, rename carefully, never delete without migrating.
