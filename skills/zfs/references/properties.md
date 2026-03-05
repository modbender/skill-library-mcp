# ZFS Property Reference

## Table of Contents
- [Pool Properties](#pool-properties)
- [Dataset Properties (Commonly Tuned)](#dataset-properties-commonly-tuned)
- [Compression Algorithms](#compression-algorithms)
- [Property Inheritance](#property-inheritance)

## Pool Properties

### Creation-Time (Immutable)

| Property | Values | Notes |
|----------|--------|-------|
| `ashift` | 9-16 (default: 0=auto) | Set to match physical sector size. Use `12` for 4K drives (most modern drives), `13` for 8K (some NVMe). Cannot be changed after pool creation. When in doubt, use `12`. |
| `feature@*` | `enabled`/`disabled` | Pool feature flags. Enable at creation for new features; cannot be disabled once active. |

### Runtime (Mutable)

| Property | Values | Notes |
|----------|--------|-------|
| `autoexpand` | `on`/`off` | Auto-expand pool when larger disks replace smaller ones. |
| `autoreplace` | `on`/`off` | Auto-replace failed disks if new disk appears at same path. |
| `autotrim` | `on`/`off` | Enable continuous TRIM for SSDs. Recommended `on` for SSD/NVMe pools. |
| `cachefile` | path/`none` | Location of pool cache file. Use `none` for pools that should not auto-import. |
| `failmode` | `wait`/`continue`/`panic` | Behavior on unrecoverable I/O failure. `wait` is safest for data integrity. |
| `listsnapshots` | `on`/`off` | Show snapshots in `zfs list` by default. |
| `multihost` | `on`/`off` | Multihost protection (requires hostid). Use for shared storage. |

## Dataset Properties (Commonly Tuned)

### Storage Behavior

| Property | Values | Default | Notes |
|----------|--------|---------|-------|
| `recordsize` | 4K-16M | `128K` | Match to workload I/O size. See workload-tuning.md for guidance. |
| `compression` | see below | `off` | Almost always set to `lz4` or `zstd`. There is virtually no reason to leave compression off. |
| `dedup` | `on`/`off`/`verify`/`skein`/`sha512` | `off` | Requires ~5GB RAM per 1TB of data. Rarely recommended — see workload-tuning.md. |
| `copies` | 1-3 | `1` | Store N copies of each block. Does NOT replace redundant vdevs. |
| `quota` | size/`none` | `none` | Hard limit on dataset + descendants space usage. |
| `reservation` | size/`none` | `none` | Guaranteed space allocation from pool. |
| `refquota` | size/`none` | `none` | Hard limit on dataset only (excludes snapshots/descendants). |
| `refreservation` | size/`none` | `none` | Guaranteed space for dataset only. |
| `volblocksize` | 4K-128K | `16K` | Block size for zvols. Set at creation, immutable. |

### Access & Mounting

| Property | Values | Default | Notes |
|----------|--------|---------|-------|
| `mountpoint` | path/`none`/`legacy` | inherited | Where dataset mounts. `legacy` for /etc/fstab management. |
| `canmount` | `on`/`off`/`noauto` | `on` | Whether dataset can be mounted. `noauto` = manual mount only. |
| `readonly` | `on`/`off` | `off` | Prevent writes to dataset. |
| `atime` | `on`/`off` | `on` | Track file access times. Set `off` for performance on most workloads. |
| `relatime` | `on`/`off` | `off` | Only update atime if mtime/ctime changed or atime > 24h old. Good compromise. |
| `xattr` | `on`/`off`/`sa` | `on` | Extended attributes. `sa` (system attribute) is faster on Linux. |
| `dnodesize` | `legacy`/`auto`/`1k`-`16k` | `legacy` | Larger dnodes improve metadata-heavy workloads. `auto` recommended if pool feature is enabled. |

### Snapshots & Replication

| Property | Values | Default | Notes |
|----------|--------|---------|-------|
| `snapdir` | `visible`/`hidden` | `hidden` | Whether `.zfs/snapshot` is visible in directory listings. |
| `sync` | `standard`/`always`/`disabled` | `standard` | `disabled` risks data loss on power failure. Never use in production. |

### Encryption

| Property | Values | Default | Notes |
|----------|--------|---------|-------|
| `encryption` | `off`/`aes-256-ccm`/`aes-256-gcm` | `off` | Set at creation. `aes-256-gcm` recommended. Cannot encrypt existing dataset. |
| `keyformat` | `passphrase`/`raw`/`hex` | - | Key format for encrypted datasets. |
| `keylocation` | `prompt`/`file:///path` | `prompt` | Where to find the encryption key. |
| `pbkdf2iters` | integer | `350000` | PBKDF2 iterations for passphrase-based keys. Higher = slower brute force. |

## Compression Algorithms

| Algorithm | Speed | Ratio | When to Use |
|-----------|-------|-------|-------------|
| `lz4` | Fastest | Good | **Default recommendation.** Negligible CPU cost, good compression. |
| `zstd` | Fast | Better | Good for general use when slightly more CPU is acceptable. |
| `zstd-N` (1-19) | Varies | Varies | `zstd-3` is a good balance. Higher N = slower but better ratio. |
| `gzip-N` (1-9) | Slow | Best | Legacy. Prefer `zstd` for similar ratios with better speed. |
| `lzjb` | Fast | Poor | Legacy. Use `lz4` instead. |
| `zle` | Fastest | Minimal | Only compresses runs of zeros. Niche use. |

## Property Inheritance

ZFS properties inherit from parent to child datasets unless explicitly set:

```
tank                    compression=lz4    (set locally)
  tank/data             compression=lz4    (inherited from tank)
    tank/data/db        compression=zstd   (set locally, overrides)
    tank/data/logs      compression=lz4    (inherited from tank)
```

Check inheritance with:
```bash
zfs get -s local,inherited compression tank/data/db
```

Reset to inherited value:
```bash
zfs inherit compression tank/data/logs
```
