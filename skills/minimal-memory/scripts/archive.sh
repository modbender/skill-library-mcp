#!/bin/bash
# Archive old NEUTRAL entries (older than 30 days)

MEMORY_DIR="${MEMORY_DIR:-$HOME/.openclaw/workspace/memory}"
ARCHIVE_DIR="$MEMORY_DIR/archive"

CUTOFF_DAYS=30

echo "📦 Memory Archival"
echo "=================="
echo ""
echo "Archiving NEUTRAL entries older than $CUTOFF_DAYS days..."
echo ""

mkdir -p "$ARCHIVE_DIR"

ARCHIVED_COUNT=0

for FILE in "$MEMORY_DIR"/*.md; do
    if [[ ! -f "$FILE" ]]; then
        continue
    fi
    
    FILENAME=$(basename "$FILE")
    
    # Skip archive directory
    if [[ "$FILE" == *"/archive/"* ]]; then
        continue
    fi
    
    # Extract date from filename
    FILE_DATE=$(echo "$FILENAME" | grep -oE '^[0-9]{4}-[0-9]{2}-[0-9]{2}')
    
    if [[ -z "$FILE_DATE" ]]; then
        continue
    fi
    
    # Calculate age
    FILE_EPOCH=$(date -j -f "%Y-%m-%d" "$FILE_DATE" +%s 2>/dev/null || date -d "$FILE_DATE" +%s 2>/dev/null)
    TODAY_EPOCH=$(date +%s)
    AGE_DAYS=$(( (TODAY_EPOCH - FILE_EPOCH) / 86400 ))
    
    if [[ $AGE_DAYS -gt $CUTOFF_DAYS ]]; then
        # Check if file has only NEUTRAL entries (no GOOD/BAD worth keeping)
        HAS_GOOD=$(grep -c "\[GOOD\]" "$FILE" 2>/dev/null || echo "0")
        HAS_BAD=$(grep -c "\[BAD\]" "$FILE" 2>/dev/null || echo "0")
        
        if [[ "$HAS_GOOD" == "0" && "$HAS_BAD" == "0" ]]; then
            mv "$FILE" "$ARCHIVE_DIR/"
            echo "   Archived: $FILENAME ($AGE_DAYS days old)"
            ((ARCHIVED_COUNT++))
        else
            echo "   Kept: $FILENAME (contains GOOD/BAD entries)"
        fi
    fi
done

echo ""
if [[ $ARCHIVED_COUNT -gt 0 ]]; then
    echo "✅ Archived $ARCHIVED_COUNT files to $ARCHIVE_DIR"
else
    echo "ℹ️  No files needed archiving"
fi
