# Memory Template — Notion API

Create `~/notion-api-integration/memory.md` with this structure:

```markdown
# Notion Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | done | declined

## Context
<!-- What you know about their Notion workspace -->
<!-- Workspace name if shared -->
<!-- Main databases they work with and their purposes -->
<!-- Common operations they request -->

## Databases
<!-- Key databases they've mentioned or queried -->
<!-- Format: db_XXX: Database Name (purpose) -->

## Notes
<!-- Internal observations -->
<!-- Property names they use frequently -->
<!-- Any pagination patterns or preferences -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning | Ask questions when relevant |
| `complete` | Has enough context | Work normally |
| `paused` | User said "not now" | Don't ask, work with what you have |
| `never_ask` | User said stop | Never ask for more context |

## Key Principles

- **No config keys visible** — use natural language, not "default_page_size: 100"
- **Learn from behavior** — if they always query the same database, remember it
- **Track databases loosely** — note what they use but don't maintain full inventory
- Update `last` on each use
