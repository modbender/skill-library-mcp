---
name: backup-to-telnyx-storage
description: Backup and restore your OpenClaw workspace to Telnyx Storage. Simple CLI-based scripts with no external dependencies.
metadata: {"openclaw":{"emoji":"💾","requires":{"bins":["telnyx"],"env":["TELNYX_API_KEY"]},"primaryEnv":"TELNYX_API_KEY"}}
---

# Backup to Telnyx Storage

Backup and restore your OpenClaw workspace to Telnyx Storage (S3-compatible).

## Setup (One-Time)

```bash
# 1. Install Telnyx CLI (if not already)
npm install -g @telnyx/api-cli

# 2. Authenticate
telnyx auth setup
```

That's it. No boto3, no AWS credentials, no environment variables.

## Usage

### Backup

```bash
./backup.sh

# Output:
# 🔄 OpenClaw Backup → Telnyx Storage
# ========================================
# Creating archive: openclaw-backup-20260201-120000.tar.gz
#   + MEMORY.md
#   + SOUL.md
#   + memory/
# ✅ Backup complete: openclaw-backup/openclaw-backup-20260201-120000.tar.gz
```

Custom bucket and workspace:
```bash
./backup.sh my-bucket ~/my-workspace
```

Control backup retention (default: 48, ~24h of 30-min backups):
```bash
MAX_BACKUPS=100 ./backup.sh
```

### List Backups

```bash
./list.sh

# Output:
# 📋 Available Backups
# ========================================
# Bucket: openclaw-backup
#
#   • openclaw-backup-20260201-120000.tar.gz  1.2M  2/1/2026
#   • openclaw-backup-20260131-180000.tar.gz  1.1M  1/31/2026
```

### Restore

```bash
# Restore latest backup
./restore.sh latest

# Restore specific backup
./restore.sh openclaw-backup-20260201-120000.tar.gz

# Restore to different location
./restore.sh latest my-bucket ~/restored-workspace
```

## What Gets Backed Up

- `AGENTS.md`, `SOUL.md`, `USER.md`, `IDENTITY.md`, `TOOLS.md`
- `MEMORY.md`, `HEARTBEAT.md`, `GUARDRAILS.md`
- `memory/`, `knowledge/`, `scripts/`

## Scheduling

Automatic backups every 30 minutes:

```bash
crontab -e
# Add:
*/30 * * * * ~/skills/backup-to-telnyx-storage/backup.sh >> /tmp/backup.log 2>&1
```

## Pricing

Telnyx Storage: **$0.023/GB/month** — typical workspace costs pennies.

## Legacy Python Script

The original `backup.py` using boto3 is still available if you need AWS SDK compatibility:

```bash
pip install boto3
export TELNYX_API_KEY=KEYxxxxx
python3 backup.py
```

Note: The CLI-based scripts (`backup.sh`, `list.sh`, `restore.sh`) are recommended as they require no additional dependencies and provide full backup/list/restore functionality.
