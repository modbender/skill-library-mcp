# ZFS Workload Tuning Guide

## Table of Contents
- [Production vs Testing Warning](#production-vs-testing-warning)
- [Recordsize by Workload](#recordsize-by-workload)
- [Compression Recommendations](#compression-recommendations)
- [Deduplication Guidance](#deduplication-guidance)
- [Special Vdev (Metadata/Small Blocks)](#special-vdev)
- [SLOG (ZIL) and L2ARC](#slog-and-l2arc)
- [ARC Tuning](#arc-tuning)
- [Pool Layout Recommendations](#pool-layout-recommendations)

## Production vs Testing Warning

**CRITICAL: Never use file-backed (loopback) pools in production.**

File-backed pools (`truncate -s 10G /path/file` + `zpool create tank /path/file`) are acceptable ONLY for:
- Learning ZFS commands
- Testing pool configurations
- CI/CD pipeline testing
- Development environments

File-backed pools in production **forfeit**:
- ZFS self-healing (checksums cannot detect underlying filesystem corruption)
- Predictable I/O performance (double filesystem overhead)
- Direct disk error detection (SMART, sector errors hidden by host filesystem)
- Write reliability (host filesystem may reorder writes, defeating ZIL guarantees)

**Always use real block devices for production:**
```bash
# Linux — use /dev/disk/by-id/ for stable device names
zpool create tank mirror \
  /dev/disk/by-id/scsi-SATA_WDC_WD40EFRX_WD-WCC4E1234567 \
  /dev/disk/by-id/scsi-SATA_WDC_WD40EFRX_WD-WCC4E7654321

# macOS — use /dev/diskN identifiers
zpool create tank mirror /dev/disk2 /dev/disk3
```

Use `/dev/disk/by-id/` on Linux (not `/dev/sdX`) because device letters can change across reboots.

## Recordsize by Workload

| Workload | Recordsize | Rationale |
|----------|-----------|-----------|
| PostgreSQL | `8K` | Matches PG page size. Set `full_page_writes=off` with ZFS CoW. |
| MySQL/InnoDB | `16K` | Matches InnoDB page size. Disable InnoDB doublewrite buffer. |
| MongoDB (WiredTiger) | `64K` | WiredTiger default block size. |
| SQLite | `64K` | Good balance for typical SQLite I/O. |
| VM disk images (zvol) | `64K` | Match guest filesystem block size or use volblocksize. |
| General file server / NAS | `128K` (default) | Good for mixed workloads with mostly sequential reads. |
| Media files (video/images) | `1M` | Large sequential I/O benefits from large records. |
| Backup target (zfs recv) | `1M` | Optimizes for sequential write throughput. |
| Torrents / download staging | `1M` | Large sequential writes. |
| Small files (source code, configs) | `64K`-`128K` | Default is fine; smaller recordsize wastes metadata overhead. |

```bash
# Set recordsize BEFORE writing data
zfs set recordsize=8K tank/postgres
```

## Compression Recommendations

**Rule: Always enable compression.** The CPU cost is negligible and even incompressible data has near-zero overhead with `lz4`.

| Workload | Algorithm | Notes |
|----------|-----------|-------|
| General / default | `lz4` | Best default. Near-zero CPU overhead. |
| NAS / file server | `zstd` or `lz4` | `zstd` for better ratio if CPU is available. |
| Databases | `lz4` | Minimize latency. |
| Log files | `zstd-3` to `zstd-7` | Logs compress extremely well. |
| Backup datasets | `zstd-3` | Good ratio for archival. |
| Already-compressed media | `lz4` | `lz4` detects incompressible data and skips quickly. |

## Deduplication Guidance

**Default recommendation: Do NOT enable dedup.** Dedup is almost never worth it.

### Why Dedup Is Usually Wrong

- Requires ~320 bytes of RAM per block in the Dedup Table (DDT)
- At 128K recordsize: ~5 GB RAM per 1 TB of data
- At 8K recordsize: ~80 GB RAM per 1 TB of data
- If DDT spills to disk, performance collapses catastrophically
- Cannot easily disable once enabled (existing data stays deduped)

### When Dedup Might Be Appropriate

- VM storage with many near-identical VMs
- Backup targets with many identical files across backups
- AND sufficient RAM (calculate DDT size first)
- AND you have verified dedup ratio with: `zdb -S poolname`

### Better Alternatives

- Block cloning (OpenZFS 2.2+): `cp --reflink=always` — free dedup at file level
- Compression: Gets most of the space savings with none of the RAM cost

## Special Vdev

A special vdev stores metadata and optionally small file blocks on fast storage (NVMe) while bulk data stays on slower disks.

```bash
# Add special vdev (mirrored NVMe for safety)
zpool add tank special mirror /dev/disk/by-id/nvme-device1 /dev/disk/by-id/nvme-device2

# Direct small blocks to special vdev
zfs set special_small_blocks=64K tank
```

**When to use**: Pools with spinning disks where metadata operations (ls, find, stat) are slow. Dramatically improves random I/O and metadata-heavy workloads.

**Warning**: Loss of special vdev = loss of pool. Always mirror special vdevs.

## SLOG and L2ARC

### SLOG (Separate ZFS Intent Log)

Accelerates synchronous writes by placing the ZIL on fast, durable storage.

```bash
zpool add tank log mirror /dev/disk/by-id/nvme-log1 /dev/disk/by-id/nvme-log2
```

**When to use**: Workloads with heavy sync writes (NFS, databases, ESXi).
**Requirements**: Must have power-loss protection (enterprise NVMe/SSD with capacitor-backed cache).
**Sizing**: 5-10 GB is typically sufficient; larger is wasted.

### L2ARC (Level 2 Adaptive Replacement Cache)

Extends ARC read cache to SSD/NVMe.

```bash
zpool add tank cache /dev/disk/by-id/nvme-cache1
```

**When to use**: Working set exceeds available RAM AND random read heavy.
**Trade-off**: Consumes ~70 bytes of ARC RAM per L2ARC block for index. On RAM-constrained systems, L2ARC can make things worse.
**Skip if**: Sufficient RAM for working set or sequential workloads.

## ARC Tuning

### Linux

```bash
# Check current ARC size
cat /proc/spl/kstat/zfs/arcstats | grep -E "^c_|^size"

# Set max ARC size (e.g., 32 GB on 64 GB system)
echo 34359738368 > /sys/module/zfs/parameters/zfs_arc_max

# Persist across reboots — add to /etc/modprobe.d/zfs.conf:
options zfs zfs_arc_max=34359738368
```

### Guidelines

| System Role | ARC Size Recommendation |
|-------------|------------------------|
| Dedicated NAS/storage | 50-75% of RAM |
| Database server | 25-50% of RAM (leave room for DB cache) |
| General server | 25-50% of RAM |
| VM host | 15-25% of RAM (VMs need their own RAM) |
| Desktop | 25-50% of RAM |

ARC is released under memory pressure, but setting an explicit max prevents ZFS from competing with application caches.

## Pool Layout Recommendations

### Redundancy Levels

| Layout | Min Disks | Usable Space | Fault Tolerance | Use Case |
|--------|-----------|-------------|-----------------|----------|
| `mirror` | 2 | 50% | 1 disk per mirror | Best performance, good for small arrays |
| `raidz1` | 3+ | N-1 disks | 1 disk | Small arrays, non-critical data |
| `raidz2` | 4+ | N-2 disks | 2 disks | **Recommended minimum for production** |
| `raidz3` | 5+ | N-3 disks | 3 disks | Large arrays with long resilver times |
| `draid` | many | varies | configurable | Very large pools (50+ disks) for faster resilver |

### Production Guidelines

- **Never use raidz1 with drives > 2TB** — resilver time during single-disk failure leaves pool vulnerable.
- **Prefer mirrors for databases** — best random I/O performance and fastest resilver.
- **Use raidz2 as minimum for data you care about.**
- **Keep vdev sizes uniform** — mismatched vdevs cause uneven data distribution.
- **Wide vdevs (>8 disks) hurt performance** — prefer more narrow vdevs. E.g., 3x 4-disk raidz1 outperforms 1x 12-disk raidz1 for random I/O.
