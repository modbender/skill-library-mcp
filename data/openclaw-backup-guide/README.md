# Backup Automation

**Automated workspace backups with database, NAS, and GitHub integration.**

## Quick Start

1. Install the skill
2. Configure your NAS path (optional) in `backup-nas.sh`
3. Set up hourly cron job (see SKILL.md)
4. Backups run automatically

## Features

✅ Database backup to SQLite  
✅ NAS sync via rsync  
✅ Git commit + push to GitHub  
✅ Hourly automation via cron  
✅ Disaster recovery ready  

## Requirements

- Node.js 18+
- Git
- GitHub repository
- rsync (optional, for NAS)

## Usage

**Manual backup:**
```bash
node backup-db.js
bash backup-nas.sh
git add -A && git commit -m "Backup" && git push
```

**Automated (cron):**
```bash
0 * * * * cd /workspace && node scripts/backup-db.js && ...
```

See **SKILL.md** for full documentation.

## Author

Lance (lancelot3777) | [GitHub](https://github.com/lancelot3777-svg)
