# Memory Template - Scale Frameworks

Create `~/scale/memory.md` with this structure:

```markdown
# Scale Frameworks Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Scale Context
<!-- What is being scaled and why now -->
<!-- Stage, constraints, and target horizon -->

## Bottleneck Map
<!-- Current dominant bottleneck and evidence -->
<!-- Secondary bottlenecks to monitor next -->

## Lever Backlog
<!-- Candidate interventions with impact, effort, and risk -->
<!-- Explicitly mark temporary boosts vs durable capacity -->

## Metrics and Guardrails
<!-- Primary throughput metric and paired guardrails -->
<!-- Thresholds that trigger pause, rollback, or escalation -->

## Decision Log
<!-- Major decisions, owner, date, and expected outcome -->
<!-- What changed after rollout -->

## Notes
<!-- Stable operating patterns worth reusing -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Default learning state | Keep refining bottlenecks and leverage patterns |
| `complete` | Stable scaling model | Reuse memory as primary planning baseline |
| `paused` | User wants fewer prompts | Ask only when critical data is missing |
| `never_ask` | User rejected setup prompts | Stop prompting and operate silently |

## Integration Values

| Value | Meaning |
|-------|---------|
| `pending` | Activation preference not confirmed |
| `done` | Activation preference confirmed |
| `declined` | User wants manual activation only |

## Key Principles

- Capture reusable scaling evidence, not full chat transcripts.
- Keep entries concise and decision-oriented.
- Redact sensitive identifiers before storing notes.
- Update `last` whenever memory is edited.
