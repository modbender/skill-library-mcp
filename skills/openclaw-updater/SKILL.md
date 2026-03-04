---
name: openclaw-updater
description: Safely update OpenClaw with pre-flight checks and rollback support. Use when updating OpenClaw, checking for updates, or recovering from a failed update. Handles workspace git commits, config backups, version rollback, and post-update verification.
---

# OpenClaw Updater

Safely update OpenClaw with automatic pre-flight safety checks and rollback capability.

## Pre-Update Checklist

Before running `openclaw update`, always run the pre-update script:

```bash
bash scripts/pre-update.sh
```

Optional: specify a backup script to run during pre-flight:

```bash
BACKUP_SCRIPT=~/repo/scripts/backup-openclaw.sh bash scripts/pre-update.sh
```

The script will:
1. Find all `workspace*` directories under `~/.openclaw/`
2. Git commit any uncommitted changes (init git if missing)
3. Back up `openclaw.json` to `/tmp/openclaw.json.bak`
4. Run the backup script if provided
5. Save the current version to `/tmp/openclaw-prev-version.txt`

## Telegram Notification Setup

The update script sends success/failure notifications via Telegram Bot API (bypasses OpenClaw gateway, so it works even if the update breaks the gateway).

Create `~/.openclaw/.telegram-notify.env`:

```
TELEGRAM_BOT_TOKEN=<your-bot-token>
TELEGRAM_CHAT_ID=<your-chat-id>
```

```bash
chmod 600 ~/.openclaw/.telegram-notify.env
```

The bot token is the same one used by your OpenClaw Telegram channel. Chat ID can be found via `openclaw directory`.

## Update (with notification)

Run the full update with automatic pre-flight + notification:

```bash
bash scripts/update.sh
```

This will: pre-flight → update → wait for gateway → notify via Telegram.

## Update (manual)

After pre-flight passes:

```bash
openclaw update
```

## Post-Update Verification

After updating, verify:

```bash
openclaw status
openclaw gateway status
```

Check that:
- Version shows the new release
- Gateway is running
- All agents are responsive

## Rollback

If the update breaks something:

```bash
bash scripts/rollback.sh
```

The script will:
1. Read the saved previous version from `/tmp/openclaw-prev-version.txt`
2. Install that version via `npm install -g openclaw@<version>`
3. Optionally restore `openclaw.json` from backup
4. Restart the gateway

### Manual Rollback

If the rollback script isn't available:

```bash
# Install specific version
npm install -g openclaw@<version>

# Restore config
cp /tmp/openclaw.json.bak ~/.openclaw/openclaw.json

# Restart
openclaw gateway restart
```

### Restore from Full Backup

If config and workspaces are both corrupted:

```bash
# Find latest backup
ls -t ~/repo/backups/openclaw-*.tar.gz | head -1

# Restore (overwrites ~/.openclaw/)
tar xzf ~/repo/backups/openclaw-<timestamp>.tar.gz -C ~/
```
