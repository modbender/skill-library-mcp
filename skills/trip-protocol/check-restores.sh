#!/bin/bash
# check-restores.sh - Check and execute any due restore jobs
# Usage: ./check-restores.sh
#
# This script is meant to be called periodically (via cron or heartbeat)
# to check if any scheduled trip restores are due.

set -e

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
SCHEDULED_DIR="$WORKSPACE/memory/scheduled"
SKILL_DIR="$(dirname "$0")"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[trip]${NC} $1"; }
warn() { echo -e "${YELLOW}[trip]${NC} $1"; }

# Exit if no scheduled directory
if [ ! -d "$SCHEDULED_DIR" ]; then
    exit 0
fi

# Get current time in ISO format
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
NOW_EPOCH=$(date -u +%s)

# Check each scheduled restore
for SCHED_FILE in "$SCHEDULED_DIR"/trip-restore-*.json; do
    [ -f "$SCHED_FILE" ] || continue
    
    # Read schedule data
    STATUS=$(jq -r '.status' "$SCHED_FILE" 2>/dev/null)
    
    # Skip if not pending
    if [ "$STATUS" != "pending" ]; then
        continue
    fi
    
    TRIGGER_TIME=$(jq -r '.triggerAt' "$SCHED_FILE" 2>/dev/null)
    SNAPSHOT_ID=$(jq -r '.snapshotId' "$SCHED_FILE" 2>/dev/null)
    TOKEN_ID=$(jq -r '.tokenId' "$SCHED_FILE" 2>/dev/null)
    
    # Convert trigger time to epoch
    TRIGGER_EPOCH=$(date -u -d "$TRIGGER_TIME" +%s 2>/dev/null || \
                    python3 -c "from datetime import datetime; print(int(datetime.fromisoformat('$TRIGGER_TIME'.replace('Z', '+00:00')).timestamp()))" 2>/dev/null || \
                    echo "0")
    
    # Check if due
    if [ "$NOW_EPOCH" -ge "$TRIGGER_EPOCH" ] && [ "$TRIGGER_EPOCH" -gt 0 ]; then
        log "Trip #$TOKEN_ID restore is due! Executing..."
        
        # Mark as executing
        jq '.status = "executing"' "$SCHED_FILE" > "$SCHED_FILE.tmp" && mv "$SCHED_FILE.tmp" "$SCHED_FILE"
        
        # Execute restore
        if "$SKILL_DIR/restore.sh" "$SNAPSHOT_ID"; then
            log "✓ Trip #$TOKEN_ID restored successfully"
            
            # Mark as completed
            jq '.status = "completed" | .completedAt = "'"$NOW"'"' "$SCHED_FILE" > "$SCHED_FILE.tmp" && mv "$SCHED_FILE.tmp" "$SCHED_FILE"
            
            # Move to archive
            ARCHIVE_DIR="$SCHEDULED_DIR/completed"
            mkdir -p "$ARCHIVE_DIR"
            mv "$SCHED_FILE" "$ARCHIVE_DIR/"
        else
            warn "Failed to restore trip #$TOKEN_ID"
            jq '.status = "failed" | .error = "restore script failed"' "$SCHED_FILE" > "$SCHED_FILE.tmp" && mv "$SCHED_FILE.tmp" "$SCHED_FILE"
        fi
    fi
done
