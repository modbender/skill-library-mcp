#!/bin/bash
# Memory Maintenance Agent v2 - Auto-cleanup
# Archives old reviews and enforces retention policy
# Run daily after memory-maintenance-v2.sh

set -e

WORKSPACE="/Users/maxhutchinson/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/agents/memory"
DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y-%m-%d-%H%M)

echo "[$TIMESTAMP] Starting memory cleanup..."

# Create archive structure
mkdir -p "$MEMORY_DIR/archive/$(date +%Y-%m)"
mkdir -p "$MEMORY_DIR/.trash"

# ============================================
# STEP 1: Clean up error logs if successful review exists
# ============================================
LATEST_REVIEW=$(ls -1 "$MEMORY_DIR"/review-v2-*.json 2>/dev/null | tail -1)
if [ -n "$LATEST_REVIEW" ]; then
    # If we have a successful review, delete error logs from today
    TODAY_ERRORS=$(find "$MEMORY_DIR" -name "error-*${DATE}*.txt" -type f 2>/dev/null)
    if [ -n "$TODAY_ERRORS" ]; then
        echo "[$TIMESTAMP] Cleaning up $(echo "$TODAY_ERRORS" | wc -l | tr -d ' ') error logs..."
        echo "$TODAY_ERRORS" | while read -r f; do
            mv "$f" "$MEMORY_DIR/.trash/"
        done
    fi
fi

# ============================================
# STEP 2: Archive reviews older than 7 days
# ============================================
echo "[$TIMESTAMP] Archiving reviews older than 7 days..."
ARCHIVED_COUNT=0

find "$MEMORY_DIR" -maxdepth 1 -name "review-v2-*.json" -type f -mtime +7 2>/dev/null | while read -r file; do
    BASENAME=$(basename "$file")
    FILE_DATE=$(echo "$BASENAME" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}')
    if [ -n "$FILE_DATE" ]; then
        MONTH=$(echo "$FILE_DATE" | cut -d'-' -f1-2)
        mkdir -p "$MEMORY_DIR/archive/$MONTH"
        mv "$file" "$MEMORY_DIR/archive/$MONTH/"
        # Also move corresponding .md if exists
        MD_FILE="${file%.json}.md"
        if [ -f "$MD_FILE" ]; then
            mv "$MD_FILE" "$MEMORY_DIR/archive/$MONTH/"
        fi
        ARCHIVED_COUNT=$((ARCHIVED_COUNT + 1))
        echo "  Archived: $BASENAME → archive/$MONTH/"
    fi
done

# ============================================
# STEP 3: Enforce retention policy (delete archive >30 days)
# ============================================
echo "[$TIMESTAMP] Enforcing 30-day retention policy..."
DELETED_COUNT=0

find "$MEMORY_DIR/archive" -type f -mtime +30 2>/dev/null | while read -r file; do
    mv "$file" "$MEMORY_DIR/.trash/"
    DELETED_COUNT=$((DELETED_COUNT + 1))
    echo "  Moved to trash: $(basename "$file")"
done

# ============================================
# STEP 4: Clean up .consolidated directory if >7 days old
# ============================================
if [ -d "$WORKSPACE/memory/.consolidated" ]; then
    CONSOLIDATED_AGE=$(find "$WORKSPACE/memory/.consolidated" -type f -mtime +7 2>/dev/null | wc -l | tr -d ' ')
    if [ "$CONSOLIDATED_AGE" -gt 0 ]; then
        echo "[$TIMESTAMP] Cleaning up old consolidated fragments..."
        find "$WORKSPACE/memory/.consolidated" -type f -mtime +7 -exec rm {} \;
        rmdir "$WORKSPACE/memory/.consolidated" 2>/dev/null || true
    fi
fi

# ============================================
# STEP 5: Update stats
# ============================================
STATS_FILE="$MEMORY_DIR/stats.json"
CURRENT_STATS=$(cat "$STATS_FILE" 2>/dev/null || echo '{}')

echo "$CURRENT_STATS" | jq --arg date "$DATE" --arg archived "$ARCHIVED_COUNT" --arg deleted "$DELETED_COUNT" '{
    lastCleanup: $date,
    totalArchived: (.totalArchived // 0) + ($archived | tonumber),
    totalDeleted: (.totalDeleted // 0) + ($deleted | tonumber),
    cleanupHistory: ((.cleanupHistory // []) + [{date: $date, archived: ($archived | tonumber), deleted: ($deleted | tonumber)}] | last(10))
}' > "$STATS_FILE.tmp"

mv "$STATS_FILE.tmp" "$STATS_FILE"

echo "[$TIMESTAMP] Cleanup complete:"
echo "  - Archived: $ARCHIVED_COUNT"
echo "  - Deleted: $DELETED_COUNT"
echo "  - Stats: $STATS_FILE"
