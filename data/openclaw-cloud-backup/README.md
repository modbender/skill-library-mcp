# OpenClaw Cloud Backup

Back up your OpenClaw configuration to local archives and any S3-compatible storage.

**Supported providers:** AWS S3, Cloudflare R2, Backblaze B2, MinIO, DigitalOcean Spaces, any S3-compatible endpoint.

## Installation

Install as an OpenClaw skill from [ClawHub](https://clawhub.com) or copy the `clawhub-bundle/` contents to your skills directory.

## Prerequisites

- `bash`, `tar`, `jq`
- `aws` CLI v2 ([install guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html))
- `gpg` (optional, for encryption)

## Quick Start

### 1. Configure credentials

Secrets are stored in OpenClaw config (`~/.openclaw/openclaw.json`).

**Ask your OpenClaw agent:**
> "Set up cloud-backup with bucket `my-bucket`, region `us-east-1`, access key `AKIA...` and secret `...`"

**Or manually:**
```bash
openclaw config patch 'skills.entries.cloud-backup.bucket="my-bucket"'
openclaw config patch 'skills.entries.cloud-backup.region="us-east-1"'
openclaw config patch 'skills.entries.cloud-backup.awsAccessKeyId="AKIA..."'
openclaw config patch 'skills.entries.cloud-backup.awsSecretAccessKey="..."'

# For non-AWS providers:
openclaw config patch 'skills.entries.cloud-backup.endpoint="https://..."'
```

### 2. Verify setup

```bash
bash scripts/openclaw-cloud-backup.sh setup
bash scripts/openclaw-cloud-backup.sh status
```

### 3. Create first backup

```bash
bash scripts/openclaw-cloud-backup.sh backup full
bash scripts/openclaw-cloud-backup.sh list
```

## Commands

| Command | Description |
|---------|-------------|
| `setup` | Show config guide and test connection |
| `status` | Print config and dependency status |
| `backup [full\|skills\|settings]` | Create and upload backup |
| `list` | List cloud backups |
| `restore <name> [--dry-run] [--yes]` | Download and restore |
| `cleanup` | Prune old backups |
| `help` | Show usage |

## Configuration

### Secrets (OpenClaw config)

Stored at `skills.entries.cloud-backup.*`:

| Key | Description |
|-----|-------------|
| `bucket` | S3 bucket name (required) |
| `region` | AWS region (default: us-east-1) |
| `endpoint` | Custom endpoint for non-AWS providers |
| `awsAccessKeyId` | Access key ID |
| `awsSecretAccessKey` | Secret access key |
| `awsProfile` | Named AWS profile (alternative to keys) |
| `gpgPassphrase` | For client-side encryption |

### Local settings (optional)

See `references/local-config.md` for non-secret settings. Copy the config block to `~/.openclaw-cloud-backup.conf`:

| Setting | Default | Description |
|---------|---------|-------------|
| `SOURCE_ROOT` | `~/.openclaw` | Directory to back up |
| `LOCAL_BACKUP_DIR` | `~/openclaw-cloud-backups` | Local archive storage |
| `PREFIX` | `openclaw-backups/<hostname>/` | S3 key prefix |
| `UPLOAD` | `true` | Upload to cloud after backup |
| `ENCRYPT` | `false` | GPG encrypt archives |
| `RETENTION_COUNT` | `10` | Keep N most recent backups |
| `RETENTION_DAYS` | `30` | Delete backups older than N days |

### Config priority

1. Environment variables (CI/automation)
2. OpenClaw config (recommended)
3. Local config file (fallback)

## Provider Setup

See `references/provider-setup.md` for provider-specific instructions.

## Scheduling

Use OpenClaw's native cron — ask your agent:

> "Schedule daily cloud backups at 2am"

> "Run weekly backup cleanup on Sundays"

The agent creates isolated cron jobs that invoke the backup script automatically.

## Security

- Keep bucket private with least-privilege credentials
- Secrets in OpenClaw config are protected by file permissions
- Archive paths are validated against traversal attacks
- Always `restore --dry-run` before extracting
- See `references/security-troubleshooting.md` for full guidance

## Repository Layout

```
├── SKILL.md                 # Skill definition (bundled)
├── README.md                # This file (GitHub only)
├── references/local-config.md    # Non-secret config template
├── scripts/
│   └── openclaw-cloud-backup.sh
├── references/
│   ├── provider-setup.md
│   └── security-troubleshooting.md
├── publish-for-clawhub.sh   # Build ClawHub bundle
└── clawhub-bundle/          # Generated upload folder
```

## ClawHub Publishing

```bash
bash publish-for-clawhub.sh
# Upload ./clawhub-bundle/ to ClawHub
```

## License

MIT
