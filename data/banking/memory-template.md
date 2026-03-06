# Memory Template - Banking

Create `~/banking/memory.md` with this structure:

```markdown
# Banking Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | complete | paused | never_ask

## Activation
- Auto-activate when:
- Activate only on explicit request for:
- Never activate for:

## Operating Context
- Jurisdiction:
- Customer profile:
- Account types:
- Payment rails:
- Cutoff windows:
- Approval controls:

## Active Incidents
- Incident:
  - Category:
  - Detection time:
  - Containment:
  - Current status:
  - Next action:

## Approved Communication Patterns
- Scenario:
  - Internal update format:
  - Customer update format:
  - Escalation trigger:

## Known Risks and Constraints
- Constraint:
  - Impact:
  - Mitigation:

## Notes
- Decision:
- Follow-up:

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Context is still evolving | Keep gathering operational constraints naturally |
| `complete` | Context is sufficient | Run workflows without setup prompts |
| `paused` | User paused setup refinements | Continue with current context only |
| `never_ask` | User rejected setup prompts | Do not ask setup follow-ups again |

## Principles

- Keep entries brief, factual, and easy to verify.
- Update `last` after every meaningful banking workflow session.
- Store decisions and controls, not sensitive raw account data.
- Preserve incident history with timestamps and explicit outcomes.
