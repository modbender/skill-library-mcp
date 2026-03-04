# Memory Template - AirTag

Create `~/airtag/memory.md` with this structure:

```markdown
# AirTag Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | done | declined

## Context
<!-- Stable environment details, in natural language -->
<!-- Example: User carries two AirTags (keys, backpack) and often commutes by train -->

## Notes
<!-- Operational observations and repeated patterns -->
<!-- Example: Precision Finding fails indoors on office floor 12; map ring still works -->

## Active Incidents
<!-- Open incidents with timestamp, item, last-known location, and next action -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning usage patterns | Continue collecting context during normal use |
| `complete` | Enough context for reliable support | Focus on execution and periodic refresh |
| `paused` | User wants fewer follow-ups | Minimize questions and act with existing context |
| `never_ask` | User does not want setup questions | Do not request additional setup details |

## Principles

- Keep notes actionable and scoped to AirTag use.
- Prefer short incident records over long narratives.
- Record what changed and what was validated after each fix.
- Never store credentials, payment data, or unrelated private content.
