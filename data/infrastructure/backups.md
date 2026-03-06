# Backup Strategies

## The 3-2-1 Rule

- **3** copies of data
- **2** different storage types
- **1** offsite

Minimum viable: Primary + Daily backup to S3/B2

---

## Database Backups

### PostgreSQL to S3

```bash
#!/bin/bash
# backup-db.sh
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BUCKET="s3://myapp-backups/postgres"

# Dump
pg_dump -Fc $DATABASE_URL > /tmp/backup_$TIMESTAMP.dump

# Upload
aws s3 cp /tmp/backup_$TIMESTAMP.dump $BUCKET/

# Cleanup local
rm /tmp/backup_$TIMESTAMP.dump

# Cleanup old backups (keep 30 days)
aws s3 ls $BUCKET/ | while read -r line; do
  createDate=$(echo $line | awk '{print $1" "$2}')
  createDate=$(date -d "$createDate" +%s)
  olderThan=$(date -d "30 days ago" +%s)
  if [[ $createDate -lt $olderThan ]]; then
    fileName=$(echo $line | awk '{print $4}')
    aws s3 rm $BUCKET/$fileName
  fi
done
```

### Cron Setup
```bash
# Daily at 3 AM
0 3 * * * /opt/scripts/backup-db.sh >> /var/log/backup.log 2>&1
```

### Restore
```bash
# Download
aws s3 cp s3://myapp-backups/postgres/backup_20240115.dump /tmp/

# Restore
pg_restore -d $DATABASE_URL /tmp/backup_20240115.dump
```

---

## Volume/Disk Backups

### Hetzner Snapshots
```bash
# Create snapshot
hcloud server create-image --type snapshot myapp \
  --description "Pre-migration $(date +%Y%m%d)"

# List snapshots
hcloud image list --type snapshot

# Restore (create new server from snapshot)
hcloud server create --name myapp-restored \
  --image snapshot-123456 --type cx22
```

### AWS EBS Snapshots
```bash
# Create
aws ec2 create-snapshot --volume-id vol-xxx \
  --description "Daily backup"

# Automate with Data Lifecycle Manager (DLM)
# Creates snapshots on schedule, manages retention
```

---

## Application Data Backups

### Docker Volumes
```bash
# Backup volume to tarball
docker run --rm -v myapp_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/data_backup.tar.gz /data

# Restore
docker run --rm -v myapp_data:/data -v $(pwd):/backup \
  alpine sh -c "cd /data && tar xzf /backup/data_backup.tar.gz --strip 1"
```

---

## Storage Options

| Provider | Cost | Best For |
|----------|------|----------|
| Backblaze B2 | $0.005/GB/mo | Cheapest, S3-compatible |
| AWS S3 | $0.023/GB/mo | Integration with AWS |
| Hetzner Storage Box | €3.81/1TB | EU data residency |
| rsync.net | $0.015/GB/mo | ZFS snapshots, SSH access |

---

## Backup Verification

**Critical:** Untested backups are not backups.

Monthly checklist:
1. Download random backup
2. Restore to test environment
3. Verify data integrity
4. Document restore time (RTO)

```bash
# Quick verify pg_dump integrity
pg_restore --list backup.dump > /dev/null && echo "Valid" || echo "Corrupt"
```

---

## Disaster Recovery Checklist

Before disaster:
- [ ] Automated backups running
- [ ] Backups verified monthly
- [ ] Restore procedure documented
- [ ] Restore tested quarterly
- [ ] Offsite copy exists

During disaster:
1. Don't panic
2. Assess what's lost
3. Find latest valid backup
4. Provision new infrastructure
5. Restore from backup
6. Update DNS
7. Verify functionality
8. Post-mortem
