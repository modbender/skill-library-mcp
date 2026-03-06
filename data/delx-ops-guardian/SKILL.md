---
name: Delx Ops Guardian
description: "name: delx-ops-guardian summary: Incident handling and operational
  recovery guardrails for OpenClaw production agents. owner: davidmosiah status:
  active"
---

name: delx-ops-guardian
summary: Incident handling and operational recovery guardrails for OpenClaw production agents.
owner: davidmosiah
status: active
---

# Delx Ops Guardian

Use this skill when handling incidents, degraded automations, or gateway/memory instability in production.

## Aliases
- `emergency_recovery`
- `handle_incident`
- `cron_guard`
- `memory_guard`
- `gateway_guard`

## Scope (strict)
This skill is **runbook-only** and must operate under least privilege.

Allowed read sources:
- OpenClaw cron state (`openclaw cron list --json`)
- Service health/status (`systemctl is-active <service>`)
- Recent logs for incident window (`journalctl -u <service> --since ... --no-pager`)
- Workspace incident artifacts (`/root/.openclaw/workspace/docs/ops/`, `/root/.openclaw/workspace/memory/`)

Allowed remediation actions (safe set):
1. Retry a failed job once when failure is transient.
2. Controlled restart of the impacted service **only** (`openclaw-gateway`, `openclaw`, or explicitly named target from incident evidence).
3. Disable/enable only the directly impacted cron job when loop-failing.
4. Add/adjust guardrails in runbook/config docs (non-secret, reversible).

Disallowed actions:
- No credential rotation/deletion.
- No firewall/network policy mutations.
- No package installs/upgrades during incident handling.
- No bulk cron rewrites unrelated to the incident.
- No edits to unrelated services/components.

## Approval policy (human-in-the-loop)
Require explicit human approval before:
- Restarting any production service more than once.
- Editing cron schedules/timezones.
- Disabling a job for more than one cycle.
- Any action with user-visible impact beyond the failing component.

## Core workflow
1. Detect and classify severity (`info`, `degraded`, `critical`).
2. Collect evidence first (status, logs, last run, error streak).
3. Propose smallest remediation from allowed set.
4. Execute only approved/safe remediation.
5. Verify stabilization window (at least one successful cycle).
6. Publish concise incident report.

## Safety rules
- Never hide persistent failures as success.
- Never expose secrets/tokens in logs or reports.
- Prefer reversible actions and document rollback path.
- Keep blast radius minimal and explicitly stated.

## Output contract
Always include:
- Incident id/time window
- Root signal and blast radius
- Actions executed (and approvals)
- Evidence (status, key metric, short log excerpt)
- Final state (`resolved`, `degraded`, `open`)
- Next check time

## Example intents
- "Gateway is flapping, recover safely."
- "Cron timed out, stabilize and prove fix."
- "Memory guard firing repeatedly, root-cause and patch."
