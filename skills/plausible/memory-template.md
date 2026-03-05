# Memory Template — Plausible

Create `~/plausible/memory.md` with this structure:

```markdown
# Plausible Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | done | declined

## Sites
<!-- Domains tracked in Plausible -->
<!-- Example: example.com, app.example.com -->

## Base URL
<!-- plausible.io (default) or self-hosted URL -->
<!-- Example: https://analytics.example.com -->

## Preferences
<!-- How user prefers data presented -->
<!-- Default period, favorite metrics, breakdown preferences -->

## Goals & Events
<!-- Custom goals and events configured in Plausible -->
<!-- Example: Signup, Purchase, Newsletter -->

## Notes
<!-- Observations about their analytics needs -->
<!-- Patterns in what they typically ask for -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning preferences | Gather context from queries |
| `complete` | Has enough context | Work normally |
| `paused` | User said "not now" | Don't ask, work with defaults |
| `never_ask` | User said stop | Never ask for more context |

## Key Principles

- **No config keys visible** — use natural language descriptions
- **Learn from queries** — note what metrics they request most
- **Most stay `ongoing`** — analytics needs evolve, keep learning
- Update `last` on each use
