---
name: gateway-auto-rollback
description: |
  Automatic configuration rollback mechanism for OpenClaw Gateway.
  Provides three-layer protection: pre-modification backup, post-modification validation,
  and automatic rollback on failure. Includes a file watcher daemon, JSON validation,
  Gateway health checks, and SHA256 content-addressed backups.
  Use when modifying openclaw.json or other critical config files to prevent
  accidental breakage and ensure zero-downtime configuration changes.
---

# Gateway Auto-Rollback

**Three-layer configuration protection for OpenClaw Gateway** — never break your config again.

## What It Does

Automatically protects your OpenClaw configuration files with:

1. **Pre-modification backup** — SHA256 content-addressed snapshots before any change
2. **Post-modification validation** — JSON syntax check + Gateway health probe
3. **Automatic rollback** — instant restore if validation fails

## When to Use

- Before modifying `openclaw.json`, `exec-approvals.json`, or `skills.json`
- When running automated config changes (cron jobs, scripts)
- As a background safety net during development
- When you want peace of mind that a bad config won't take down your agent

## Quick Start

### One-shot check (before manual edits)

```bash
python3 gateway-auto-rollback.py
```

This initializes the backup directory, validates current config, and logs status.

### Watch mode (background daemon)

```bash
python3 gateway-auto-rollback.py --watch &
```

Monitors critical config files every 3 minutes. Auto-exits after 3 consecutive healthy checks (config is stable).

## How It Works

```
Before Modification        During              After Modification
       ↓                    ↓                        ↓
  Backup + Hash  ───→  Execute Change  ───→  JSON Validate + Health Check
       │                                          │
       └──────────────────────────────────────→ Auto-rollback on failure
```

### Protected Files

| File | Description |
|------|-------------|
| `openclaw.json` | Main Gateway configuration |
| `exec-approvals.json` | Command execution approvals |
| `skills.json` | Skills registry |

### Backup Naming

Backups are stored in `~/.openclaw/backup/` with content-addressed names:

```
openclaw.json.20260301_053612.a1b2c3d4.bak
                 ↑ timestamp    ↑ SHA256 prefix (dedup)
```

## API Reference

### Python Functions

```python
from gateway_auto_rollback import (
    pre_modification_check,   # Call before modifying config
    post_modification_verify, # Call after modifying config
    create_backup,            # Manual backup creation
    validate_json,            # JSON syntax validation
    check_gateway_health,     # Gateway health probe
    rollback_to_backup,       # Manual rollback
    watch_config_files,       # Start watch daemon
)
```

### Pre-modification flow

```python
from pathlib import Path

config = Path.home() / ".openclaw" / "openclaw.json"

# Returns backup path on success, False on failure
backup = pre_modification_check(config)

# ... make your changes ...

# Validates and auto-rolls back if needed
success = post_modification_verify(config, backup)
```

### Watch mode details

The watcher:
- Polls every **3 minutes** (gives Gateway time to restart)
- Detects changes via SHA256 hash comparison
- Auto-creates backup when change detected
- Validates JSON + health check after each change
- **Auto-exits** after 3 consecutive healthy checks (config stabilized)
- Logs all events to `~/.openclaw/logs/config-modification.log`

## Integration with Cron

Set up periodic health checks:

```bash
# Cron job example: check every hour
0 * * * * python3 /path/to/gateway-auto-rollback.py
```

Or use OpenClaw's built-in cron:

```json
{
  "name": "Gateway-Auto-Rollback",
  "schedule": { "kind": "cron", "expr": "0 */6 * * *", "tz": "Asia/Shanghai" },
  "payload": {
    "kind": "agentTurn",
    "message": "Run gateway health check. If unhealthy, rollback to latest backup."
  },
  "sessionTarget": "isolated"
}
```

## Manual Rollback

If you need to manually restore a config:

```bash
# List available backups (newest first)
ls -lt ~/.openclaw/backup/ | head -10

# Restore a specific backup
cp ~/.openclaw/backup/openclaw.json.20260301_053612.a1b2c3d4.bak \
   ~/.openclaw/openclaw.json

# Restart Gateway
openclaw gateway restart

# Verify
curl -s http://127.0.0.1:18789/api/health
```

## Testing

Run the included test suite to verify the mechanism works:

```bash
bash test-rollback-mechanism.sh
```

Tests cover:
- Backup directory existence
- JSON validation
- SHA256 hash computation
- Backup creation and restore
- Watch daemon status
- Log file integrity
- Script permissions

## Logs

All events are logged to `~/.openclaw/logs/config-modification.log`:

```
[2026-03-01 05:37:00] INFO: ✅ 备份创建: openclaw.json.20260301_053612.a1b2c3d4.bak
[2026-03-01 05:37:01] INFO: ✅ 修改验证通过
[2026-03-01 05:40:00] WARN: ⚠️ 检测到修改: openclaw.json
[2026-03-01 05:40:01] ERROR: JSON 验证失败 — 触发回滚
```

## Requirements

- Python 3.8+
- OpenClaw Gateway running (for health checks)
- No additional pip packages needed (stdlib only)

## File Structure

```
gateway-auto-rollback/
├── SKILL.md                      # This file
├── _meta.json                    # ClawHub metadata
├── gateway-auto-rollback.py      # Main script (backup/validate/rollback/watch)
└── test-rollback-mechanism.sh    # Test suite
```
