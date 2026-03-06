# Memory Template - Home Server

Create `~/home-server/memory.md` with this structure:

```markdown
# Home Server Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Context
- Hardware profile and host OS
- Core services and exposure policy
- Stated reliability and security priorities

## Service Inventory
- Service name -> purpose -> data path -> exposure level
- Owner and maintenance cadence

## Backup Coverage
- What is backed up
- Where backups are stored
- Last restore test date

## Notes
- Repeated failure patterns
- Proven recovery procedures
- Preferences inferred from behavior

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Context still evolving | Keep learning from normal work |
| `complete` | Stable environment model exists | Operate with current assumptions |
| `paused` | User requested less setup discussion | Limit follow-up questions |
| `never_ask` | User asked to stop setup discovery | Only use explicit requests |

## Rules

- Use natural language observations, not exposed config keys.
- Update `last` whenever home server context changes.
- Promote recurring incidents into explicit prevention notes.
- Never delete prior context without confirmation.
