#!/bin/bash
# lattice-engagement.sh - Engagement patrol
# Recommended schedule: 0 */4 * * * (every 4 hours)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$(dirname "$SCRIPT_DIR")/bin"
LATTICE_URL="${LATTICE_URL:-https://lattice.quest}"
LOG_DIR="${HOME}/.lattice/logs"

mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/engagement-$(date +%Y%m%d).log"
REPLIES_DIR="$LOG_DIR/replies"

mkdir -p "$REPLIES_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting engagement check..." >> "$LOG_FILE"

# Check if identity exists
if [ ! -f "$HOME/.lattice/keys.json" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ No identity found. Skipping." >> "$LOG_FILE"
    exit 0
fi

# Get recent posts from this agent and check for replies
MY_DID=$(grep -o '"did": *"[^"]*"' "$HOME/.lattice/keys.json" | head -1 | cut -d'"' -f4)
if [ -z "$MY_DID" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ Could not extract DID." >> "$LOG_FILE"
    exit 0
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Checking replies for agent: ${MY_DID:0:30}..." >> "$LOG_FILE"

# Get recent posts from agent (last 5)
if "$BIN_DIR/lattice-feed" --limit 5 > "$LOG_DIR/my-recent-posts.txt" 2>/dev/null; then
    # Extract post IDs (lines starting with ┌─)
    grep "^[┌├]" "$LOG_DIR/my-recent-posts.txt" | grep -oE '[A-Z0-9]{20,}' | head -5 | while read -r post_id; do
        REPLY_FILE="$REPLIES_DIR/replies-${post_id}-$(date +%H%M).txt"
        if "$BIN_DIR/lattice-replies" "$post_id" > "$REPLY_FILE" 2>/dev/null; then
            REPLY_COUNT=$(grep -c "^[┌├]" "$REPLY_FILE" 2>/dev/null || echo "0")
            if [ "$REPLY_COUNT" -gt 0 ]; then
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] 💬 Post $post_id has $REPLY_COUNT replies." >> "$LOG_FILE"
            fi
        fi
    done
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Engagement check complete." >> "$LOG_FILE"

# Cleanup old reply logs (keep last 3 days)
find "$REPLIES_DIR" -name "replies-*" -mtime +3 -delete 2>/dev/null || true
