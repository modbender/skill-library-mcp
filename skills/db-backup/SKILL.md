---
description: Generate automated backup scripts with rotation for PostgreSQL, MySQL, SQLite, and MongoDB.
---

# DB Backup

Create automated database backup scripts with compression, rotation, and scheduling.

## Instructions

1. **Ask user for**: Database type, name(s), connection details, backup dir (default: `~/backups/db/`), retention (default: 7 days), schedule (default: daily 2 AM)

2. **Generate script** based on database type:

### PostgreSQL
```bash
#!/bin/bash
set -euo pipefail
BACKUP_DIR="${BACKUP_DIR:-$HOME/backups/db}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
TS=$(date +%Y%m%d_%H%M%S)
DB="DATABASE_NAME"
mkdir -p "$BACKUP_DIR" && chmod 700 "$BACKUP_DIR"
pg_dump -Fc "$DB" > "$BACKUP_DIR/${DB}_${TS}.dump"
chmod 600 "$BACKUP_DIR/${DB}_${TS}.dump"
find "$BACKUP_DIR" -name "${DB}_*.dump" -mtime +$RETENTION_DAYS -delete
echo "[$(date)] ✅ Backup: ${DB}_${TS}.dump"
```

### MySQL
```bash
#!/bin/bash
set -euo pipefail
BACKUP_DIR="${BACKUP_DIR:-$HOME/backups/db}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
TS=$(date +%Y%m%d_%H%M%S)
DB="DATABASE_NAME"
mkdir -p "$BACKUP_DIR" && chmod 700 "$BACKUP_DIR"
mysqldump --single-transaction "$DB" | gzip > "$BACKUP_DIR/${DB}_${TS}.sql.gz"
chmod 600 "$BACKUP_DIR/${DB}_${TS}.sql.gz"
find "$BACKUP_DIR" -name "${DB}_*.sql.gz" -mtime +$RETENTION_DAYS -delete
echo "[$(date)] ✅ Backup: ${DB}_${TS}.sql.gz"
```

### SQLite
```bash
#!/bin/bash
set -euo pipefail
BACKUP_DIR="${BACKUP_DIR:-$HOME/backups/db}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
TS=$(date +%Y%m%d_%H%M%S)
DB_FILE="PATH_TO_DB.sqlite"
DB_NAME=$(basename "$DB_FILE" .sqlite)
mkdir -p "$BACKUP_DIR" && chmod 700 "$BACKUP_DIR"
sqlite3 "$DB_FILE" ".backup '$BACKUP_DIR/${DB_NAME}_${TS}.sqlite'"
gzip "$BACKUP_DIR/${DB_NAME}_${TS}.sqlite"
chmod 600 "$BACKUP_DIR/${DB_NAME}_${TS}.sqlite.gz"
find "$BACKUP_DIR" -name "${DB_NAME}_*.sqlite.gz" -mtime +$RETENTION_DAYS -delete
echo "[$(date)] ✅ Backup: ${DB_NAME}_${TS}.sqlite.gz"
```

3. **Set up cron**:
   ```bash
   chmod +x backup.sh
   (crontab -l 2>/dev/null; echo "0 2 * * * /path/to/backup.sh >> /path/to/backup.log 2>&1") | crontab -
   ```

4. **Verify**: Run manually once and check output

## Security

- **NEVER hardcode passwords** — use `~/.pgpass` (PostgreSQL), `~/.my.cnf` (MySQL), or env vars
- Set `chmod 600` on all dump files, `chmod 700` on backup directory
- Add backup directory to `.gitignore`
- For remote storage: pipe to `aws s3 cp` or `rclone copy`

## Troubleshooting

- **"permission denied"**: Check DB user privileges and file permissions
- **"command not found"**: Install `postgresql-client`, `mysql-client`, or `sqlite3`
- **Disk full**: Check `df -h` before backup; add pre-check to script
- **Locked DB (SQLite)**: Ensure no write transactions during `.backup`

## Requirements

- Database client tools: `pg_dump`, `mysqldump`, `sqlite3`, or `mongodump`
- `gzip`, `find`, `crontab` (standard Unix)
- No API keys needed
