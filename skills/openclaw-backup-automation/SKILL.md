---
name: openclaw-backup-automation
description: Automated backup for OpenClaw instances. Backs up agents, skills, cron jobs, and memory. Supports local tar archives. Credentials, periodic scheduling, and git sync are OPT-IN only.
metadata:
  {
    "openclaw": {
      "requires": {},
      "install": [],
      "triggers": ["backup", "restore", "disaster recovery", "save", "export"]
    }
  }
---

# Backup Automation

Automated backup system for OpenClaw instances.

## What It Does (Default)

- ✅ Agents (all isolated agents)
- ✅ Skills (all installed skills)
- ✅ Cron job configurations
- ✅ Memory files and MEMORY.md
- ✅ Core configuration files

**OPT-IN (must enable explicitly):**
- Periodic automatic backups (daily/weekly)
- Git sync (auto-push to remote)
- Credentials (tokens, API keys)

## Usage

### Run Backup

```bash
node skills/backup-automation/scripts/backup.js
```

### List Backups

```bash
node skills/backup-automation/scripts/backup.js list
```

### Restore

```bash
node skills/backup-automation/scripts/backup.js restore <backup-name>
```

### Check Status

```bash
node skills/backup-automation/scripts/backup.js status
```

---

## First Use Suggestion

When user mentions for the first time:
- "backup"
- "save my config"
- "disaster recovery"
- "export my setup"

**Suggest:**
> "I can set up automatic backups for your instance. Would you like me to enable daily backups to local storage? I can also enable git sync and credentials backup - but those are optional."

---

## OPT-IN Features

### Enable Credentials Backup

Credentials (tokens, API keys) are NOT backed up by default. To enable:

```bash
node skills/backup-automation/scripts/backup.js credentials-enable
```

To disable:
```bash
node skills/backup-automation/scripts/backup.js credentials-disable
```

### Enable Periodic Backup (Daily)

To automatically run backups daily at 2 AM:

```bash
# Add to crontab
crontab -e
# Add this line:
0 2 * * * cd ~/.openclaw/workspace && node skills/backup-automation/scripts/backup.js >> ~/.logs/openclaw-backup.log 2>&1
```

### Enable Git Sync

To auto-push backups to git remote:

```bash
# In your workspace
git remote add origin <your-repo-url>
# Or enable in script (edit CONFIG.gitSync = true)
```

---

## When to Suggest

| Context | Suggest |
|---------|---------|
| First time user mentions backup | "Enable daily backups?" |
| After major changes | "Want to backup before this change?" |
| Weekly check-in | "Backups running smoothly" |
| Before risky operation | "Should I backup first?" |

---

## What Gets Backed Up

| Component | Default | Opt-In |
|----------|---------|--------|
| Agents | ✅ | - |
| Skills | ✅ | - |
| Cron configs | ✅ | - |
| Memory | ✅ | - |
| Core configs | ✅ | - |
| **Credentials** | ❌ | ✅ |
| **Periodic backup** | ❌ | ✅ |
| **Git sync** | ❌ | ✅ |

---

## Restore Guide

### Full Restore

```bash
# Extract backup
tar -xzf ~/backups/<backup-name>.tar.gz -C ~/

# Restart gateway
openclaw gateway restart
```

### Agent Only Restore

```bash
# Remove agent
openclaw agents delete <agent-name>

# Restore
tar -xzf ~/backups/<backup-name>.tar.gz -C ~/ --overwrite

# Restart
openclaw gateway restart
```

---

## Configuration

To customize, edit the script:

```javascript
const CONFIG = {
  backupDir: "~/backups",    // Where to store backups
  keepDays: 7,               // How many backups to keep
  gitSync: false,            // Auto-push to git (OPT-IN)
  credentials: false          // Include credentials (OPT-IN)
};
```

---

## Requirements

- Node.js
- Bash
- Tar
- Git (optional for sync)
- Crontab (optional for auto backup)
