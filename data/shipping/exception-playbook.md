# Exception Playbook - Shipping Operations

## Incident Types and First Response

| Incident | First move | Deadline risk |
|----------|------------|---------------|
| No first scan | Verify handoff proof and pickup event | Missed SLA within 24h |
| In-transit delay | Check lane disruption and update ETA | Customer trust erosion |
| Customs hold | Resolve missing document immediately | Return to sender risk |
| Damaged on arrival | Collect photos and packaging evidence | Claim denial if delayed |
| Lost package | Open trace and claim with full evidence | Claim window expiration |
| Refused delivery | Confirm reason and next disposition | Return fees and stock ambiguity |

## Evidence Checklist

Collect before escalation:
- Label and tracking number
- Pickup/dropoff proof
- Weight and dimensions used for quote
- Invoice and customs documents if international
- Photos for damage cases
- Customer communication timeline

No evidence package means weak claim position.

## Customer Communication Rules

- Acknowledge issue quickly with current facts only.
- Give next update time, not vague promises.
- State what you are doing and what is pending from carrier.
- Offer options when threshold is met: wait, reship, or refund.

Silence creates more support load than bad news.

## Escalation Thresholds

Use explicit triggers:
- First scan missing beyond 24h -> open carrier case.
- Delay beyond promised window -> proactive customer update.
- No carrier movement for 48h -> escalate to supervisor queue.
- Claim-relevant incident -> start claim workflow immediately.

Adjust thresholds per carrier SLA if documented.

## Postmortem Pattern

After resolution, log:
- Root cause category (label, handoff, lane, customs, packaging)
- Cost impact (refund, reship, surcharge, labor)
- Preventive control for next shipment

Feed results back into memory and carrier-selection rules.
