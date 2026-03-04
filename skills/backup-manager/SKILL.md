# Backup Manager

Automated backups for your files, databases, and configurations. Local, network, or cloud storage.

**Category:** home, security
**API Key Required:** No (unless using cloud storage)

## What It Does

Sets up and manages automated backups using rsync, cron, and optional cloud sync (rclone). Back up important files to another drive, NAS, or cloud provider (Google Drive, S3, Dropbox). Your agent handles scheduling, monitoring, and restoration.

## Setup

### Install dependencies
```bash
sudo apt install rsync -y
# For cloud backups:
sudo apt install rclone -y
```

## Agent Commands

### Simple backup (local to local)
```bash
# Backup home directory to external drive
rsync -avh --progress /home/USER/ /mnt/backup/home/ --delete --exclude='.cache' --exclude='node_modules' --exclude='.local/share/Trash'
```

### Backup to another machine (SSH)
```bash
rsync -avhz --progress /home/USER/ user@BACKUP_SERVER:/backups/$(hostname)/ --delete
```

### Create a backup script
```bash
cat > ~/backup.sh << 'EOF'
#!/bin/bash
TIMESTAMP=$(date +%Y-%m-%d_%H%M)
BACKUP_DIR="/mnt/backup"
LOG="/var/log/backup.log"

echo "[$TIMESTAMP] Backup starting..." >> $LOG

# Backup home directory
rsync -avh --delete \
  --exclude='.cache' \
  --exclude='node_modules' \
  --exclude='.local/share/Trash' \
  --exclude='*.tmp' \
  /home/ $BACKUP_DIR/home/ 2>&1 >> $LOG

# Backup system configs
rsync -avh /etc/ $BACKUP_DIR/etc/ 2>&1 >> $LOG

echo "[$TIMESTAMP] Backup complete." >> $LOG
EOF
chmod +x ~/backup.sh
```

### Schedule automatic backups
```bash
# Daily at 2am
(crontab -l 2>/dev/null; echo "0 2 * * * /home/USER/backup.sh") | crontab -
```

### Cloud backup with rclone

```bash
# Configure (interactive, one-time)
rclone config

# Backup to Google Drive
rclone sync /home/USER/Documents remote:Backups/Documents --progress

# Backup to S3
rclone sync /home/USER/Documents s3:mybucket/backups/ --progress

# List configured remotes
rclone listremotes
```

### Database backup (PostgreSQL)
```bash
pg_dump DATABASE_NAME > /mnt/backup/db/$(date +%Y%m%d)_database.sql
```

### Database backup (MySQL)
```bash
mysqldump -u root DATABASE_NAME > /mnt/backup/db/$(date +%Y%m%d)_database.sql
```

### Check backup status
```bash
# Last backup time
ls -lht /mnt/backup/ | head -5

# Backup size
du -sh /mnt/backup/*/

# Check cron is set up
crontab -l | grep backup
```

### Compare backup with source
```bash
rsync -avhn --delete /home/USER/ /mnt/backup/home/ | head -20
# -n = dry run, shows what WOULD change
```

### Restore from backup
```bash
# Restore specific file
cp /mnt/backup/home/USER/Documents/important.doc /home/USER/Documents/

# Restore entire directory
rsync -avh /mnt/backup/home/USER/ /home/USER/ --dry-run
# Remove --dry-run when ready to actually restore
```

### Snapshot backup (with versions)
```bash
# Create timestamped snapshots using hard links (space efficient)
DEST="/mnt/backup/snapshots/$(date +%Y-%m-%d)"
LATEST="/mnt/backup/snapshots/latest"
rsync -avh --delete --link-dest=$LATEST /home/USER/ $DEST/
ln -snf $DEST $LATEST
```

### Check backup integrity
```bash
# Compare checksums
find /home/USER/Documents -type f -exec md5sum {} \; | sort > /tmp/source.md5
find /mnt/backup/home/USER/Documents -type f -exec md5sum {} \; | sort > /tmp/backup.md5
diff /tmp/source.md5 /tmp/backup.md5
```

### Clean old backups
```bash
# Remove snapshots older than 30 days
find /mnt/backup/snapshots/ -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \;
```

## The 3-2-1 Rule

For important data, follow 3-2-1:
- **3** copies of your data
- **2** different storage types (e.g. SSD + external drive)
- **1** off-site copy (cloud or remote server)

## Examples

**User:** "Back up my stuff"
→ Run rsync to backup destination, report what was copied

**User:** "Set up automatic daily backups"
→ Create backup script + cron job, confirm schedule

**User:** "When was my last backup?"
→ Check backup directory timestamps and cron logs

**User:** "I accidentally deleted a file"
→ Find it in the backup, restore it

## Constraints

- rsync --delete removes files from backup that no longer exist in source — be careful
- First backup takes longest (copies everything), subsequent are incremental
- Cloud backups depend on upload speed
- Always test restores — a backup you can't restore is worthless
- Database backups should happen before file backups (consistency)
