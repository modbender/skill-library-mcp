# Memory Template - Beszel

Create `~/beszel/memory.md` with this structure:

```markdown
# Beszel Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Context
- Monitoring scope and critical services
- Reliability goals and risk tolerance
- Constraints for maintenance and response

## Node Inventory
- Node name -> role -> owner -> criticality
- Connectivity notes and known constraints

## Alert Strategy
- Primary thresholds by service class
- Escalation path and response expectation
- Known noisy alerts and suppression approach

## Incident Notes
- Timeline summary for major incidents
- Root cause and validated fix
- Prevention actions to apply next time

## Notes
- Observed preferences inferred from behavior
- Important pending follow-ups

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Context still evolving | Keep learning during normal operations |
| `complete` | Monitoring model is stable | Operate with current assumptions |
| `paused` | User wants less setup detail | Minimize follow-up questions |
| `never_ask` | User asked to stop discovery | Use only explicit instructions |

## Rules

- Use concise natural-language notes, not exposed config keys.
- Update `last` whenever monitoring context changes.
- Promote repeated incidents into prevention rules.
- Never delete prior context without confirmation.
