#!/bin/bash
# Archive memories older than N days
# Usage: ./prune.sh [days]

set -e

DAYS="${1:-30}"
MEMORY_DIR="${AGENT_MEMORY_DIR:-$HOME/.agent-memory}"
ARCHIVE_DIR="$MEMORY_DIR/archive"

if [ ! -d "$MEMORY_DIR" ]; then
    echo "No memories to prune."
    exit 0
fi

mkdir -p "$ARCHIVE_DIR"

CUTOFF=$(date -u -d "$DAYS days ago" +%s 2>/dev/null || date -u -v-${DAYS}d +%s 2>/dev/null)
if [ -z "$CUTOFF" ]; then
    echo "Error: could not compute cutoff date"
    exit 1
fi

COUNT=0

find "$MEMORY_DIR" -name "*.jsonl" -not -path "*/archive/*" | while read -r FILE; do
    # Extract date from path: .../YYYY/MM/DD.jsonl
    BASENAME=$(basename "$FILE" .jsonl)
    DIRMONTH=$(basename "$(dirname "$FILE")")
    DIRYEAR=$(basename "$(dirname "$(dirname "$FILE")")")

    FILE_DATE="${DIRYEAR}-${DIRMONTH}-${BASENAME}"
    FILE_TS=$(date -u -d "$FILE_DATE" +%s 2>/dev/null || date -u -j -f "%Y-%m-%d" "$FILE_DATE" +%s 2>/dev/null || echo "")

    if [ -z "$FILE_TS" ]; then
        continue
    fi

    if [ "$FILE_TS" -lt "$CUTOFF" ]; then
        REL_DIR="$DIRYEAR/$DIRMONTH"
        mkdir -p "$ARCHIVE_DIR/$REL_DIR"
        mv "$FILE" "$ARCHIVE_DIR/$REL_DIR/"
        echo "📦 Archived: $FILE_DATE"
        COUNT=$((COUNT + 1))
    fi
done

# Clean up empty directories
find "$MEMORY_DIR" -type d -empty -not -path "*/archive*" -not -path "$MEMORY_DIR" -delete 2>/dev/null || true

echo "✓ Pruning complete. Archived files older than $DAYS days."
