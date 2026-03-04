---
name: openclaw-model-router-skill
description: Production-grade model router for OpenClaw: prefix routing (@codex/@mini), timezone-aware schedule switching, verify-after-switch, rollback, lock protection, and JSONL audit logs.
---

# OpenClaw Model Router Skill

Deterministic model routing with a **closed-loop production switch pipeline**.

## Why use this skill

- Explicit user intent routing (`@codex`, `@mini`)
- Time-window model policy (`router.schedule.json`)
- Safe switch flow with verification and rollback
- Concurrency lock to prevent race conditions
- Structured audit logs for operations and incident review

## Core capabilities

1) **Prefix routing**
- `@codex` → `openai-codex/gpt-5.3-codex`
- `@mini` → `minimax/MiniMax-M2.5`
- Aliases: `@c`, `@m`

2) **Scheduler routing**
- Rule-based windows by day/time/priority
- Timezone-aware resolution (`router.schedule.json.timezone`)
- Supports overnight windows (e.g. 18:00 → 09:00)

3) **Production switch loop**
- `schedule apply` / `schedule end`
- Auth gate (`auth.requiredEnv[]`)
- Switch + readback verify
- Failure classification (`auth_expired`, `rate_limit`, `provider_drift`, `unknown`)
- Optional rollback (`safety.rollbackOnFailure`)
- Lock file (`safety.lockPath`) to avoid concurrent switching
- Audit logs (`router.log.jsonl` + rotation)

## Quick commands

```bash
# Validate config
node src/cli.js validate

# Route inspection
node src/cli.js route "@codex implement this" --json

# Scheduler
node src/cli.js schedule validate
node src/cli.js schedule resolve --at "2026-03-02T10:00:00+01:00" --json
node src/cli.js schedule apply --json
node src/cli.js schedule end --id workday_codex --json
```

## Key config files

- `router.config.json` (prefix map, retry, auth, safety, logging, controller)
- `router.schedule.json` (timezone + rules)

## Reliability checklist

- Deterministic mapping
- Idempotent switching behavior
- Execute only after switch verification
- Observable success/failure events
- Recoverability on failure paths

## Tests

```bash
node --test
```
