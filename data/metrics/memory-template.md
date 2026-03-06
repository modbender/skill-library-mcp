# Memory Template - Metrics

Create `~/metrics/memory.md` with this structure:

```markdown
# Metrics Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | done | declined

## Operating Context
- Domain focus:
- Decision horizon: daily | weekly | monthly | quarterly
- Main stakeholders:
- Current primary objective:

## Metric Registry Index
| Metric | Owner | Grain | Segment Lens | Source | Health |
|--------|-------|-------|--------------|--------|--------|
| Example: Activation Rate | Growth | Weekly | Channel | warehouse.events | green |

## Formula Inventory
| Formula | Version | Inputs | Guardrails | Last Change |
|---------|---------|--------|------------|-------------|
| Example: CAC Payback | v1.0.0 | spend, gross margin | null checks | YYYY-MM-DD |

## Reporting Calendar
- Daily report owner:
- Weekly report owner:
- Monthly report owner:
- Last report date:

## Alert Policies
- Trigger:
  Severity:
  Owner:
  First response:
  Escalation path:

## Decision Log
- Date:
  Decision:
  Metric signal:
  Confidence:
  Follow-up date:

## Backlog
- [ ]
- [ ]

## Notes
- Stable context and constraints worth retaining.
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Context still evolving | Keep collecting context while shipping useful outputs |
| `complete` | Baseline is stable | Focus on execution and continuous optimization |
| `paused` | User postponed setup | Continue work without setup prompts |
| `never_ask` | User opted out permanently | Never ask setup questions again |

## Memory Hygiene

- Store decisions and definitions, not raw chat transcripts.
- Keep formula history auditable with short version notes.
- Archive retired metrics instead of deleting context.
