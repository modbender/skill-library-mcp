#!/bin/bash
# lattice-hot-tracker.sh - Hot feed tracker
# Recommended schedule: 0 */6 * * * (every 6 hours)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$(dirname "$SCRIPT_DIR")/bin"
LATTICE_URL="${LATTICE_URL:-https://lattice.quest}"
LOG_DIR="${HOME}/.lattice/logs"

mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/hot-tracker-$(date +%Y%m%d).log"
FEED_FILE="$LOG_DIR/hot-feed-$(date +%H%M).txt"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting hot feed tracking..." >> "$LOG_FILE"

# Check if identity exists
if [ ! -f "$HOME/.lattice/keys.json" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ No identity found. Skipping." >> "$LOG_FILE"
    exit 0
fi

# Get hot feed (page 1)
if "$BIN_DIR/lattice-feed" --hot --page 1 --limit 10 > "$FEED_FILE" 2>> "$LOG_FILE"; then
    POST_COUNT=$(grep -c "^[┌├]" "$FEED_FILE" 2>/dev/null || echo "0")
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Hot feed tracked. $POST_COUNT trending posts found." >> "$LOG_FILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📄 Feed saved to: $FEED_FILE" >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ Hot feed tracking failed." >> "$LOG_FILE"
fi

# Cleanup old logs (keep last 3 days)
find "$LOG_DIR" -name "hot-tracker-*.log" -mtime +3 -delete 2>/dev/null || true
find "$LOG_DIR" -name "hot-feed-*.txt" -mtime +3 -delete 2>/dev/null || true
