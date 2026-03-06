---
name: fullbackup
description: Create a full local backup of the OpenClaw workspace and configuration using the existing backup-local.sh script. Use for /fullbackup in Telegram or when the user asks for a complete local backup.
---

# Full Backup (local archive)

## Overview
Run the local full-backup script and store the archive in `/root/.openclaw/backups`.

## Quick start
Run the bundled wrapper:
```bash
bash /root/.openclaw/workspace/skills/fullbackup/scripts/full-backup.sh
```

## Output
Print the archive path and size.

## Notes
- The backup script already applies safe exclusions (caches/logs).
- Do not delete older archives.
