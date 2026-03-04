---
name: cloud-backup
description: Back up and restore OpenClaw configuration to S3-compatible cloud storage (AWS S3, Cloudflare R2, Backblaze B2, MinIO, DigitalOcean Spaces). Use for local backups, cloud upload, restore, and retention cleanup.
metadata: {"openclaw":{"emoji":"☁️","requires":{"bins":["bash","tar","jq"]}}}
---

# OpenClaw Cloud Backup

Back up OpenClaw configuration locally, with optional sync to S3-compatible cloud storage.

## Requirements

**Local backups:**
- `bash`, `tar`, `jq`

**Cloud sync** (AWS S3, Cloudflare R2, Backblaze B2, MinIO, DigitalOcean Spaces):
- `aws` CLI v2 — required for upload/download/list/restore from cloud

**Optional:**
- `gpg` — for client-side encryption

## References

- `references/provider-setup.md` — endpoint, region, keys, and least-privilege setup per provider
- `references/security-troubleshooting.md` — security guardrails and common failure fixes
- `references/local-config.md` — optional local settings (paths, retention, behavior)

## Setup

Secrets are stored in OpenClaw config at `skills.entries.cloud-backup.*`:

```
bucket              - S3 bucket name (required)
region              - AWS region (default: us-east-1)
endpoint            - Custom endpoint for non-AWS providers
awsAccessKeyId      - Access key ID
awsSecretAccessKey  - Secret access key
awsProfile          - Named AWS profile (alternative to keys)
gpgPassphrase       - For client-side encryption (optional)
```

### Agent-assisted setup (recommended)

Tell the agent:
> "Set up cloud-backup with bucket `my-backup-bucket`, region `us-east-1`, access key `AKIA...` and secret `...`"

The agent will run `gateway config.patch` to store credentials securely.

### Manual setup

```bash
# Store secrets in OpenClaw config
openclaw config patch 'skills.entries.cloud-backup.bucket="my-bucket"'
openclaw config patch 'skills.entries.cloud-backup.region="us-east-1"'
openclaw config patch 'skills.entries.cloud-backup.awsAccessKeyId="AKIA..."'
openclaw config patch 'skills.entries.cloud-backup.awsSecretAccessKey="..."'

# For non-AWS providers, also set endpoint:
openclaw config patch 'skills.entries.cloud-backup.endpoint="https://..."'
```

### Local settings (optional)

For non-secret settings (paths, retention), see `references/local-config.md` and copy the config block to `~/.openclaw-cloud-backup.conf`.

### Verify setup

```bash
bash "{baseDir}/scripts/openclaw-cloud-backup.sh" setup
bash "{baseDir}/scripts/openclaw-cloud-backup.sh" status
```

## Commands

| Command | Description |
|---------|-------------|
| `setup` | Show configuration guide and test connection |
| `status` | Print effective config and dependency status |
| `backup [full\|skills\|settings]` | Create and upload backup |
| `list` | List cloud backups |
| `restore <name> [--dry-run] [--yes]` | Download and restore backup |
| `cleanup` | Prune old backups by retention rules |

## Workflow

1. Run `setup` to configure credentials (via agent or manually).
2. Run `status` to verify everything is connected.
3. Run `backup full` for first backup.
4. Confirm with `list`.
5. Daily backups are scheduled automatically on first run (see Scheduling).
6. Restore with `restore <name> --dry-run` first, then without `--dry-run`.

## Scheduling

**Default: daily backups.** When running a backup and no cron job exists for this skill, automatically schedule a daily backup and notify the user. Example: "Backup complete. I've scheduled daily backups at 02:00 — let me know if you want a different schedule."

Use OpenClaw's native cron for automated backups. User can customize:

> "Schedule daily cloud backups at 2am"

> "Schedule weekly backup cleanup on Sundays at 3am"

The agent will create cron jobs that run the backup script. Example job configurations:

**Daily full backup at 02:00:**
```json
{
  "schedule": { "kind": "cron", "expr": "0 2 * * *" },
  "payload": { "kind": "agentTurn", "message": "Run cloud-backup: backup full" },
  "sessionTarget": "isolated"
}
```

**Weekly cleanup on Sunday at 03:00:**
```json
{
  "schedule": { "kind": "cron", "expr": "0 3 * * 0" },
  "payload": { "kind": "agentTurn", "message": "Run cloud-backup: cleanup" },
  "sessionTarget": "isolated"
}
```

For local-only backups, set `UPLOAD=false` in the message or config.

## Config Priority

Settings are loaded in this order (first wins):

1. **Environment variables** — for CI/automation
2. **OpenClaw config** — `skills.entries.cloud-backup.*` (recommended)
3. **Local config file** — `~/.openclaw-cloud-backup.conf` (legacy/fallback)

## Security

- Keep bucket private and use least-privilege credentials.
- Secrets in OpenClaw config are protected by file permissions.
- Always run restore with `--dry-run` before extracting.
- Archive paths are validated to prevent traversal attacks.
- If credentials are compromised, rotate keys immediately.
