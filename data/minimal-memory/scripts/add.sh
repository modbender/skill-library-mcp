#!/bin/bash
# Add a tagged entry to today's memory file

MEMORY_DIR="${MEMORY_DIR:-$HOME/.openclaw/workspace/memory}"
TODAY=$(date +%Y-%m-%d)
TODAY_FILE="$MEMORY_DIR/$TODAY.md"

usage() {
    echo "Usage: add.sh CATEGORY \"Entry text\""
    echo ""
    echo "Categories: GOOD, BAD, NEUTRAL"
    echo ""
    echo "Examples:"
    echo '  add.sh GOOD "CSV batching prevents duplicates"'
    echo '  add.sh BAD "Bird CLI blocked by X anti-bot"'
    echo '  add.sh NEUTRAL "Day 5 of media plan"'
}

if [[ $# -lt 2 ]]; then
    usage
    exit 1
fi

CATEGORY=$(echo "$1" | tr '[:lower:]' '[:upper:]')
ENTRY="$2"

# Validate category
if [[ "$CATEGORY" != "GOOD" && "$CATEGORY" != "BAD" && "$CATEGORY" != "NEUTRAL" ]]; then
    echo "Error: Category must be GOOD, BAD, or NEUTRAL"
    usage
    exit 1
fi

# Create daily file if needed
if [[ ! -f "$TODAY_FILE" ]]; then
    cat > "$TODAY_FILE" << EOF
# $TODAY - Daily Memory Log

## [GOOD]
- 

## [BAD]
- 

## [NEUTRAL]
- 
EOF
fi

# Check if file has the category sections
if ! grep -q "^## \[GOOD\]" "$TODAY_FILE" 2>/dev/null; then
    # Add category sections at the end
    echo "" >> "$TODAY_FILE"
    echo "## [GOOD]" >> "$TODAY_FILE"
    echo "- " >> "$TODAY_FILE"
    echo "" >> "$TODAY_FILE"
    echo "## [BAD]" >> "$TODAY_FILE"
    echo "- " >> "$TODAY_FILE"
    echo "" >> "$TODAY_FILE"
    echo "## [NEUTRAL]" >> "$TODAY_FILE"
    echo "- " >> "$TODAY_FILE"
fi

# Add entry to the file using sed
TEMP_FILE=$(mktemp)

# Find the section and add entry after the header
awk -v cat="$CATEGORY" -v entry="$ENTRY" '
    BEGIN { in_section = 0 }
    /^## \['"$CATEGORY"'\]/ {
        print
        in_section = 1
        next
    }
    in_section && /^## / {
        in_section = 0
    }
    in_section && /^- $/ {
        print "- ["cat"] "entry
        in_section = 0
        next
    }
    { print }
' "$TODAY_FILE" > "$TEMP_FILE"

mv "$TEMP_FILE" "$TODAY_FILE"

case "$CATEGORY" in
    GOOD)  echo "✅ [GOOD] Added: $ENTRY" ;;
    BAD)   echo "❌ [BAD] Added: $ENTRY" ;;
    NEUTRAL) echo "⚪ [NEUTRAL] Added: $ENTRY" ;;
esac
