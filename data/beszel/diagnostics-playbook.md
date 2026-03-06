# Beszel Diagnostics Playbook

## Objective

Resolve monitoring failures quickly with a consistent triage sequence.

## Triage Order

1. Confirm symptom scope:
- Is the issue one node, one service group, or the full stack?

2. Check component health:
- Validate hub and agent process status.
- Check recent restart loops or crash indicators.

3. Verify connectivity:
- Confirm network path between hub and agent.
- Check DNS resolution and firewall policies.

4. Validate time consistency:
- Compare host clocks for hub and agents.
- Correct drift before interpreting event timelines.

5. Inspect resource pressure:
- Review CPU, memory, disk, and I/O pressure on impacted nodes.
- Correlate telemetry gaps with host saturation windows.

6. Confirm version compatibility:
- Check hub and agent versions before concluding protocol issues.

## Incident Note Template

Use this minimal format in `incidents.md`:

```markdown
## YYYY-MM-DD - Incident Title
- Impact:
- Detection signal:
- Root cause:
- Fix applied:
- Prevention update:
```

## Escalation Guidance

- Escalate immediately when monitoring blind spots affect production.
- Escalate when repeated disconnects persist after connectivity checks.
- Escalate if upgrades introduce persistent metric gaps.

## Post-Incident Follow-up

- Update alert thresholds only after root cause is confirmed.
- Add one preventive rule tied to the incident.
- Record owner and due date for unresolved remediation.
