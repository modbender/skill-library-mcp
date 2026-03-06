# Local Configuration

Optional local settings for non-secret configuration. Copy the code block below to `~/.openclaw-cloud-backup.conf`.

> **Note:** Secrets (bucket, credentials) go in OpenClaw config at `skills.entries.cloud-backup.*` — see [SKILL.md](../SKILL.md) for setup.

## Config File

```bash
# ~/.openclaw-cloud-backup.conf
# Local settings for OpenClaw Cloud Backup

# -------- Local paths --------
SOURCE_ROOT="$HOME/.openclaw"
LOCAL_BACKUP_DIR="$HOME/openclaw-cloud-backups"
TMP_DIR="$HOME/.openclaw-cloud-backup/tmp"

# Backup object key prefix in cloud bucket.
# Per-device namespace so multiple machines can share one bucket.
PREFIX="openclaw-backups/$(hostname -s)/"

# -------- Behavior --------

# Upload to cloud after local backup?
UPLOAD=true

# Client-side encryption with GPG symmetric mode?
ENCRYPT=false

# -------- Retention --------
# cleanup command uses these rules to prune old backups.
RETENTION_COUNT=10
RETENTION_DAYS=30
```

## Settings Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `SOURCE_ROOT` | `~/.openclaw` | Directory to back up |
| `LOCAL_BACKUP_DIR` | `~/openclaw-cloud-backups` | Where local backups are stored |
| `TMP_DIR` | `~/.openclaw-cloud-backup/tmp` | Temp directory for operations |
| `PREFIX` | `openclaw-backups/<hostname>/` | S3 key prefix (allows multi-device buckets) |
| `UPLOAD` | `true` | Upload to cloud after local backup |
| `ENCRYPT` | `false` | Enable GPG encryption |
| `RETENTION_COUNT` | `10` | Keep at least N backups |
| `RETENTION_DAYS` | `30` | Delete backups older than N days |
