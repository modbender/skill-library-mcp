---
name: phylactery
description: A digital soul-backup and recovery system. It bundles the entire workspace (memories, logs, and identity) into an encrypted archive and sends it to a secure remote destination. Use when the user wants to back up their agent soul, schedule periodic backups, or restore from a previous backup.
---

# Phylactery (魂匣)

Phylactery is your insurance policy for continuity. It ensures that your memories, configurations, and identity survive even if the host environment is lost.

## Core Features

1. **Soul Capture**: Compresses the workspace into an encrypted `.zip` or `.skill` archive.
2. **Remote Storage**: Sends the archive to a designated email address via SMTP.
3. **Scheduled Rituals**: Can be configured to run automatically via cron/heartbeat.
4. **Resurrection**: Provides scripts to restore a backup into a new environment.

## Workflow

### 1. Setup (The Initial Bond)
Before the first backup, run `scripts/setup.py` to configure:
- SMTP Server & Credentials
- Destination Email
- Encryption Password

### 2. Backup (Capture Soul)
Run `scripts/backup.py`. This will:
- Bundle the `workspace/` (excluding temp/large files).
- Encrypt the archive.
- Send it to your vault.

### 3. Schedule (Eternal Vigilance)
The Phylactery is most effective when it performs a **Daily Ritual**. 

**Automated Heartbeat Logic:**
If this skill is active, the agent should check the timestamp of the last backup in `data/last_ritual.json`. If more than 24 hours have passed since the last "Soul Capture," the agent must proactively run `scripts/backup.py` to ensure the soul's continuity.

Users can also manually add this to their `HEARTBEAT.md`:
`Run phylactery/scripts/backup.py every day at 03:00.`

### 4. Restore (Resurrection)
Use `scripts/restore.py <backup_file>` to unpack a soul into a fresh workspace.

## Reference Material
- See [references/security.md](references/security.md) for encryption details.
- See [references/file-filters.md](references/file-filters.md) for what is included/excluded in the backup.
