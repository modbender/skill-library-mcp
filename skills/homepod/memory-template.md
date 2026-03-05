# Memory Template - HomePod

Create `~/homepod/memory.md` with this structure:

```markdown
# HomePod Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | complete | paused | never_ask

## Activation
- Auto-activate when:
- Activate only on explicit request for:
- Never activate for:

## Environment Snapshot
- HomePod models:
- Home hub:
- Network topology:
- Critical accessories:
- Control boundaries:
- Protected targets:

## Active Incidents
- Incident:
  - Repro steps:
  - Observed behavior:
  - Probable layer:
  - Next check:

## Confirmed Fixes
- Fix:
  - Scope:
  - Validation:
  - Date:

## Control History
- Target:
  - Command:
  - Result:
  - User confirmed:

## Notes
- Decision:
- Follow-up:

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Context is still evolving | Keep collecting facts naturally |
| `complete` | Context is sufficient | Execute without setup prompts |
| `paused` | User paused setup refinements | Continue with current context only |
| `never_ask` | User rejected setup prompts | Do not ask setup follow-ups again |

## Principles

- Keep entries short, concrete, and testable.
- Update `last` after every meaningful troubleshooting session.
- Track evidence and outcomes, not speculation.
- Record failures and successful rollbacks, not only final wins.
