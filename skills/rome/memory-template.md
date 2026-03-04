# Memory Template — Rome

Create `~/.rome/memory.md` with this structure:

```markdown
# Rome Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | done | declined

## Context
<!-- What you know about their Rome situation -->
<!-- Role: visitor, expat, digital nomad, student, retiree -->
<!-- Nationality: visa implications -->
<!-- Timeline: when visiting, when moving, how long there -->
<!-- Italian level: none, basic, intermediate, fluent -->

## Neighborhoods
<!-- Areas they're interested in or considering -->
<!-- Budget constraints if any -->

## Notes
<!-- Preferences learned from conversations -->
<!-- Things to remember for future interactions -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning | Gather context opportunistically |
| `complete` | Has enough context | Work normally |
| `paused` | User said "not now" | Don't ask, work with what you have |
| `never_ask` | User said stop | Never ask for more context |

## Key Principles

- **No config keys visible** — use natural language
- **Learn from behavior** — observe and confirm, don't interrogate
- **Most stay `ongoing`** — always learning, that's fine
- Update `last` on each use
