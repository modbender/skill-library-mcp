#!/bin/bash
# Search through all memory files with categorization filters

MEMORY_DIR="${MEMORY_DIR:-$HOME/.openclaw/workspace/memory}"
WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"

usage() {
    echo "Usage: search.sh [OPTIONS] QUERY"
    echo ""
    echo "Search memory files with categorization"
    echo ""
    echo "Options:"
    echo "  --good       Search only [GOOD] entries"
    echo "  --bad        Search only [BAD] entries"
    echo "  --neutral    Search only [NEUTRAL] entries"
    echo "  --recent N   Search only last N days (default: 7)"
    echo "  --all        Search all memory (default)"
    echo "  -h, --help   Show this help"
    echo ""
    echo "Examples:"
    echo "  search.sh \"duplicate posting\""
    echo "  search.sh --good \"CSV format\""
    echo "  search.sh --recent 3 \"cron job\""
}

# Parse arguments
CATEGORY=""
RECENT_DAYS=""
QUERY=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --good)
            CATEGORY="GOOD"
            shift
            ;;
        --bad)
            CATEGORY="BAD"
            shift
            ;;
        --neutral)
            CATEGORY="NEUTRAL"
            shift
            ;;
        --recent)
            RECENT_DAYS="${2:-7}"
            shift 2
            ;;
        --all)
            CATEGORY=""
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            QUERY="$1"
            shift
            ;;
    esac
done

if [[ -z "$QUERY" ]]; then
    echo "Error: No search query provided"
    usage
    exit 1
fi

echo "🔍 Searching memory for: $QUERY"
if [[ -n "$CATEGORY" ]]; then
    echo "   Category: [$CATEGORY]"
fi
if [[ -n "$RECENT_DAYS" ]]; then
    echo "   Time range: last $RECENT_DAYS days"
fi
echo ""

# Build grep pattern
if [[ -n "$CATEGORY" ]]; then
    PATTERN="\[$CATEGORY\]"
else
    PATTERN=".*"
fi

# Find files to search
FILES_TO_SEARCH=""

# Always include MEMORY.md
if [[ -f "$WORKSPACE/MEMORY.md" ]]; then
    FILES_TO_SEARCH="$WORKSPACE/MEMORY.md"
fi

# Add daily files
if [[ -n "$RECENT_DAYS" ]]; then
    # Recent files only
    for i in $(seq 0 $((RECENT_DAYS - 1))); do
        DATE=$(date -v-${i}d +%Y-%m-%d 2>/dev/null || date -d "-$i days" +%Y-%m-%d 2>/dev/null)
        FILE="$MEMORY_DIR/$DATE.md"
        if [[ -f "$FILE" ]]; then
            FILES_TO_SEARCH="$FILES_TO_SEARCH $FILE"
        fi
    done
else
    # All daily files
    if [[ -d "$MEMORY_DIR" ]]; then
        FILES_TO_SEARCH="$FILES_TO_SEARCH $MEMORY_DIR/*.md"
    fi
fi

# Perform search
if [[ -n "$FILES_TO_SEARCH" ]]; then
    RESULTS=$(grep -r -i -n "$QUERY" $FILES_TO_SEARCH 2>/dev/null | grep -i "$PATTERN" | head -20)
    
    if [[ -n "$RESULTS" ]]; then
        echo "$RESULTS" | while read -r line; do
            # Extract category for color coding
            if echo "$line" | grep -q "\[GOOD\]"; then
                echo "✅ $line"
            elif echo "$line" | grep -q "\[BAD\]"; then
                echo "❌ $line"
            elif echo "$line" | grep -q "\[NEUTRAL\]"; then
                echo "⚪ $line"
            else
                echo "   $line"
            fi
        done
        echo ""
        echo "Found $(echo "$RESULTS" | wc -l | tr -d ' ') results"
    else
        echo "No results found"
    fi
else
    echo "No memory files found"
fi
