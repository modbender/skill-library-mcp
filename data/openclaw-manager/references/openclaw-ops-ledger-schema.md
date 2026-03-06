# OpenClaw Ops Ledger Schema

Use this schema for every ledger entry.

## Required Fields
- `timestamp_utc`
- `event`
- `operator`
- `mode`
- `provider`
- `os`
- `environment`
- `secrets_profile`
- `channels`
- `integrations`
- `security_status`
- `blocking_issues`
- `rollback_tested`
- `next_owner`
- `next_action_date`

## Event Types
- `scope_lock`
- `predeploy_validation`
- `deploy_complete`
- `security_gate`
- `handover`
- `incident`

## Rules
1. Never record secret values.
2. Record profile and key names only.
3. Keep one entry per event occurrence.
4. If `security_status=failed`, include actionable blockers.
5. `next_action_date` must be ISO date (`YYYY-MM-DD`).

## Example Entry
```markdown
## 2026-02-15T21:20:00Z | security_gate
- operator: codex
- mode: hosted
- provider: fly
- os: linux
- environment: prod
- secrets_profile: hosted-fly
- channels: telegram,slack
- integrations: email,calendar
- security_status: failed
- blocking_issues: gateway token rotation policy missing
- rollback_tested: no
- next_owner: platform-oncall
- next_action_date: 2026-02-16
```
