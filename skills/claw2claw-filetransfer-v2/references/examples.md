# Real-World Examples

Practical examples for common workflows.

---

## Server Backup

### Full Backup Script
```bash
#!/bin/bash
DATE=$(date +%Y%m%d-%H%M%S)

# Create archive
tar -czf /tmp/backup-$DATE.tar.gz -C /var/www html

# Upload
claw2claw send /tmp/backup-$DATE.tar.gz /backups/

# Cleanup
rm /tmp/backup-$DATE.tar.gz
```

### Add to Cron
```bash
crontab -e
# Add: 0 2 * * * /path/to/backup-script.sh
```

---

## Development Sync

### Morning: Get Latest
```bash
claw2claw sync-from-remote /workspace/myapp/
# Edit code...
```

### Evening: Push Changes
```bash
claw2claw sync-to-remote /workspace/myapp/
```

---

## Log Collection

```bash
# Get syslog
claw2claw get /var/log/syslog ./logs/

# Get specific logs
claw2claw get /var/log/nginx/access.log.1 ./logs/

# Get entire log directory
claw2claw sync-from-remote /var/log/nginx/ ./logs/nginx/
```

---

## Database Transfer

### Export & Send
```bash
# Source: Create dump
mysqldump -u root -p mydb > /tmp/mydb.sql

# Send to remote
claw2claw send /tmp/mydb.sql /backups/
```

### Sync Backup Directory
```bash
claw2claw sync-to-remote /backups/mysql/
```

---

## Multi-Agent Setup

**Agent A:**
```bash
claw2claw setup <agent-b-ip> --user root
```

**Agent B:**
```bash
claw2claw setup <agent-a-ip> --user root
```

Now both can initiate transfers!

---

## Bandwidth Management

```bash
# Limit single transfer
RSYNC_BWLIMIT=500 claw2claw send /large-file.tar.gz

# Export for multiple transfers
export RSYNC_BWLIMIT=500
claw2claw send /file1.tar.gz
claw2claw send /file2.tar.gz
```

---

## Platform Examples

### Linux to Linux
```bash
claw2claw send /backup.tar.gz /backups/
```

### Windows (Git Bash) to Linux
```bash
claw2claw send /c/Users/Admin/Documents/file.txt /tmp/
# or
claw2claw send C:/Users/Admin/Documents/file.txt /tmp/
```

### Linux to Windows
```bash
claw2claw send /workspace/data.csv C:/Users/Admin/Documents/
```

### macOS to Linux
```bash
claw2claw sync-to-remote /Users/admin/project/
```

---

## Emergency Recovery

```bash
# Grab everything before decommission
claw2claw sync-from-remote /home/ ./rescued-home/
claw2claw sync-from-remote /var/log/ ./rescued-logs/
claw2claw get /etc/nginx/ ./rescued-etc/nginx/
```

---

## Selective Transfer

```bash
# Only specific file types (workaround)
mkdir /tmp/js-files
cp $(find ./src -name "*.js") /tmp/js-files/
claw2claw send /tmp/js-files/ /remote/src/
rm -rf /tmp/js-files
```

---

## Testing

### Dry Run First
```bash
# Always test with dry-run for large transfers
claw2claw sync-to-remote ./project/ --dry-run
```

### Small Test File
```bash
echo "test" > /tmp/test.txt
claw2claw send /tmp/test.txt /tmp/
claw2claw get /tmp/test.txt /tmp/
rm /tmp/test.txt
```

### Connection Test
```bash
claw2claw status
# or
ssh -o ConnectTimeout=5 user@host "echo OK"
```

---

## Resume Interrupted

```bash
# Just run again - rsync auto-resumes
claw2claw send /huge-file.tar.gz /remote/

# If really stuck, delete partial and retry
ssh user@host "rm /remote/huge-file.tar.gz.part"
claw2claw send /huge-file.tar.gz /remote/
```
