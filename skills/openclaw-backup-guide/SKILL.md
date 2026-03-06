---
name: Backup Automation Skill
description: Automated backup system for OpenClaw workspaces with database, NAS,
  and GitHub integration.
---

# Backup Automation Skill

Automated backup system for OpenClaw workspaces with database, NAS, and GitHub integration.

## What It Does

This skill provides automated hourly backups:
- **Database backup** to SQLite
- **NAS sync** via rsync
- **Git commit + push** to GitHub for version control

Perfect for maintaining workspace continuity and disaster recovery.

## Setup

### 1. Configure NAS Target (Optional)

Edit `backup-nas.sh` to set your NAS mount point:

```bash
NAS_PATH="/path/to/your/nas/backup"
```

If you don't use NAS, the script will skip that step gracefully.

### 2. Set Up Cron Job

Add to your crontab for hourly backups:

```bash
0 * * * * cd /path/to/workspace && node scripts/backup-db.js; bash scripts/backup-nas.sh; git add -A && git commit -m "Hourly backup: $(date '+%Y-%m-%d %H:%M %Z')" && git push origin main
```

**OR** use OpenClaw's built-in cron:

```bash
openclaw cron add --schedule "0 * * * *" --task "Hourly workspace backup" --command "cd /path/to/workspace && node scripts/backup-db.js && bash scripts/backup-nas.sh && git add -A && git commit -m 'Auto backup' && git push"
```

### 3. GitHub Authentication

Ensure you have:
- Git configured with your credentials
- GitHub SSH key added (or HTTPS token set)
- Remote origin configured: `git remote -v`

## Usage

### Manual Backup

```bash
cd /path/to/your/workspace
node backup-db.js
bash backup-nas.sh
git add -A && git commit -m "Manual backup" && git push
```

### Check Backup Status

```bash
# Check last backup commit
git log --oneline -1

# Check database backup
ls -lh workspace.db*

# Check NAS sync
ls -lh /your/nas/path/
```

## Files

- `backup-db.js` - Node.js script for database backup
- `backup-nas.sh` - Bash script for NAS rsync
- `skill.json` - Skill metadata
- `SKILL.md` - This file (usage guide)
- `README.md` - Overview

## Requirements

- **Node.js** 18+ (for backup-db.js)
- **Git** (for version control)
- **rsync** (for NAS sync, optional)
- **GitHub** repository (for remote storage)

## Customization

### Change Backup Frequency

Edit the cron schedule:
- Every hour: `0 * * * *`
- Every 30 min: `*/30 * * * *`
- Every 6 hours: `0 */6 * * *`
- Daily at 3am: `0 3 * * *`

### Add Custom Backup Logic

Extend `backup-db.js` with additional backup targets:

```javascript
// Add S3 sync, Dropbox upload, etc.
```

### Backup Retention

To limit backup history in Git:

```bash
# Squash old commits periodically
git rebase -i HEAD~100
```

## Troubleshooting

**Backup not running:**
- Check cron logs: `tail -f /var/log/cron`
- Verify script permissions: `chmod +x backup-nas.sh`

**Git push fails:**
- Verify SSH key: `ssh -T git@github.com`
- Check remote: `git remote -v`

**NAS sync issues:**
- Test rsync manually: `rsync -av /source /destination`
- Check mount: `mount | grep nas`

## Security Notes

- Database backups may contain sensitive data
- Ensure your GitHub repo is **private** if storing sensitive info
- NAS should be on a secure network (Tailscale/VPN recommended)
- Consider encryption for sensitive backups

## License

MIT - Use freely, modify as needed.

## Author

Created by Lance (lancelot3777) for OpenClaw workspace management.
