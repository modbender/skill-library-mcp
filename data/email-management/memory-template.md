# Memory Template - Email Management

Create `~/email-management/memory.md` with this structure:

```markdown
# Email Management Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | complete | paused | never_ask

## Work Context
- Primary role:
- Main inbox types:
- High-priority contacts:
- Default response tone:
- Quiet hours:

## Routing Rules
- Urgent if:
- Action if:
- Waiting if:
- Archive if:

## Follow-up Defaults
- Standard follow-up window:
- Escalation threshold:
- Reminder cadence:

## Active Commitments
- Thread | Owner | Due date | Status

## Notes
- Short observations safe to persist.

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | context still forming | keep refining routing and tone |
| `complete` | context stable | apply defaults with minimal prompts |
| `paused` | updates paused | read-only memory use |
| `never_ask` | no setup follow-ups | avoid setup-related questions |

## Key Principles

- Store durable preferences and decisions, not raw email dumps.
- Never store passwords, tokens, or full payment details.
- Keep active commitments current and remove closed items quickly.
- Update `last` whenever memory is written.
