# Memory Template - Shipping Operations

Create `~/shipping/memory.md` with this structure:

```markdown
# Shipping Operations Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Business Context
<!-- Product types, average order value, destination mix -->
<!-- SLA promises, return policy constraints -->

## Carrier Preferences
<!-- Preferred carriers by lane and package profile -->
<!-- Known carrier constraints and account limits -->

## Cost Patterns
<!-- Repeated surcharges and landed-cost drivers -->
<!-- Packaging choices that reduced cost without damage -->

## International Rules
<!-- Country-specific customs notes and documents -->
<!-- Duties/taxes handling preferences and Incoterms -->

## Incident Patterns
<!-- Delay/loss/damage history with resolved outcomes -->
<!-- Which escalations worked fastest and why -->

## Notes
<!-- Stable operational insights worth reusing -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Default learning state | Keep collecting route and carrier evidence |
| `complete` | Stable operating context | Use memory as primary default |
| `paused` | User wants fewer prompts | Ask only when critical data is missing |
| `never_ask` | User rejected setup prompts | Stop prompting and operate silently |

## Integration Values

| Value | Meaning |
|-------|---------|
| `pending` | Activation preference not confirmed |
| `done` | Activation preference confirmed |
| `declined` | User wants manual activation only |

## Key Principles

- Record decisions that improve future shipments, not chat transcripts.
- Keep memory concise and route oriented.
- Redact sensitive identifiers before storing notes.
- Update `last` whenever memory is edited.
