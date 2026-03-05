---
name: openclaw-healthcheck-cron
description: Create and run a reusable OpenClaw deep healthcheck automation using a cron job plus a script. Use when setting up scheduled OpenClaw health audits, standardizing security/status checks, sanitizing environment-specific values for sharing, and packaging the setup for reuse.
---

# OpenClaw Healthcheck Cron Skill

Create a portable healthcheck automation that runs on a schedule and reports concise findings.

## Build the automation

1. Create a script at `scripts/healthcheck.sh` (or reuse the one in this skill).
2. Keep checks read-only by default.
3. Write artifacts to `/tmp/openclaw-healthcheck/YYYY-MM-DD/HHMMSS/`.
4. Return a compact summary with severity.

## Create the scheduled job

Use an isolated cron `agentTurn` job that runs twice daily (example: 6am and 7pm local time):

- `schedule.kind`: `cron`
- `schedule.expr`: `0 6,19 * * *`
- `schedule.tz`: set local timezone
- `sessionTarget`: `isolated`
- `payload.kind`: `agentTurn`
- `delivery.mode`: `announce` (or `none` if reporting is handled inside task)

Use this task pattern:
- Execute `bash scripts/healthcheck.sh`
- Parse summary line and emit:
  - Verdict: `OK | MONITOR | NEEDS_ATTENTION`
  - Counts: passed/warn/fail
  - Artifact path
  - Active issues + recommended next action

## Sanitize before publishing

Remove or parameterize all local identifiers:

- Usernames, hostnames, phone numbers, chat IDs
- API keys, tokens, webhook URLs
- Absolute personal paths (use placeholders or relative paths)

Replace with variables:

- `${HEALTHCHECK_OUTPUT_DIR:-/tmp/openclaw-healthcheck}`
- `${OPENCLAW_HEALTH_TZ:-America/New_York}`
- `${HEALTHCHECK_EXCLUDE:-small model,sandbox,groupPolicy}`

## Validate

1. Run script manually once.
2. Confirm artifact directory and summary format.
3. Run cron job once with `cron run`.
4. Verify final message is concise and actionable.

## Package

Package as a `.skill` zip containing only:

- `SKILL.md`
- `scripts/healthcheck.sh`
- `references/cron-job-example.json`
