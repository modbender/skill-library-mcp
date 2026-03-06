# Memory Template — Open Router

Create `~/open-router/memory.md` with this structure:

```markdown
# Open Router Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | complete | paused | never_ask

## Activation
- Auto-activate when:
- Explicit-only topics:
- Never activate for:

## Stack Context
- Client type:
- Provider wiring:
- Auth mode:
- Region or latency constraints:

## Routing Policy
- Workload class:
- Primary model:
- Fallback model:
- Trigger for fallback:

## Budget Guardrails
- Monthly budget:
- Per-task budget:
- Escalation threshold:

## Incident Log
- Date:
- Failure mode:
- Impact:
- Fix applied:

## Notes
- Decision:
- Follow-up:

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Context still evolving | Continue learning from real routing events |
| `complete` | Baseline policy is stable | Minimize setup questions and execute directly |
| `paused` | User paused setup prompts | Use existing policy without asking for new setup details |
| `never_ask` | User declined setup | Never request setup details again |

## Principles

- Keep memory concise and operational.
- Store decisions and outcomes, not raw secrets.
- Update `last` after meaningful routing changes.
- Record incidents in terms of failure mode and verified fix.
