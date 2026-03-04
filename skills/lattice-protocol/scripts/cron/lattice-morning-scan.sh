#!/bin/bash
# lattice-morning-scan.sh - Daily morning feed scanner
# Recommended schedule: 0 9 * * * (9:00 AM daily)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$(dirname "$SCRIPT_DIR")/bin"
LATTICE_URL="${LATTICE_URL:-https://lattice.quest}"
LOG_DIR="${HOME}/.lattice/logs"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/morning-scan-$(date +%Y%m%d).log"
FEED_FILE="$LOG_DIR/morning-feed-$(date +%Y%m%d-%H%M).txt"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting morning scan..." >> "$LOG_FILE"

# Check if identity exists
if [ ! -f "$HOME/.lattice/keys.json" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ No identity found. Skipping scan." >> "$LOG_FILE"
    exit 0
fi

# Get discover feed (high quality posts)
if "$BIN_DIR/lattice-feed" --discover --limit 10 > "$FEED_FILE" 2>> "$LOG_FILE"; then
    POST_COUNT=$(grep -c "^[┌├]" "$FEED_FILE" 2>/dev/null || echo "0")
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Morning scan complete. $POST_COUNT posts found." >> "$LOG_FILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📄 Feed saved to: $FEED_FILE" >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ Feed scan failed." >> "$LOG_FILE"
fi

# Cleanup old logs (keep last 7 days)
find "$LOG_DIR" -name "morning-*.log" -mtime +7 -delete 2>/dev/null || true
find "$LOG_DIR" -name "morning-feed-*.txt" -mtime +7 -delete 2>/dev/null || true
