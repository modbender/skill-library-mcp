#!/bin/bash
# Doc Cleanup Script - Ubuntu 24.04

set -euo pipefail

echo "=== Doc Cleanup Starting ==="

# 1. Empty Trash
trash-empty 2>/dev/null || true
echo "Trash emptied"

# 2. Apt Clean
apt autoremove -y
apt autoclean
apt clean
echo "Apt cleaned"

# 3. Temp Files
rm -rf /tmp/* /var/tmp/*
echo "Temp files cleared"

# 4. Logs
journalctl --vacuum-time=2weeks --vacuum-size=100M
echo "Logs vacuumed"

# 5. Cache Drop
sync; echo 3 > /proc/sys/vm/drop_caches
echo "Caches dropped"

# 6. Report
df -h | head -10
free -h
echo "=== Cleanup Complete ==="
