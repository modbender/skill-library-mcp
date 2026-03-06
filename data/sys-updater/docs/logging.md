# Logging

## Location

Logs are stored in `state/logs/` (configurable via `SYS_UPDATER_LOG_DIR`).

```
state/logs/
├── apt_maint.log           # Current day's log
├── apt_maint.log.2024-01-14 # Previous days (rotated)
├── apt_maint.log.2024-01-13
└── ...
```

## Rotation

- **Rotation**: Daily at midnight UTC
- **Retention**: 10 days (configurable in code: `backupCount=10`)
- **Handler**: `TimedRotatingFileHandler` from Python stdlib

## Log Format

```
2024-01-15T06:00:05Z [INFO] === run_6am START ===
2024-01-15T06:00:05Z [INFO] State files: last_run=/path/to/last_run.json, tracked=/path/to/tracked.json
2024-01-15T06:00:05Z [INFO] Running: sudo apt-get update
2024-01-15T06:00:12Z [INFO] apt-get update: OK
2024-01-15T06:00:12Z [INFO] Running: sudo unattended-upgrade -d
2024-01-15T06:00:45Z [INFO] unattended-upgrade: OK (rc=0)
...
2024-01-15T06:01:02Z [INFO] === run_6am END (success) ===
```

Format: `%(asctime)s [%(levelname)s] %(message)s`

## What is Logged

| Event | Level | Example |
|-------|-------|---------|
| Phase start/end | INFO | `=== run_6am START ===` |
| Command execution | INFO | `Running: sudo apt-get update` |
| Command result | INFO/ERROR | `apt-get update: OK` or `FAILED (...)` |
| State file paths | INFO | `State files: last_run=..., tracked=...` |
| Package counts | INFO | `Upgradable packages found: 5` |
| Tracking summary | INFO | `Tracking summary: planned=2, blocked=1` |
| Unhandled exceptions | ERROR | Full traceback |

## What is NOT Logged

- Passwords or authentication tokens
- Telegram bot tokens or session strings
- Full command output (only summaries)
- Environment variables containing secrets

## Console Logging (Verbose Mode)

Use `--verbose` / `-v` to also log to stderr:

```bash
python3 scripts/apt_maint.py run_6am --verbose
```

Console output uses simplified format: `[LEVEL] message`

## Viewing Logs

```bash
# Recent entries
tail -100 state/logs/apt_maint.log

# Follow in real-time
tail -f state/logs/apt_maint.log

# Search for errors
grep ERROR state/logs/apt_maint.log*

# Last run summary
grep -A 20 "run_6am START" state/logs/apt_maint.log | tail -25
```

## Cron Logs

Cron output (stdout/stderr not captured by the logging system) goes to `state/logs/cron.log` if configured in crontab with redirection.
