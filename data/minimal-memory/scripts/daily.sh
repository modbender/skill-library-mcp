#!/bin/bash
# Create or open today's memory file

MEMORY_DIR="${MEMORY_DIR:-$HOME/.openclaw/workspace/memory}"
TODAY=$(date +%Y-%m-%d)
TODAY_FILE="$MEMORY_DIR/$TODAY.md"

# Create memory directory if needed
mkdir -p "$MEMORY_DIR"

# If file doesn't exist, create with template
if [[ ! -f "$TODAY_FILE" ]]; then
    cat > "$TODAY_FILE" << EOF
# $TODAY - Daily Memory Log

## [GOOD]
- 

## [BAD]
- 

## [NEUTRAL]
- 

## Notes
- 
EOF
    echo "✅ Created: $TODAY_FILE"
else
    echo "📄 Exists: $TODAY_FILE"
fi

echo ""
echo "File location: $TODAY_FILE"
