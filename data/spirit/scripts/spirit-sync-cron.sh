#!/bin/bash
# SPIRIT Auto-Sync Cron Script
# Place in crontab or use with OpenClaw scheduled jobs

set -e

# Check if spirit is installed
if ! command -v spirit &> /dev/null; then
    echo "Error: spirit not found in PATH"
    exit 1
fi

# Check if initialized
if [ ! -d "$HOME/.spirit" ]; then
    echo "Error: SPIRIT not initialized. Run: spirit init"
    exit 1
fi

# Run sync with timestamp
LOG_FILE="$HOME/.spirit/.cron-sync.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting SPIRIT auto-sync..." >> "$LOG_FILE"

if spirit sync >> "$LOG_FILE" 2>&1; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✓ SPIRIT sync completed" >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✗ SPIRIT sync failed" >> "$LOG_FILE"
    exit 1
fi

# Keep only last 100 lines of log
tail -100 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
