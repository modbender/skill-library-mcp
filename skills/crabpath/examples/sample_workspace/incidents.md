# Incident Response

## Before an incident
- Confirm deploy.md runbook has a fresh PR and signed-off approvals.
- Capture last 3 deployment IDs and attach to the incident record.
- Check monitoring.md dashboards for live error and latency deltas.

## During an incident
1. Pause risky rollouts; never skip rollback steps.
2. Page the on-call and record exact failed query + error text.
3. If traffic drops or error rate spikes, follow the deploy rollback checklist.
4. Validate fixes in staging before re-running deploy paths.

## After incident
- Post a concise timeline of root cause, detection, and resolution.
- Add one teaching note for future prevention.
- Ask the team to review `CI`, `deploy`, and `monitoring` links in this workspace.
