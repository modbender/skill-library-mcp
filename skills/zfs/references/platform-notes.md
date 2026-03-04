# ZFS Platform Notes: Linux vs macOS

## Table of Contents
- [Feature Parity Summary](#feature-parity-summary)
- [Installation](#installation)
- [Device Naming](#device-naming)
- [Kernel Integration](#kernel-integration)
- [Key Behavioral Differences](#key-behavioral-differences)
- [macOS-Specific Caveats](#macos-specific-caveats)
- [Linux-Specific Notes](#linux-specific-notes)

## Feature Parity Summary

Both Linux and macOS run OpenZFS, but Linux is the primary development target and gets features first.

| Feature | Linux | macOS |
|---------|-------|-------|
| Core ZFS (pools, datasets, snapshots) | Full | Full |
| Encryption (native) | Full | Full |
| zfs send/recv | Full | Full |
| Block cloning (OpenZFS 2.2+) | Yes | Depends on version |
| dRAID | Yes | Limited |
| Kernel module | DKMS/kmod | kext (kernel extension) |
| TRIM/autotrim | Full | Check version support |
| Hibernation/suspend | Requires care | Not supported with ZFS root |
| Root-on-ZFS | Supported | Not supported |

## Installation

### Linux (Ubuntu/Debian)

```bash
apt install zfsutils-linux

# Verify
zfs version
modinfo zfs | grep version
```

### Linux (RHEL/Fedora)

```bash
# Add ZFS repo
dnf install https://zfsonlinux.org/epel/zfs-release-2-3.el9.noarch.rpm
dnf install zfs

# Load module
modprobe zfs
```

### macOS

Install via Homebrew (OpenZFS on OS X):
```bash
brew install --cask openzfs
```

Or download from https://openzfsonosx.org

**Note**: macOS kernel extensions require security approval in System Preferences > Security & Privacy after installation. On Apple Silicon, may require reduced security mode.

## Device Naming

### Linux

```bash
# ALWAYS use persistent names for production pools
# /dev/disk/by-id/    — most stable, includes serial numbers
# /dev/disk/by-path/  — stable by controller/port
# /dev/disk/by-uuid/  — partition UUID (less useful for ZFS)

# Example
zpool create tank mirror \
  /dev/disk/by-id/scsi-SATA_WDC_WD40EFRX_WD-WCC4E1234567 \
  /dev/disk/by-id/scsi-SATA_WDC_WD40EFRX_WD-WCC4E7654321

# AVOID /dev/sdX — letters can change between reboots
```

### macOS

```bash
# List disks
diskutil list

# Use /dev/diskN (whole disk) or /dev/diskNsP (partition)
zpool create tank mirror /dev/disk2 /dev/disk3

# Device names are generally stable on macOS but can change
# if USB/Thunderbolt devices are reconnected in different ports
```

## Kernel Integration

### Linux

- ZFS is a kernel module (DKMS or pre-built kmod)
- Automatically loads on boot if pools exist
- Must rebuild module on kernel updates (DKMS handles automatically)
- ARC tuning via `/sys/module/zfs/parameters/` and `/etc/modprobe.d/zfs.conf`

```bash
# Check module parameters
cat /sys/module/zfs/parameters/zfs_arc_max

# Persist parameters
echo 'options zfs zfs_arc_max=34359738368' > /etc/modprobe.d/zfs.conf
```

### macOS

- ZFS is a kernel extension (kext) — requires security approval
- Apple Silicon Macs may need reduced security boot policy
- macOS updates can break the kext — check compatibility before OS updates
- ARC tuning via sysctl:

```bash
# Check ARC size
sysctl kstat.zfs.misc.arcstats.size

# Set max ARC (not persistent — add to startup script)
sudo sysctl -w kstat.zfs.misc.arcstats.c_max=8589934592
```

## Key Behavioral Differences

### Extended Attributes

```bash
# Linux: use system attribute mode for best performance
zfs set xattr=sa tank/data

# macOS: xattr=sa may not be supported or behave differently
# Default xattr=on is typically fine
```

### Mount Behavior

```bash
# Linux: ZFS mounts datasets automatically at boot via zfs-mount.service
systemctl enable zfs-mount.service
systemctl enable zfs-import-cache.service

# macOS: ZFS mounts via LaunchDaemon, generally automatic
# Check: launchctl list | grep zfs
```

### Case Sensitivity

```bash
# Linux: default is case-sensitive (matches ext4/xfs behavior)
zfs create -o casesensitivity=sensitive tank/data

# macOS: HFS+/APFS is case-insensitive by default
# For compatibility with macOS apps, consider:
zfs create -o casesensitivity=insensitive tank/data
# But: case-insensitive cannot be changed after creation
```

### ACL Support

```bash
# Linux: POSIX ACLs and NFSv4 ACLs supported
zfs set acltype=posixacl tank/data  # Most common on Linux

# macOS: NFSv4 ACLs
zfs set acltype=nfsv4 tank/data
```

## macOS-Specific Caveats

1. **No root-on-ZFS**: macOS must boot from APFS. ZFS is for additional data volumes only.
2. **OS updates may break ZFS**: Always check OpenZFS macOS compatibility before major macOS updates.
3. **Apple Silicon considerations**: Kernel extension loading is more restricted. May need to allow in recovery mode.
4. **Spotlight indexing**: Disable on ZFS volumes to avoid performance issues:
   ```bash
   mdutil -i off /Volumes/tank
   ```
5. **Time Machine**: ZFS is not natively supported as a Time Machine target. Use ZFS snapshots instead.
6. **Sleep/wake**: Pools on external drives may not survive sleep/wake cycles cleanly. Export before sleep or disable sleep.
7. **Fusion Drive conflicts**: Do not mix ZFS with Apple Fusion Drive configurations.

## Linux-Specific Notes

1. **DKMS rebuilds**: Kernel updates trigger automatic DKMS rebuild. If it fails, ZFS won't load after reboot. Pin kernel or verify DKMS success.
2. **systemd integration**: Use `zfs-import-cache.service` and `zfs-mount.service` for proper boot ordering.
3. **Swap on ZFS**: Possible via zvol but not recommended. Deadlock risk under memory pressure. Use a dedicated partition.
4. **Docker on ZFS**: Docker has a native ZFS storage driver. Set in `/etc/docker/daemon.json`:
   ```json
   { "storage-driver": "zfs" }
   ```
5. **Proxmox/LXC**: Native ZFS support for VM storage and container datasets.
6. **NFS export**: Export ZFS datasets directly:
   ```bash
   zfs set sharenfs="rw=@10.0.0.0/24,no_root_squash" tank/shared
   ```
