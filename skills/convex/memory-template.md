# Memory Template - Convex

Create `~/convex/memory.md` with this structure:

```markdown
# Convex Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Project Context
<!-- Repos and environments using Convex -->
<!-- Product domain and lifecycle stage -->

## Data Model Decisions
<!-- Table shapes, relationship assumptions, naming choices -->
<!-- Decisions that should remain stable across iterations -->

## Index Strategy
<!-- Access paths that must stay fast -->
<!-- Index rationale and known constraints -->

## Auth and Permissions
<!-- Identity model and tenant boundaries -->
<!-- Permission checks that must never be bypassed -->

## Rollout and Incidents
<!-- Migration notes and deployment caveats -->
<!-- Incident summaries and preventive actions -->

## Notes
<!-- Durable, high-signal implementation lessons -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Default learning state | Keep collecting technical context |
| `complete` | Stable context available | Use memory as primary defaults |
| `paused` | User wants fewer prompts | Ask only when critical data is missing |
| `never_ask` | User rejected setup prompts | Stop prompting and operate with existing context |

## Integration Values

| Value | Meaning |
|-------|---------|
| `pending` | Activation preference not confirmed |
| `done` | Activation preference confirmed |
| `declined` | User wants manual activation only |

## Key Principles

- Store decisions that improve future Convex work, not raw chat logs.
- Keep memory concise and implementation-focused.
- Redact secrets and sensitive identifiers before saving notes.
- Update `last` whenever memory is edited.
