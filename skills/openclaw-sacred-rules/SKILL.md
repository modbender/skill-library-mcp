---
name: openclaw-sacred-rules
description: OpenClaw configuration safety rules to prevent system disasters. Use when: (1) Making OpenClaw config changes, (2) Troubleshooting auth failures, (3) Taking system backups, (4) Recovering from config disasters, (5) User asks about config best practices, or (6) Before enabling/disabling system features like sandbox mode.
---

# OpenClaw Sacred Rules

The 8 Sacred Rules learned from production disasters. **Never violate these rules.**

## The 8 Sacred Rules

### 1. Verify Backups Before Confirming
```bash
# Always verify files exist and are valid
ls -la backup-file.json
python3 -m json.tool backup-file.json > /dev/null
```

### 2. Never Edit openclaw.json Manually
**Wrong:** `nano ~/.openclaw/openclaw.json`  
**Right:** Use Python/CLI tools that handle JSON safely

### 3. Never Add Unverified Config Keys
Check official docs or ask before adding ANY new configuration keys.

### 4. Never Enable Sandbox Without Backup
Sandbox mode can cascade auth failures. Always backup first and test in isolation.

### 5. All Providers Failing = Config Issue
If multiple model providers fail simultaneously, suspect recent config changes, not provider outages.

### 6. Prefix Auth Commands with Environment
```bash
source ~/.openclaw/.env && openclaw auth <command>
```

### 7. Anthropic 401 = Check auth-profiles.json
Don't read the file directly - use `openclaw status` or CLI tools.

### 8. tool_use without tool_result = Reset Session
Corrupted sessions need `/reset` to recover.

## Safe Backup Script

Use the provided backup script instead of manual file copying:

```bash
scripts/safe_backup.sh
```

## Cooldown Reset Script

When experiencing "all providers unavailable" errors despite valid credentials, the in-memory cooldown state may be stale. Use:

```bash
scripts/reset_cooldowns.sh
```

This clears expired cooldowns from auth-profiles.json.

**Note:** This is a workaround for a bug where in-memory cooldown state doesn't refresh when file timestamps expire.

## Config Validation

Before applying config changes:

```bash
scripts/config_validator.py ~/.openclaw/openclaw.json
```

## Recovery Procedures

When you break a rule, see `references/recovery.md` for step-by-step recovery procedures.

## Auth Troubleshooting

For auth issues, use the safe checker:

```bash
scripts/auth_checker.sh
```

**Never directly read auth-profiles.json** - use the checker script instead.