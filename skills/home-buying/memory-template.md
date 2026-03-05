# Memory Template - Home Buying

Create `~/home-buying/memory.md` with this structure:

```markdown
# Home Buying Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Buy Box
<!-- Non-negotiables: location, property type, size, timeline -->
<!-- Deal-breakers and acceptable compromises -->

## Budget Guardrails
<!-- Monthly all-in ceiling and preferred range -->
<!-- Cash to close range and reserve target -->

## Financing Context
<!-- Pre-approval status, rate assumptions, lender constraints -->
<!-- Preferred loan structure and timeline pressure -->

## Active Deal Pipeline
<!-- Properties under review and current stage -->
<!-- Key risks, blockers, and deadlines -->

## Offer Patterns
<!-- Price tiers that were approved or rejected -->
<!-- Concessions and contingency outcomes -->

## Due Diligence Lessons
<!-- Inspection findings that changed decisions -->
<!-- Recurring hidden-cost patterns by neighborhood or property type -->

## Notes
<!-- Durable insights to improve future home-buying decisions -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Default learning state | Keep collecting decision context incrementally |
| `complete` | Baseline stable | Use memory defaults with minimal clarifications |
| `paused` | User wants fewer prompts | Ask only when critical data is missing |
| `never_ask` | User rejected setup prompts | Stop setup prompts and operate on explicit input only |

## Integration Values

| Value | Meaning |
|-------|---------|
| `pending` | Activation preference not confirmed |
| `done` | Activation preference confirmed |
| `declined` | User wants manual activation only |

## Key Principles

- Keep notes decision-grade, not transcript-style.
- Prefer numbers, thresholds, and outcomes over narratives.
- Redact sensitive data before storing.
- Update `last` whenever memory changes.
