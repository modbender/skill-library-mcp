#!/bin/bash
set -eo pipefail

echo "$(date): Starting memory sync..." 

WORKSPACE="${1:-$(pwd)}"
cd "$WORKSPACE"

# Check if MEMORY.md exists
if [[ ! -f "MEMORY.md" ]]; then
    echo "$(date): Creating MEMORY.md"
    echo "# Agent Memory" > MEMORY.md
    echo "" >> MEMORY.md
fi

# Sync today's memory to MEMORY.md if it has content
TODAY_MEMORY="memory/$(date +%Y-%m-%d).md"
if [[ -f "$TODAY_MEMORY" ]] && [[ -s "$TODAY_MEMORY" ]]; then
    echo "$(date): Syncing daily memory to MEMORY.md"
    
    # Add today's content to MEMORY.md if not already present
    if ! grep -q "$(date +%Y-%m-%d)" MEMORY.md; then
        echo "" >> MEMORY.md
        echo "## $(date +%Y-%m-%d)" >> MEMORY.md
        cat "$TODAY_MEMORY" >> MEMORY.md
    fi
fi

# Clean up old memory files (keep last 30 days)
find memory/ -name "*.md" -mtime +30 -delete 2>/dev/null || true

echo "$(date): Memory sync completed"