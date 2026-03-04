# Automation Patterns

Use these patterns to keep metric workflows scalable without alert fatigue.

## Automation Layers

| Layer | Purpose | Typical Trigger |
|-------|---------|-----------------|
| Collection | Refresh metric inputs | schedule or source update |
| Validation | Run quality gates | post-refresh |
| Reporting | Generate summary output | fixed cadence |
| Alerting | Escalate material deviations | threshold or anomaly |
| Learning | Update policy from outcomes | post-incident review |

## Trigger Design Rules

- Keep triggers tied to decision value, not data volume.
- Separate warning and critical thresholds.
- Add cooldown windows to avoid repeated noise.
- Attach owner and first response action to every trigger.

## Severity Model

| Severity | Condition | Response Target |
|----------|-----------|-----------------|
| Info | Small variance within normal range | Document and monitor |
| Warning | Variance likely requiring action | Owner reviews in next cycle |
| Critical | Breach with business impact | Immediate response and escalation |

## Escalation Template

When a critical trigger fires:

1. Confirm data validity before action.
2. Notify owner with impacted metrics and segments.
3. Run first response playbook.
4. Escalate if not stabilized by agreed SLA.
5. Log resolution and prevention step.

## Automation Hygiene

- Review thresholds monthly to reduce stale rules.
- Retire triggers that never lead to decisions.
- Track false-positive rate by policy.
- Record postmortems for major metric incidents.
