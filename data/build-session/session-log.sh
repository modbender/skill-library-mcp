#!/bin/bash
# session-log.sh — Quick session logging helper
# Usage: ./session-log.sh "What I Built" "Key Insight"

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
TODAY=$(date +%Y-%m-%d)
NOW=$(date +%H:%M)
MEMORY_DIR="$WORKSPACE/memory"
LOG_FILE="$MEMORY_DIR/$TODAY.md"

# Create memory dir if needed
mkdir -p "$MEMORY_DIR"

# Create file with header if new
if [ ! -f "$LOG_FILE" ]; then
    echo "# $TODAY ($(date +%A))" > "$LOG_FILE"
    echo "" >> "$LOG_FILE"
fi

TITLE="${1:-Build Session}"
INSIGHT="${2:-No notable insights}"

cat >> "$LOG_FILE" << EOF

---

## Build Session: $NOW — $TITLE

### What I Built
$TITLE

### Key Insights
$INSIGHT

### Git
$(cd "$WORKSPACE" && git status --short 2>/dev/null | head -5 || echo "Not a git repo")

EOF

echo "✓ Logged to $LOG_FILE"
