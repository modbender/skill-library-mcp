#!/bin/bash
# =============================================================================
# ESXi VM Disk Resize — Online grow for Debian VMs with simple partitioning
# Usage: ./esxi-vm-resize-disk.sh <vm-name> <new-size-gb>
#
# What it does:
# 1. Expand the virtual disk via govc
# 2. SSH into the VM and grow partition + filesystem online
# 3. Works with MBR (p1=root, p2=extended, p5=swap) layout from preseed
#
# Requirements: govc, sshpass, cloud-guest-utils on target VM
# =============================================================================
set -euo pipefail

VM_NAME="${1:?Usage: $0 <vm-name> <new-size-gb>}"
NEW_SIZE="${2:?Usage: $0 <vm-name> <new-size-gb>}G"
SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"

ESXI_HOST="${ESXI_HOST:?Set ESXI_HOST to your ESXi IP}"
ESXI_PASS="${ESXI_PASS:?Set ESXI_PASS to your ESXi root password}"
export GOVC_URL="https://${ESXI_HOST}"
export GOVC_USERNAME="${ESXI_USER:-root}"
export GOVC_PASSWORD="${ESXI_PASS}"
export GOVC_INSECURE=true

# Get VM IP and disk name
VM_IP=$(govc vm.ip "$VM_NAME")
DISK_NAME=$(govc device.ls -vm "$VM_NAME" | grep VirtualDisk | awk '{print $1}')

if [ -z "$VM_IP" ] || [ -z "$DISK_NAME" ]; then
    echo "❌ Could not get VM IP or disk name"
    exit 1
fi

# VM password (from environment)
VM_PASS="${VM_PASS:?Set VM_PASS to the VM root password}"

echo "============================================"
echo "  Disk Resize: $VM_NAME"
echo "============================================"
echo "  IP:       $VM_IP"
echo "  Disk:     $DISK_NAME → $NEW_SIZE"
echo "============================================"

# Step 1: Expand virtual disk (works online for SCSI/NVMe)
echo "[1/3] Expanding virtual disk..."
govc vm.disk.change -vm "$VM_NAME" -disk.name "$DISK_NAME" -size "$NEW_SIZE"

# Step 2: Rescan disk in guest
echo "[2/3] Rescanning disk in guest..."
SSHPASS="$VM_PASS" sshpass -e ssh -o StrictHostKeyChecking=no "root@$VM_IP" bash -s <<'REMOTE'
set -e

# Find the root disk device
ROOT_DEV=$(findmnt -no SOURCE / | sed 's/[0-9]*$//')
ROOT_PART=$(findmnt -no SOURCE /)
PART_NUM=$(echo "$ROOT_PART" | grep -o '[0-9]*$')
DISK=$(echo "$ROOT_DEV" | sed 's/p$//')  # handle nvme0n1p → nvme0n1

echo "  Root: $ROOT_PART on $DISK partition $PART_NUM"

# Rescan for NVMe
if [[ "$DISK" == *nvme* ]]; then
    echo 1 > /sys/class/block/$(basename $DISK)/device/rescan_controller 2>/dev/null || true
fi

# Check if growpart is available
if ! command -v growpart &>/dev/null; then
    echo "  Installing cloud-guest-utils..."
    DEBIAN_FRONTEND=noninteractive apt-get install -y cloud-guest-utils >/dev/null 2>&1
fi

# Grow partition
echo "  Growing partition..."
growpart "$DISK" "$PART_NUM" || echo "  (already at max size)"

# Resize filesystem
echo "  Resizing filesystem..."
FS_TYPE=$(findmnt -no FSTYPE /)
case "$FS_TYPE" in
    ext4|ext3|ext2) resize2fs "$ROOT_PART" ;;
    xfs) xfs_growfs / ;;
    *) echo "  ⚠️  Unknown filesystem: $FS_TYPE" ;;
esac
REMOTE

# Step 3: Verify
echo "[3/3] Verifying..."
SSHPASS="$VM_PASS" sshpass -e ssh -o StrictHostKeyChecking=no "root@$VM_IP" "df -h / | tail -1"

echo "============================================"
echo "  ✅ Resize complete!"
echo "============================================"
