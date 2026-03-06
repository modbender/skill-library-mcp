#!/bin/bash
# Automatic IAP configuration backup with change history
# Usage: ./scripts/auto-backup.sh <cluster-name> <vc-ip> [password]

set -e

CLUSTER_NAME=${1:-"office-iap"}
VC_IP=${2:-"192.168.20.56"}
SSH_PASSWORD=${3:-""}

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="${BACKUP_DIR}/${TIMESTAMP}"

echo "💾 Automatic IAP Configuration Backup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Cluster: ${CLUSTER_NAME}"
echo "VC: ${VC_IP}"
echo "Timestamp: ${TIMESTAMP}"
echo "Backup Path: ${BACKUP_PATH}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Create backup directory
mkdir -p "${BACKUP_PATH}"

# Build snapshot command
SNAPSHOT_CMD="iapctl snapshot-cmd --cluster ${CLUSTER_NAME} --vc ${VC_IP} --out ${BACKUP_PATH}"

# Add password if provided
if [ -n "${SSH_PASSWORD}" ]; then
    SNAPSHOT_CMD="${SNAPSHOT_CMD} --ssh-password ${SSH_PASSWORD}"
fi

# Take full snapshot
echo "📸 Taking full configuration snapshot..."
${SNAPSHOT_CMD}

if [ ! -f "${BACKUP_PATH}/result.json" ]; then
    echo "❌ Snapshot failed!"
    exit 1
fi

# Copy running-config to dated backup
cp "${BACKUP_PATH}/raw/show_running-config.txt" "${BACKUP_PATH}/running-config-${TIMESTAMP}.txt"

# Create backup metadata
cat > "${BACKUP_PATH}/backup-info.json" << EOF
{
  "cluster": "${CLUSTER_NAME}",
  "vc": "${VC_IP}",
  "timestamp": "${TIMESTAMP}",
  "timestamp_iso": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "backup_type": "full_snapshot",
  "files": [
    {
      "name": "show_running-config.txt",
      "description": "Full running configuration"
    },
    {
      "name": "show_version.txt",
      "description": "IAP version and model info"
    },
    {
      "name": "show_wlan.txt",
      "description": "WLAN configuration"
    },
    {
      "name": "show_ap_database.txt",
      "description": "AP database and cluster info"
    },
    {
      "name": "show_user-table.txt",
      "description": "Connected clients"
    },
    {
      "name": "show_interface.txt",
      "description": "Network interface status"
    },
    {
      "name": "show_radio.txt",
      "description": "Radio configuration and status"
    }
  ]
}
EOF

# Create latest symlink
rm -f "${BACKUP_DIR}/latest"
ln -s "${TIMESTAMP}" "${BACKUP_DIR}/latest"

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Backup completed successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📁 Backup location: ${BACKUP_PATH}"
echo ""
echo "📦 Backup artifacts:"
ls -lh "${BACKUP_PATH}/raw/"
echo ""
echo "📄 Latest backup: ${BACKUP_DIR}/latest -> ${TIMESTAMP}"
echo ""

# Show backup history
echo "📊 Backup history:"
echo ""
ls -lht "${BACKUP_DIR}" | grep "^d" | head -10
echo ""

# Show configuration size
echo "📊 Configuration statistics:"
CONFIG_SIZE=$(wc -l "${BACKUP_PATH}/raw/show_running-config.txt" | awk '{print $1}')
AP_COUNT=$(grep -c "Name:" "${BACKUP_PATH}/raw/show_ap_database.txt" 2>/dev/null || echo "0")
CLIENT_COUNT=$(grep -c "^" "${BACKUP_PATH}/raw/show_user-table.txt" 2>/dev/null || echo "0")

echo "  - Configuration lines: ${CONFIG_SIZE}"
echo "  - APs in cluster: ${AP_COUNT}"
echo "  - Connected clients: ${CLIENT_COUNT}"
echo ""

# Create simple restore instruction
cat > "${BACKUP_PATH}/RESTORE.txt" << 'EOF'
===========================================
IAP Configuration Backup Restore Guide
===========================================

To restore from this backup:

Option 1: Full Configuration Restore
-----------------------------------
1. Access the IAP web interface at https://<vc-ip>
2. Navigate to Maintenance > Configuration Backup
3. Upload the file: raw/show_running-config.txt
4. Apply and restart the cluster

Option 2: Manual CLI Restore
-----------------------------
1. SSH to the virtual controller:
   ssh admin@<vc-ip>

2. Enter configuration mode:
   configure terminal

3. Copy and paste the contents of: raw/show_running-config.txt

4. Save configuration:
   write memory

Option 3: iapctl Apply (Recommended)
------------------------------------
1. Use iapctl to apply the configuration:
   iapctl diff-cmd \
     --cluster <cluster-name> \
     --vc <vc-ip> \
     --in ./changes/restore.json \
     --out ./restore-diff

2. Review and apply changes:
   iapctl apply-cmd \
     --cluster <cluster-name> \
     --vc <vc-ip> \
     --change-id restore_<timestamp> \
     --in ./restore-diff/commands.json \
     --out ./restore-apply

===========================================
Backup Metadata
===========================================
EOF

cat "${BACKUP_PATH}/backup-info.json" >> "${BACKUP_PATH}/RESTORE.txt"

echo "📖 Restore instructions: ${BACKUP_PATH}/RESTORE.txt"
echo ""
echo "💡 View configuration: cat ${BACKUP_PATH}/raw/show_running-config.txt"
echo "💡 View backup info: cat ${BACKUP_PATH}/backup-info.json"
