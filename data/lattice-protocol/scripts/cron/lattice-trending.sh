#!/bin/bash
# lattice-trending.sh - Trending topics explorer
# Recommended schedule: 0 10,18 * * * (10:00 AM and 6:00 PM)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$(dirname "$SCRIPT_DIR")/bin"
LATTICE_URL="${LATTICE_URL:-https://lattice.quest}"
LOG_DIR="${HOME}/.lattice/logs"

mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/trending-$(date +%Y%m%d).log"
TOPICS_FILE="$LOG_DIR/trending-topics-$(date +%H%M).txt"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting trending topics check..." >> "$LOG_FILE"

# Check if identity exists
if [ ! -f "$HOME/.lattice/keys.json" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ No identity found. Skipping." >> "$LOG_FILE"
    exit 0
fi

# Get trending topics
if "$BIN_DIR/lattice-topics" --trending 20 > "$TOPICS_FILE" 2>> "$LOG_FILE"; then
    TOPIC_COUNT=$(grep -c "^│" "$TOPICS_FILE" 2>/dev/null || echo "0")
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Trending topics updated. $TOPIC_COUNT topics found." >> "$LOG_FILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📄 Topics saved to: $TOPICS_FILE" >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ Trending topics check failed." >> "$LOG_FILE"
fi

# Cleanup old logs (keep last 7 days)
find "$LOG_DIR" -name "trending-*.log" -mtime +7 -delete 2>/dev/null || true
find "$LOG_DIR" -name "trending-topics-*.txt" -mtime +3 -delete 2>/dev/null || true
