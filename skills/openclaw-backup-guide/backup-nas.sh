#!/bin/bash
# Backup full workspace to Synology NAS → Cloud Sync → Google Drive
# NAS: 192.168.4.95 (DS1812+), user: lstone
# Path: /volume2/SecondVolume/Lance/Backup/Orbital/

NAS="lstone@192.168.4.95"
DEST="/volume2/SecondVolume/Lance/Backup/Orbital"
SRC="/home/killingtime/hub-local"

# Use tar to bundle everything (excluding node_modules/.next/.git) and scp it over
# This gives us a full snapshot without needing rsync
tar czf /tmp/orbital-backup.tar.gz \
  --exclude='node_modules' \
  --exclude='.next' \
  --exclude='.git' \
  -C "$SRC" . 2>/dev/null

scp -O /tmp/orbital-backup.tar.gz "$NAS:$DEST/orbital-workspace.tar.gz" 2>/dev/null

# Also send the clean DB copy separately for easy access
scp -O "$SRC/projects/the-orbital/data/orbital-backup.db" "$NAS:$DEST/orbital-backup.db" 2>/dev/null

rm -f /tmp/orbital-backup.tar.gz

echo "✅ NAS backup complete"
