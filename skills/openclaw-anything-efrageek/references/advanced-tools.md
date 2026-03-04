# OpenClaw Advanced Tools Reference

Reference normalized against:
- `https://docs.openclaw.ai/tools`
- `https://docs.openclaw.ai/tools/browser`
- `https://docs.openclaw.ai/automation/cron-jobs`
- `https://docs.openclaw.ai/plugins`
- `https://docs.openclaw.ai/cli/gateway`

Last verified: 2026-02-17.

## Safety First
This file documents advanced capabilities for operator awareness.
It does not grant blanket authorization to execute privileged or high-risk operations.
See `references/security-policy.md`.

## Gateway API Utility
Use gateway API calls directly from CLI:
- `openclaw gateway call <path>`

Typical patterns:
- health checks
- custom automation hooks
- debugging specific gateway endpoints

## Managed Browser (High-risk)
- `openclaw browser start`
- `openclaw browser open <url>`
- `openclaw browser screenshot [--full-page]`
- `openclaw browser snapshot --format aria`
- `openclaw browser stop`

Requires explicit approval and wrapper opt-in.

## Cron Automation (High-risk)
- `openclaw cron list`
- `openclaw cron add ...`
- `openclaw cron run <jobId>`
- `openclaw cron remove <jobId>`

Creation, run, and delete operations require explicit approval.

## Plugins (High-risk)
- `openclaw plugins list`
- `openclaw plugins install <path-or-url>`
- `openclaw plugins enable <name>`
- `openclaw plugins disable <name>`

Install and enable operations should be limited to trusted sources.

## Upstream Runtime Capabilities (Awareness)
Depending on OpenClaw runtime configuration, upstream may expose:
- `exec` style arbitrary command execution
- elevated permission workflows
- sub-agent delegation

Treat these as privileged features with explicit, per-action approval.
