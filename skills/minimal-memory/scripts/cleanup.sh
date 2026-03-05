#!/bin/bash
# Cleanup: migrate GOOD/BAD entries from daily files to MEMORY.md

MEMORY_DIR="${MEMORY_DIR:-$HOME/.openclaw/workspace/memory}"
WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
MEMORY_FILE="$WORKSPACE/MEMORY.md"

echo "🧹 Memory Cleanup"
echo "================"
echo ""

# Find recent entries (last 14 days)
echo "Checking last 14 days of daily files..."
echo ""

GOOD_ENTRIES=""
BAD_ENTRIES=""

for i in $(seq 0 13); do
    DATE=$(date -v-${i}d +%Y-%m-%d 2>/dev/null || date -d "-$i days" +%Y-%m-%d 2>/dev/null)
    FILE="$MEMORY_DIR/$DATE.md"
    
    if [[ -f "$FILE" ]]; then
        # Extract GOOD entries
        FILE_GOOD=$(grep "\[GOOD\]" "$FILE" 2>/dev/null | sed 's/^[[:space:]]*- //' | sed 's/^[[:space:]]*//')
        if [[ -n "$FILE_GOOD" ]]; then
            GOOD_ENTRIES="$GOOD_ENTRIES
# From $DATE:
$FILE_GOOD"
        fi
        
        # Extract BAD entries
        FILE_BAD=$(grep "\[BAD\]" "$FILE" 2>/dev/null | sed 's/^[[:space:]]*- //' | sed 's/^[[:space:]]*//')
        if [[ -n "$FILE_BAD" ]]; then
            BAD_ENTRIES="$BAD_ENTRIES
# From $DATE:
$FILE_BAD"
        fi
    fi
done

# Display findings
echo "📈 [GOOD] entries found:"
if [[ -n "$GOOD_ENTRIES" ]]; then
    echo "$GOOD_ENTRIES" | head -20
else
    echo "   None found"
fi

echo ""
echo "📉 [BAD] entries found:"
if [[ -n "$BAD_ENTRIES" ]]; then
    echo "$BAD_ENTRIES" | head -20
else
    echo "   None found"
fi

echo ""
echo "💡 Next steps:"
echo "   1. Review entries above"
echo "   2. Add condensed GOOD/BAD sections to MEMORY.md"
echo "   3. Remove duplicates and similar items"
echo "   4. Ensure MEMORY.md stays under 150 lines"
echo ""
echo "   To auto-migrate (use with caution):"
echo "   $(dirname $0)/cleanup.sh --apply"

# If --apply flag, actually modify MEMORY.md
if [[ "$1" == "--apply" ]]; then
    echo ""
    echo "⚠️  Auto-migration not yet implemented - manual review recommended"
    echo "   Please manually update MEMORY.md based on entries above"
fi
