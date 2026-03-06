#!/bin/bash
# fetch-skill.sh — Download skill source files as TEXT ONLY for review
# Usage: bash fetch-skill.sh <author>/<skill-name>
# Output: Prints all skill file contents to stdout (for piping to review agent)
# SAFETY: This script ONLY downloads and prints text. It never executes anything.

set -e

SKILL_PATH="${1:?Usage: fetch-skill.sh <author>/<skill-name>}"
AUTHOR=$(echo "$SKILL_PATH" | cut -d'/' -f1)
SKILL=$(echo "$SKILL_PATH" | cut -d'/' -f2)
API_PATH="/repos/openclaw/skills/contents/skills/$AUTHOR/$SKILL"
RAW_BASE="https://raw.githubusercontent.com/openclaw/skills/main/skills/$AUTHOR/$SKILL"

echo "=========================================="
echo "SKILL SOURCE: $AUTHOR/$SKILL"
echo "=========================================="
echo ""

# Fetch file listing using gh CLI (authenticated, higher rate limit)
FILES=$(gh api "$API_PATH" 2>/dev/null | python3 -c "
import json, sys
data = json.load(sys.stdin)
if isinstance(data, list):
    for f in data:
        if f['type'] == 'file':
            print(f'FILE:{f[\"name\"]}:{f[\"size\"]}')
        elif f['type'] == 'dir':
            print(f'DIR:{f[\"name\"]}')
" 2>/dev/null)

# Print each file's contents
while IFS= read -r entry; do
    TYPE=$(echo "$entry" | cut -d':' -f1)
    NAME=$(echo "$entry" | cut -d':' -f2)
    
    if [ "$TYPE" = "FILE" ]; then
        echo "--- FILE: $NAME ---"
        curl -sL "$RAW_BASE/$NAME"
        echo ""
        echo ""
    elif [ "$TYPE" = "DIR" ]; then
        # Recurse one level into subdirectories
        SUBFILES=$(gh api "$API_PATH/$NAME" 2>/dev/null | python3 -c "
import json, sys
data = json.load(sys.stdin)
if isinstance(data, list):
    for f in data:
        if f['type'] == 'file':
            print(f['name'])
" 2>/dev/null)
        while IFS= read -r subfile; do
            if [ -n "$subfile" ]; then
                echo "--- FILE: $NAME/$subfile ---"
                curl -sL "$RAW_BASE/$NAME/$subfile"
                echo ""
                echo ""
            fi
        done <<< "$SUBFILES"
    fi
done <<< "$FILES"

echo "=========================================="
echo "END OF SKILL SOURCE"
echo "=========================================="
