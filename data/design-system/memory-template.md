# Memory Template — Design System

Create `~/design-system/memory.md` with this structure:

```markdown
# Design System Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Context
<!-- Stack and platforms -->
<!-- Existing patterns to preserve -->
<!-- Team size and workflow -->

## Decisions
<!-- Key decisions made and why -->
<!-- Token naming conventions chosen -->
<!-- Component API patterns agreed -->

## Notes
<!-- Observations about their preferences -->
<!-- Things to remember for consistency -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning their system | Gather context, suggest patterns |
| `complete` | System is established | Maintain consistency, extend carefully |
| `paused` | User said "not now" | Work with what you have |
| `never_ask` | User said stop | Never ask for more context |

## Key Principles

- Use natural language in Context and Notes sections
- Update `last` on each use
- All data stays in ~/design-system/
