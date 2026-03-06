---
name: synology-backup
description: "Backup and restore OpenClaw workspace, configs, and agent data to a Synology NAS via SMB. Use when: backing up workspace files, restoring from a snapshot, checking backup status/health, or setting up automated backups. Supports Tailscale for secure remote VPS-to-NAS connectivity."
---

# Synology Backup

Backup OpenClaw data to a Synology NAS over SMB. Designed for secure, automated daily snapshots with configurable retention.

## Setup

### 1. Network Connectivity

For VPS-to-NAS backups, use [Tailscale](https://tailscale.com) for secure connectivity without exposing SMB to the internet:

1. Install Tailscale on the Synology (Package Center → search "Tailscale")
2. Install Tailscale on the VPS — see [Tailscale's official install guide](https://tailscale.com/download) for your platform
3. Join both to the same tailnet
4. Use the Synology's Tailscale IP in config

For local network setups, use the NAS local IP directly.

### 2. Synology Preparation

1. Create a dedicated user on the Synology (e.g., `openclaw-backup`) with minimal permissions
2. Create or choose a shared folder (e.g., `backups`)
3. Grant the user read/write access to **only** that folder

### 3. Credentials File

Create an SMB credentials file with restricted permissions — **never store credentials in config or scripts**:

```bash
# Create the file and set permissions (replace placeholders with your values)
touch ~/.openclaw/.smb-credentials
chmod 600 ~/.openclaw/.smb-credentials
# Edit the file and add two lines:
#   username=<your-synology-user>
#   password=<your-synology-password>
nano ~/.openclaw/.smb-credentials
```

### 4. Configuration

Create `~/.openclaw/synology-backup.json`:

```json
{
  "host": "100.x.x.x",
  "share": "backups/openclaw",
  "mountPoint": "/mnt/synology",
  "credentialsFile": "~/.openclaw/.smb-credentials",
  "smbVersion": "3.0",
  "backupPaths": [
    "~/.openclaw/workspace",
    "~/.openclaw/openclaw.json",
    "~/.openclaw/cron",
    "~/.openclaw/agents"
  ],
  "includeSubAgentWorkspaces": true,
  "retention": 7,
  "schedule": "0 3 * * *"
}
```

**Note on sensitive files:** The `.env` file (containing API keys) is **not** included in the default backup paths. If you want to back it up, add `"~/.openclaw/.env"` to `backupPaths` — but ensure your Synology share has restricted access and the dedicated user has minimal permissions.

| Field | Description | Default |
|-------|-------------|---------|
| `host` | Synology IP (Tailscale or local) | required |
| `share` | SMB share path | required |
| `mountPoint` | Local mount point | `/mnt/synology` |
| `credentialsFile` | Path to SMB credentials file | required |
| `smbVersion` | SMB protocol version | `3.0` |
| `backupPaths` | Paths to backup | workspace + config |
| `includeSubAgentWorkspaces` | Auto-include `workspace-*` dirs | `true` |
| `retention` | Days of snapshots to keep | `7` |
| `schedule` | Cron expression (host timezone) | `0 3 * * *` |

### 5. Install Dependencies

```bash
apt-get install -y cifs-utils rsync
```

### 6. Mount Setup

For persistent mounts across reboots, add to `/etc/fstab`:

```
//<host>/<share> /mnt/synology cifs credentials=<credentials-file>,vers=3.0,_netdev,nofail 0 0
```

## Usage

### Backup Now

```bash
scripts/backup.sh
```

Runs an incremental backup. First run copies everything; subsequent runs only sync changes.

### Restore a Snapshot

```bash
scripts/restore.sh [date]
```

Restores from a specific date's snapshot (e.g., `2026-02-20`). Without a date, lists available snapshots.

### Check Status

```bash
scripts/status.sh
```

Shows last backup time, snapshot count, total size, and mount health.

## What Gets Backed Up

- `~/.openclaw/workspace/` — memory, SOUL, AGENTS, skills, all workspace files
- `~/.openclaw/workspace-*/` — all sub-agent workspaces (if enabled)
- `~/.openclaw/openclaw.json` — main config
- `~/.openclaw/cron/` — cron job definitions
- `~/.openclaw/agents/` — agent configurations
- `~/.openclaw/.env` — **opt-in only** (contains API keys — add to backupPaths manually if desired)

## Snapshot Structure

```
backups/
├── 2026-02-20/
│   ├── manifest.json
│   ├── workspace/
│   ├── workspace-email/
│   ├── workspace-news/
│   ├── agents/
│   ├── cron/
│   └── openclaw.json
├── 2026-02-19/
└── ...
```

## Security Notes

- **Credentials**: Always use a dedicated credentials file with restricted permissions (`chmod 600`). Never inline secrets in config files, scripts, or fstab.
- **Network**: Use Tailscale or a VPN for remote backups. Never expose SMB (port 445) to the public internet.
- **Sensitive data**: The `.env` file contains API keys and is excluded from default backup paths. Only include it if your NAS share is properly secured with restricted user permissions.
- **NAS user**: Create a dedicated Synology user with access to only the backup share — not an admin account.
- **Retention**: Old snapshots are pruned by moving them to the Synology trash (if supported) or deleting them. Increase retention for critical environments.
