![OpenClaw Model Router](assets/logo.jpg?v=20260228-2315)

<h1 align="center">OpenClaw Model Router Skill</h1>

<p align="center">
Deterministic model routing for OpenClaw: prefix-based switching + timezone-aware scheduler,
with verification, rollback, lock protection, and JSONL audit logs.
</p>

---

## What it does

- **Prefix routing**
  - `@codex` → `openai-codex/gpt-5.3-codex`
  - `@mini` → `minimax/MiniMax-M2.5`
  - aliases: `@c`, `@m`
- **Route pipeline**: `parse -> validate -> switch -> verify -> execute`
- **Time-based scheduler** with rule priority + overnight windows
- **Production safety**
  - post-switch verification
  - rollback on failure (configurable)
  - lock file to avoid concurrent switch races
  - structured JSONL audit logs

---

## Quick Start

```bash
# Validate config
node src/cli.js validate

# Inspect route decision
node src/cli.js route "@codex implement this" --json

# Parse only
node src/cli.js parse "@mini summarize this"
```

---

## Scheduler

Schedule config: `router.schedule.json`

```json
{
  "timezone": "Europe/Rome",
  "rules": [
    {
      "id": "workday_codex",
      "days": ["mon", "tue", "wed", "thu", "fri"],
      "start": "09:00",
      "end": "18:00",
      "model": "openai-codex/gpt-5.3-codex",
      "priority": 10,
      "enabled": true
    },
    {
      "id": "night_mini",
      "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
      "start": "18:00",
      "end": "09:00",
      "model": "minimax/MiniMax-M2.5",
      "priority": 1,
      "enabled": true
    }
  ]
}
```

Scheduler commands:

```bash
node src/cli.js schedule list --json
node src/cli.js schedule validate
node src/cli.js schedule resolve --at "2026-03-02T10:00:00+01:00" --json
node src/cli.js schedule apply --json
node src/cli.js schedule end --id workday_codex --json
node src/cli.js schedule cron
```

---

## Production Execution Loop (Closed-Loop)

This repo now supports a real production switch loop:

1. **Switch entry**: `schedule apply`
2. **Auth gate**: `auth.requiredEnv[]`
3. **Model set + readback verify**
4. **Failure classification** (`auth_expired | rate_limit | provider_drift | unknown`)
5. **Rollback** (if enabled)
6. **Concurrency lock** (`safety.lockPath`)
7. **Audit logging** (`router.log.jsonl` with rotation)

---

## Config (router.config.json)

Important fields:

- `prefixMap`, `aliasMap`
- `retry.maxRetries / baseDelayMs / verifyRetries / verifyDelayMs`
- `defaultModel`
- `auth.requiredEnv[]`
- `safety.rollbackOnFailure / lockPath / lockStaleMs`
- `logging.path`
- `sessionController.binary / setArgsPrefix / statusArgs`

---

## Testing

```bash
node --test
```

Current suite covers:
- prefix parsing & aliasing
- routing + fallback behavior
- prefix-only switch confirmation
- retry and verification failures
- scheduler conflict detection
- timezone-aware schedule resolution

---

## Docs

- `docs/runbook.md`
- `docs/scheduler-notes.md`
