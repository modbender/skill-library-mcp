# ZFS Replication Guide

## Table of Contents
- [Snapshot Fundamentals](#snapshot-fundamentals)
- [Local Snapshot Management](#local-snapshot-management)
- [zfs send/recv Basics](#zfs-sendrecv-basics)
- [Remote Replication over SSH](#remote-replication-over-ssh)
- [Incremental Replication](#incremental-replication)
- [Encrypted Send](#encrypted-send)
- [Automated Replication](#automated-replication)
- [Production Distributed Replication](#production-distributed-replication)
- [Snapshot Rotation Policies](#snapshot-rotation-policies)

## Snapshot Fundamentals

Snapshots are instant, zero-cost at creation, and grow only as data changes.

```bash
# Create a snapshot
zfs snapshot tank/data@2024-01-15_daily

# Create recursive snapshot (all child datasets)
zfs snapshot -r tank@2024-01-15_daily

# List snapshots
zfs list -t snapshot -o name,used,refer -s creation

# Access snapshot contents (read-only)
ls /tank/data/.zfs/snapshot/2024-01-15_daily/

# Rollback to snapshot (destroys changes since snapshot)
zfs rollback tank/data@2024-01-15_daily

# Rollback to non-latest snapshot (destroys intermediate snapshots)
zfs rollback -r tank/data@2024-01-10_daily
```

## Local Snapshot Management

```bash
# Clone a snapshot (writable copy, shares blocks via CoW)
zfs clone tank/data@snap1 tank/data-clone

# Promote clone to independent dataset (swap parent/child relationship)
zfs promote tank/data-clone

# Diff between snapshots
zfs diff tank/data@snap1 tank/data@snap2

# Destroy a snapshot
zfs destroy tank/data@old-snap

# Destroy range of snapshots
zfs destroy tank/data@snap1%snap5
```

## zfs send/recv Basics

```bash
# Full send to a file (backup)
zfs send tank/data@snap1 > /backup/data-snap1.zfs

# Full send to another local pool
zfs send tank/data@snap1 | zfs recv backup/data

# Send with properties preserved
zfs send -p tank/data@snap1 | zfs recv backup/data

# Send recursively (all child datasets and their snapshots)
zfs send -R tank@snap1 | zfs recv -d backup/tank

# Receive with force (overwrite existing dataset)
zfs send tank/data@snap1 | zfs recv -F backup/data
```

### Send Flags

| Flag | Purpose |
|------|---------|
| `-p` | Send properties (compression, quota, etc.) |
| `-R` | Recursive: send all descendants and snapshots |
| `-c` | Send compressed (keep blocks in compressed form) |
| `-w` | Raw send (preserves encryption — required for encrypted datasets) |
| `-L` | Allow large blocks (>128K recordsize) |
| `-e` | Generate more compact stream |
| `-v` | Verbose: show progress |
| `-n` | Dry run: estimate stream size |
| `-i` | Incremental from snapshot |
| `-I` | Incremental with all intermediate snapshots |

## Remote Replication over SSH

```bash
# Send to remote host
zfs send tank/data@snap1 | ssh user@remote zfs recv backup/data

# With compression in transit (if not using -c flag)
zfs send tank/data@snap1 | ssh -c aes128-gcm@openssh.com user@remote zfs recv backup/data

# With progress monitoring (pv)
zfs send -v tank/data@snap1 | pv | ssh user@remote zfs recv backup/data

# With mbuffer for network buffering (reduces stalls)
zfs send tank/data@snap1 | mbuffer -s 128k -m 1G | ssh user@remote "mbuffer -s 128k -m 1G | zfs recv backup/data"
```

### SSH Optimization for Replication

```bash
# ~/.ssh/config for replication host
Host zfs-backup
    HostName backup.example.com
    User zfsrepl
    Compression no           # ZFS handles compression via -c flag
    Ciphers aes128-gcm@openssh.com  # Fastest modern cipher
    ControlMaster auto       # Connection multiplexing
    ControlPath /tmp/ssh-%r@%h:%p
    ControlPersist 600
```

## Incremental Replication

Incremental sends transmit only changed blocks between two snapshots.

```bash
# Initial full send
zfs send -R tank/data@monday | ssh remote zfs recv backup/data

# Incremental send (only changes between monday and tuesday)
zfs send -i tank/data@monday tank/data@tuesday | ssh remote zfs recv backup/data

# Incremental with all intermediate snapshots preserved
zfs send -I tank/data@monday tank/data@friday | ssh remote zfs recv backup/data
```

### Incremental Replication Workflow

1. Create initial snapshot and full send
2. For each subsequent replication:
   a. Create new snapshot on source
   b. Incremental send from last-sent snapshot to new snapshot
   c. Verify receipt on target
   d. Destroy old snapshots (keep at least the last-sent on both sides)

**Critical**: Both source and target must share a common snapshot. Never destroy the last-replicated snapshot on either side until a newer common snapshot exists.

## Encrypted Send

```bash
# Raw send preserves encryption (receiver does not need the key)
zfs send -w tank/encrypted@snap1 | ssh remote zfs recv backup/encrypted

# The remote side stores encrypted blocks — cannot read data without key
# Useful for offsite backup to untrusted storage

# To receive and re-encrypt with a different key, send decrypted:
zfs send tank/encrypted@snap1 | ssh remote zfs recv -o encryption=aes-256-gcm -o keyformat=passphrase backup/reencrypted
```

## Automated Replication

### Using syncoid (sanoid/syncoid suite)

The most common production replication tool. Install `sanoid` package.

```bash
# Basic sync (handles incremental automatically)
syncoid tank/data remote:backup/data

# Recursive sync
syncoid -r tank remote:backup/tank

# With encryption preservation
syncoid --sendoptions="w" tank/encrypted remote:backup/encrypted

# Cron job for hourly replication
0 * * * * /usr/sbin/syncoid -r tank remote:backup/tank --no-sync-snap 2>&1 | logger -t syncoid
```

### Using sanoid for Snapshot Policy

```ini
# /etc/sanoid/sanoid.conf
[tank/data]
    use_template = production
    recursive = yes

[template_production]
    hourly = 24
    daily = 30
    monthly = 12
    yearly = 2
    autosnap = yes
    autoprune = yes
```

```bash
# Run via cron every 15 minutes
*/15 * * * * /usr/sbin/sanoid --cron
```

## Production Distributed Replication

For production-grade distributed storage with data replication across multiple hosts:

### Architecture Pattern: Primary + Replicas

```
Primary Server (tank)
  ├── zfs send ──> Replica 1 (backup1/tank) [same site]
  └── zfs send ──> Replica 2 (backup2/tank) [remote site]
```

### Setup

**1. Dedicated replication user with minimal privileges:**

```bash
# On each replica host
useradd -m -s /bin/bash zfsrepl

# Grant only necessary ZFS permissions
zfs allow -u zfsrepl create,mount,receive,destroy,rollback,hold,release backup
```

**2. SSH key-based auth (no passphrase for automation):**

```bash
# On primary
ssh-keygen -t ed25519 -f /root/.ssh/zfsrepl_key -N ""
ssh-copy-id -i /root/.ssh/zfsrepl_key zfsrepl@replica1
ssh-copy-id -i /root/.ssh/zfsrepl_key zfsrepl@replica2
```

**3. Replication script with error handling:**

```bash
#!/bin/bash
# /usr/local/bin/zfs-replicate.sh
set -euo pipefail

DATASET="tank/data"
SNAP_PREFIX="repl"
REPLICAS=("zfsrepl@replica1:backup/data" "zfsrepl@replica2:backup/data")
SSH_KEY="/root/.ssh/zfsrepl_key"
SNAP="${DATASET}@${SNAP_PREFIX}_$(date +%Y%m%d_%H%M%S)"

# Create new snapshot
zfs snapshot -r "$SNAP"

for target in "${REPLICAS[@]}"; do
    IFS=':' read -r host dataset <<< "$target"

    # Find last common snapshot
    last_common=$(ssh -i "$SSH_KEY" "$host" \
        "zfs list -H -o name -t snapshot -r $dataset" 2>/dev/null | \
        grep "${SNAP_PREFIX}_" | tail -1 | awk -F@ '{print $2}')

    if [ -z "$last_common" ]; then
        echo "Initial full send to $host:$dataset"
        zfs send -Rw "$SNAP" | ssh -i "$SSH_KEY" "$host" "zfs recv -F $dataset"
    else
        echo "Incremental send to $host:$dataset from @$last_common"
        zfs send -RwI "@${last_common}" "$SNAP" | \
            ssh -i "$SSH_KEY" "$host" "zfs recv -F $dataset"
    fi
done

echo "Replication complete: $SNAP"
```

**4. Monitoring and alerting:**

```bash
# Verify replication is current (add to monitoring)
last_snap=$(ssh -i "$SSH_KEY" zfsrepl@replica1 \
    "zfs list -H -o name -t snapshot -r backup/data" | tail -1)
snap_time=$(echo "$last_snap" | grep -oP '\d{8}_\d{6}')
# Alert if last replication > threshold age
```

### Multi-Site Considerations

- Use `zfs send -c` to reduce bandwidth (send compressed blocks)
- Use `zfs send -w` for encrypted offsite replicas (zero-knowledge backup)
- Use `mbuffer` or `pv` to handle network latency
- Stagger replication schedules to avoid bandwidth contention
- Monitor replication lag as a key metric

## Snapshot Rotation Policies

### Simple Rotation Script

```bash
#!/bin/bash
# Keep last N snapshots per type
DATASET="tank/data"

# Destroy snapshots older than retention
zfs list -H -o name -t snapshot -r "$DATASET" | \
    grep "@daily_" | head -n -30 | xargs -rn1 zfs destroy

zfs list -H -o name -t snapshot -r "$DATASET" | \
    grep "@hourly_" | head -n -24 | xargs -rn1 zfs destroy
```

### Naming Convention

Use consistent, sortable snapshot names:
```
tank/data@hourly_2024-01-15_14:00
tank/data@daily_2024-01-15
tank/data@monthly_2024-01
tank/data@repl_20240115_140000  (replication snapshots)
```
