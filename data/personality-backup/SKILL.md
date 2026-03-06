---
name: personality-backup
description: Create encrypted backups of agent personality files, memory, config, secrets, and projects. Use when the agent needs to set up, run, or manage automated backups of its workspace and identity files. Supports configurable backup targets, AES-256 encryption via 7-zip, and delivery via email (SMTP) or local storage.
---

# Personality Backup

Encrypted backup of agent identity, memory, and workspace data.

## Prerequisites

- `p7zip-full` (7-zip CLI)
- Python 3 with `smtplib` (for email delivery)
- A backup password stored in a file

## Configuration

Create `~/.openclaw/secrets/backup-config.json`:

```json
{
  "password_file": "/home/jan/.openclaw/secrets/backup-password.txt",
  "password_field": "Password",
  "delivery": "email",
  "email": {
    "to": "user@example.com",
    "from": "agent@example.com",
    "smtp_host": "mail.example.com",
    "smtp_port": 465,
    "smtp_user": "agent@example.com",
    "smtp_pass_env": "BACKUP_SMTP_PASS"
  },
  "local": {
    "dir": "/home/jan/backups"
  },
  "workspace": "/home/jan/.openclaw/workspace",
  "secrets_dir": "/home/jan/.openclaw/secrets",
  "config_file": "/home/jan/.openclaw/openclaw.json",
  "agent_name": "Agent",
  "agent_emoji": "",
  "personality_files": ["SOUL.md", "IDENTITY.md", "USER.md", "AGENTS.md", "MEMORY.md", "TOOLS.md"],
  "backup_memory": true,
  "backup_secrets": true,
  "backup_config": true,
  "backup_projects": true,
  "backup_scripts": true,
  "project_excludes": ["node_modules", ".git", "__pycache__", "*.mp4", "*.mp3", "*.wav"],
  "generate_restore_guide": true
}
```

All fields have sensible defaults. Only `password_file` and delivery settings are required.

### Password File Format

The password file should contain a line: `Password: YOUR_SECRET_KEY`

Or set `password_field` to `null` and the entire file content is used as the password.

## Usage

### Run a backup

```bash
bash scripts/backup.sh /path/to/backup-config.json
```

### Set up daily cron

```bash
echo "0 3 * * * bash $(pwd)/scripts/backup.sh /path/to/backup-config.json" | crontab -
```

### Delivery Methods

- **email** — Sends encrypted archive as email attachment via SMTP
- **local** — Saves archive to a local directory

SMTP password: set via the environment variable named in `smtp_pass_env`, or put it directly in `smtp_pass` (less secure).

## Restore

The backup includes a generated `RESTORE.md` with step-by-step instructions for restoring onto a fresh OpenClaw installation. The restore guide is customized with the agent's name and configuration.
