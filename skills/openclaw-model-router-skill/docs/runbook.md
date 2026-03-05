# Model Router Runbook

## Validate configuration

```bash
node -e "console.log(require('./router.config.json'))"
```

## Run tests

```bash
node --test
```

## Integration contract

`routeAndExecute(...)` requires:

- `sessionController.getCurrentModel()`
- `sessionController.setModel(model)`
- `taskExecutor.execute(text)`
- `logger.log(event)`

## Scheduler (time-based model routing)

Validate and resolve schedule:

```bash
node src/cli.js schedule validate
node src/cli.js schedule resolve --at "2026-02-28T10:00" --json
```

Apply active rule (production switch):

```bash
node src/cli.js schedule apply --json
```

Force apply a specific rule:

```bash
node src/cli.js schedule apply --id workday_codex --json
```

End a rule window (restore router.config.defaultModel):

```bash
node src/cli.js schedule end --id workday_codex --json
```

Generate cron preview (manual install):

```bash
node src/cli.js schedule cron
```

## Operational notes

- Prefix-based routing is deterministic and idempotent.
- Switching is verified before task execution.
- Route events are JSONL and can be tailed for observability.
- Schedule apply uses a lock file (`safety.lockPath`) to prevent concurrent switches.
- Auth prerequisites can be enforced with `auth.requiredEnv`.
- On switch failure, rollback is controlled by `safety.rollbackOnFailure`.
- Failures are classified to support triage: `auth_expired`, `rate_limit`, `provider_drift`, `unknown`.

## New failure surfaces (2026-02-28 sprint)

- `FALLBACK_EXECUTION_FAILED`: primary execution failed, router switched to fallback model, but fallback execution still failed.
  - Action: inspect upstream tool/service health and payload validity.
- Config validation now fails fast at load time for malformed `prefixMap`/`retry` fields.
  - Action: fix `router.config.json` shape before runtime.
