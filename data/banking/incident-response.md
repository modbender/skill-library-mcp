# Banking Incident Response

Use this flow for fraud, unauthorized activity, system outages, or control failures.

## Severity Levels

| Level | Description | Response Target |
|-------|-------------|-----------------|
| P1 | Active fraud or funds at immediate risk | Start containment now |
| P2 | Material payment disruption or repeated failures | Start triage within 15 minutes |
| P3 | Isolated issue with low financial impact | Resolve in normal queue with owner |

## Containment First

1. Stop active exposure:
   - Freeze affected account path when policy allows.
   - Hold pending transactions linked to the incident.
2. Preserve evidence:
   - Keep transaction IDs, timestamps, and control state.
   - Avoid destructive edits to source logs.
3. Notify owners:
   - Operations owner
   - Fraud or risk owner
   - Compliance contact when required

## Recovery Sequence

1. Define scope: customers, rails, and funds impacted.
2. Apply minimal viable fix with rollback plan.
3. Re-run validation checks on one controlled sample.
4. Resume normal processing in staged increments.
5. Monitor for repeat symptoms during the next cycle.

## Communication Cadence

- Internal updates: every 15-30 minutes for P1 and P2.
- Customer updates: when status changes materially.
- Include known facts, current action, and next checkpoint.

## Closeout Requirements

- Root cause statement in one paragraph.
- Control gap and corrective action.
- Owner and deadline for permanent fix.
- Lessons added to ongoing memory notes.
