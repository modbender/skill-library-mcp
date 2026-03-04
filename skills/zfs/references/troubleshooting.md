# ZFS Troubleshooting Guide

## Table of Contents
- [Pool Health Diagnostics](#pool-health-diagnostics)
- [Degraded Pool Recovery](#degraded-pool-recovery)
- [Scrub Errors](#scrub-errors)
- [Data Corruption](#data-corruption)
- [Performance Issues](#performance-issues)
- [Import/Export Problems](#importexport-problems)
- [Capacity Issues](#capacity-issues)
- [Common Mistakes](#common-mistakes)

## Pool Health Diagnostics

### Quick Status Check

```bash
# Overall pool status (most important command)
zpool status -v

# Pool I/O statistics
zpool iostat -v 5      # 5-second interval

# All pool details
zpool get all tank

# Dataset space usage
zfs list -o name,used,avail,refer,mountpoint -r tank
```

### Reading zpool status Output

```
pool: tank
state: DEGRADED
status: One or more devices has been removed by the FMA agent.
action: Online the device using 'zpool online' or replace the device with
        'zpool replace'.
scan: scrub repaired 0B in 03:45:12 with 0 errors on Sun Jan 14 03:45:12 2024
config:
    NAME                                    STATE     READ WRITE CKSUM
    tank                                    DEGRADED     0     0     0
      mirror-0                              DEGRADED     0     0     0
        /dev/disk/by-id/scsi-SATA_disk1     ONLINE       0     0     0
        /dev/disk/by-id/scsi-SATA_disk2     REMOVED      0     0     0
```

**Key columns**:
- `READ`: Read errors (correctable if redundancy exists)
- `WRITE`: Write errors (data may be lost)
- `CKSUM`: Checksum errors (data corruption detected)

**States**: `ONLINE` > `DEGRADED` > `FAULTED` > `REMOVED` > `UNAVAIL`

## Degraded Pool Recovery

### Replacing a Failed Drive

```bash
# 1. Identify the failed device
zpool status tank

# 2. If disk is still present but failing, offline it
zpool offline tank /dev/disk/by-id/old-disk

# 3. Physically replace the drive

# 4. Replace in ZFS (starts resilver)
zpool replace tank /dev/disk/by-id/old-disk /dev/disk/by-id/new-disk

# If old disk is already gone and new disk is in same slot:
zpool replace tank /dev/disk/by-id/old-disk /dev/disk/by-id/new-disk

# 5. Monitor resilver progress
zpool status tank
# Look for: "scan: resilver in progress"
```

### Resilver Time Expectations

- Mirrors: Fastest (only copies used blocks)
- raidz1/2/3: Slower (must recalculate parity across all disks in vdev)
- Larger pools take longer — this is why raidz1 with large disks is risky

### Clearing Transient Errors

```bash
# Clear error counters after resolving the cause
zpool clear tank

# Clear errors for a specific device
zpool clear tank /dev/disk/by-id/device
```

## Scrub Errors

### Understanding Scrub Results

```bash
# Start a scrub
zpool scrub tank

# Check scrub progress
zpool status tank | grep scan

# Possible outcomes:
# "scrub repaired 0B ... with 0 errors" — healthy
# "scrub repaired 512B ... with 0 errors" — corruption found and auto-fixed via redundancy
# "scrub ... with 5 errors" — corruption found, could NOT repair (insufficient redundancy)
```

### Responding to Scrub Errors

**If errors were repaired (0 errors, repaired > 0)**:
- ZFS self-healed using redundant copies
- Check SMART data on all disks: `smartctl -a /dev/sdX`
- If a disk shows SMART warnings, plan proactive replacement

**If errors were NOT repaired (errors > 0)**:
```bash
# List affected files
zpool status -v tank
# Shows files with permanent errors

# Check specific file integrity
sha256sum /path/to/affected/file

# Restore affected files from backup or snapshot
cp /tank/.zfs/snapshot/last-good/path/to/file /tank/path/to/file
```

### Scrub Schedule

Run scrubs regularly:
```bash
# Weekly scrub via cron (Sunday 2am)
0 2 * * 0 /sbin/zpool scrub tank

# Monthly for large pools (1st of month, 2am)
0 2 1 * * /sbin/zpool scrub tank
```

Frequency depends on pool size and risk tolerance. Weekly for critical data, monthly for large archival pools.

## Data Corruption

### When Checksums Detect Corruption

ZFS detects corruption via checksums. With redundancy (mirror/raidz), it auto-heals. Without:

```bash
# 1. Check pool status for error details
zpool status -v tank

# 2. If copies=2 or higher, ZFS may self-heal
# Otherwise, restore from snapshot:
zfs rollback tank/data@last-good-snapshot

# 3. Or restore specific files from snapshot
cp /tank/data/.zfs/snapshot/last-good/corrupted-file /tank/data/corrupted-file
```

### Preventing Data Loss

1. **Use redundancy** (mirror or raidz2 minimum)
2. **Use `copies=2`** for critical datasets without pool-level redundancy
3. **Regular scrubs** catch silent corruption early
4. **Offsite replication** is your last-resort recovery option
5. **ECC RAM** prevents bitflips from corrupting in-flight data (strongly recommended)

## Performance Issues

### Diagnosing Slow Performance

```bash
# Pool I/O stats (check for saturation)
zpool iostat -v 2

# ARC hit rate (should be > 90% for read-heavy workloads)
cat /proc/spl/kstat/zfs/arcstats | grep -E "^hits|^misses"

# TXG sync times (should be < 5 seconds normally)
# Long sync times indicate write bottleneck
cat /proc/spl/kstat/zfs/txgs

# Check for slow devices
zpool iostat -v -l 2   # latency mode
```

### Common Performance Fixes

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Slow reads, low ARC hit rate | Insufficient ARC | Increase `zfs_arc_max` |
| Slow sync writes | No SLOG, slow disks | Add SLOG (mirrored NVMe) |
| Slow metadata ops (ls, find) | Metadata on HDDs | Add special vdev |
| Pool 80%+ full | Fragmentation, CoW overhead | Free space or expand pool |
| High CKSUM errors | Failing disk | Replace disk |
| CPU-bound compression | Wrong compression algo | Switch to `lz4` |

### Fragmentation

ZFS performance degrades as pools fill past ~80% capacity. CoW requires free space to write new block copies.

```bash
# Check fragmentation
zpool list -o name,frag,cap

# If >80% full: add vdevs, delete old snapshots, or migrate data
```

## Import/Export Problems

```bash
# Export pool (safe unmount)
zpool export tank

# Import pool
zpool import tank

# List importable pools (scan for pools)
zpool import

# Import with alternate root
zpool import -R /mnt tank

# Force import (pool was not cleanly exported)
zpool import -f tank

# Import read-only (safe for forensics or recovery)
zpool import -o readonly=on tank

# Pool not found — search specific device directory
zpool import -d /dev/disk/by-id

# Import pool that was last used on different system
zpool import -f tank
```

### "Pool is busy" on Export

```bash
# Find processes using pool mountpoints
lsof +D /tank
fuser -m /tank

# Force export (may cause data loss if writes in flight)
zpool export -f tank
```

## Capacity Issues

### Finding Space

```bash
# Dataset and snapshot space usage
zfs list -o name,used,usedbysnapshots,usedbydataset -r tank -s used

# Largest snapshots
zfs list -t snapshot -o name,used -s used -r tank | tail -20

# Compressratio — see effective space savings
zfs get compressratio tank
```

### Expanding Pool

```bash
# Add a new vdev (CAUTION: must match existing topology for balance)
zpool add tank mirror /dev/disk/by-id/new-disk1 /dev/disk/by-id/new-disk2

# Replace disks with larger ones + autoexpand
zpool set autoexpand=on tank
# Replace each disk one at a time, wait for resilver between each
zpool replace tank /dev/disk/by-id/small-disk /dev/disk/by-id/large-disk
```

**Warning**: You cannot remove vdevs from a pool (except cache, log, and special vdevs on OpenZFS 2.0+). Plan pool topology carefully.

## Common Mistakes

| Mistake | Consequence | Prevention |
|---------|-------------|------------|
| File-backed pools in production | No self-healing, poor performance | Use real block devices |
| Using `/dev/sdX` names | Device letters change on reboot | Use `/dev/disk/by-id/` |
| raidz1 with large drives | Vulnerable during long resilver | Use raidz2 or mirrors |
| Mixing vdev types/sizes | Uneven data distribution | Keep vdevs uniform |
| Pool > 80% full | Severe performance degradation | Monitor capacity, plan expansion |
| Destroying common snapshot | Breaks incremental replication | Always verify before destroying |
| `sync=disabled` in production | Data loss on power failure | Leave `sync=standard` |
| Dedup without sufficient RAM | Catastrophic performance | Calculate DDT size first |
| No regular scrubs | Silent corruption goes undetected | Schedule weekly/monthly scrubs |
| No ECC RAM | Bitflips corrupt data undetected | Use ECC for production ZFS |
