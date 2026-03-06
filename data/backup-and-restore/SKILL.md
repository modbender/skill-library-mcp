---
name: backup
description: Backup, restore, disaster recovery, and migration for OpenClaw. Encrypts and stores ~/.openclaw/ locally and to cloud destinations (S3, R2, B2, GCS, Google Drive, rsync). Use when the user asks about backups, snapshots, disaster recovery, migration, or restoring OpenClaw from a backup.
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["gpg", "tar"], "optionalBins": ["jq", "aws", "gsutil", "gcloud", "b2", "rclone", "rsync"] },
        "env": ["BACKUP_PASSPHRASE", "BACKUP_ENCRYPT", "BACKUP_RETAIN_DAYS", "BACKUP_STOP_GATEWAY", "BACKUP_DIR"],
        "credentials": ["~/.openclaw/credentials/backup/backup-passphrase"],
        "optionalCredentials": ["~/.openclaw/credentials/backup/aws-credentials", "~/.openclaw/credentials/backup/r2-credentials", "~/.openclaw/credentials/backup/b2-credentials", "~/.openclaw/credentials/backup/gcs-key.json", "~/.openclaw/credentials/backup/rclone.conf"],
      },
  }
---

# Backup Skill

Backup and restore your entire OpenClaw installation — config, credentials, workspace, memory, and skills.

## Requirements

**Required:** `gpg`, `tar` (typically pre-installed on Linux)

**Optional** (for cloud uploads): `jq`, `aws` (S3/R2), `gsutil`/`gcloud` (GCS), `b2` (Backblaze), `rclone` (Google Drive), `rsync`

**Environment variables:** `BACKUP_PASSPHRASE`, `BACKUP_ENCRYPT`, `BACKUP_RETAIN_DAYS`, `BACKUP_STOP_GATEWAY`, `BACKUP_DIR`

**Credential files** (created during setup, stored at `~/.openclaw/credentials/backup/`):
- `backup-passphrase` — required for encrypted full backups
- `aws-credentials`, `r2-credentials`, `b2-credentials`, `gcs-key.json`, `rclone.conf` — optional, per cloud provider

## Quick Start

```bash
# Run a backup now — creates TWO files: full (encrypted) + workspace-only
~/.openclaw/workspace/skills/backup/scripts/backup.sh

# Upload both backups to configured cloud destinations
~/.openclaw/workspace/skills/backup/scripts/upload.sh

# Full restore (same environment / disaster recovery)
~/.openclaw/workspace/skills/backup/scripts/restore.sh ~/backups/openclaw/openclaw-myhost-20260215-full.tar.gz.gpg

# Workspace-only restore (any environment — just the agent's brain)
~/.openclaw/workspace/skills/backup/scripts/restore.sh ~/backups/openclaw/openclaw-myhost-20260215-workspace.tar.gz
```

## Interactive Setup

For guided setup, read `references/setup-guide.md` and follow the conversational flow with the user. This walks through encryption, backup mode, schedule, and cloud destination configuration.

## Manual Usage

### backup.sh — Create local backups

Every run produces **two files**:

1. **Full backup** (`*-full.tar.gz.gpg`) — everything including credentials, encrypted. For disaster recovery on the same or similar environment.
2. **Workspace backup** (`*-workspace.tar.gz.gpg`) — just `~/.openclaw/workspace/` (memory, skills, files), encrypted. Safe to restore on any environment without affecting gateway config. This is the agent's brain.

```bash
# Default: creates both files
./scripts/backup.sh

# Skip gateway stop/restart (for testing)
BACKUP_STOP_GATEWAY=false ./scripts/backup.sh
```

Saves to `~/backups/openclaw/`.

### upload.sh — Upload to cloud

```bash
# Upload latest local backup to all configured destinations
./scripts/upload.sh

# Upload a specific file
./scripts/upload.sh /path/to/backup.tar.gz.gpg
```

### restore.sh — Restore from backup

```bash
# Full restore (disaster recovery — replaces entire ~/.openclaw/)
./scripts/restore.sh openclaw-myhost-20260215-full.tar.gz.gpg

# Workspace-only restore (just the agent brain — keeps your config/credentials)
./scripts/restore.sh openclaw-myhost-20260215-workspace.tar.gz

# Extract only workspace from a full backup
./scripts/restore.sh --workspace-only openclaw-myhost-20260215-full.tar.gz.gpg

# From cloud
./scripts/restore.sh s3://mybucket/openclaw/openclaw-myhost-20260215-workspace.tar.gz
```

Automatically detects workspace backups by filename. Creates a safety copy before extracting.

**Note:** Workspace-only restores don't require a gateway restart — the agent picks up the new files on its next session. Full restores stop and replace the entire `~/.openclaw/` directory, so the gateway needs to be restarted afterward.

### test-backup.sh — Validate setup

```bash
./scripts/test-backup.sh
```

Creates a tiny test file, encrypts, uploads to all destinations, verifies, cleans up. Exit 0 = all good.

## Config Reference

Config lives at `~/.openclaw/workspace/skills/backup/config.json`:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `encrypt` | bool | `true` | AES-256 GPG symmetric encryption (for full backups) |
| `retainDays` | number | `30` | Auto-prune local backups older than this |
| `schedule` | string | `"daily"` | `daily`, `weekly`, or `manual` |
| `destinations` | array | `[]` | Cloud upload targets (see destinations.md) |

## Environment Variables

All settings can be overridden via env vars:

| Variable | Description |
|----------|-------------|
| `BACKUP_ENCRYPT` | `true` or `false` (for full backups) |
| `BACKUP_RETAIN_DAYS` | Number of days to keep old backups |
| `BACKUP_PASSPHRASE` | Encryption passphrase (or read from credentials file) |
| `BACKUP_STOP_GATEWAY` | `true` (default) or `false` |
| `BACKUP_DIR` | Override backup output directory |

## Credentials

Stored in `~/.openclaw/credentials/backup/`:

- `backup-passphrase` — encryption passphrase
- `aws-credentials` — for S3
- `r2-credentials` — for Cloudflare R2
- `b2-credentials` — for Backblaze B2
- `gcs-key.json` — Google Cloud Storage service account key
- `rclone.conf` — for Google Drive (rclone config)

## Security Notes

- Backups are encrypted by default with AES-256 (GPG symmetric)
- **Full-mode backups REQUIRE encryption** — the script will refuse to run without a passphrase when mode=full, since credentials would be stored in plaintext
- Workspace-only backups are also encrypted — they contain personal data (memory, notes, conversations)
- The passphrase file at `~/.openclaw/credentials/backup/backup-passphrase` should be readable only by the owner (mode 600)
- On first use, always walk the user through setting a passphrase (see `references/setup-guide.md`)
- If no passphrase is set, default to portable mode — never store credentials unencrypted
- Local backups are auto-pruned after the configured retention period
- Remote backups are never auto-deleted (see `references/destinations.md` for lifecycle guidance)
