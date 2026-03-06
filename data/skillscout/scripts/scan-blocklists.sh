#!/bin/bash
# scan-blocklists.sh — Stage 1: Check skill against known blocklists
# Usage: bash scan-blocklists.sh <skill-name>
# Returns exit code 0 if clean, 1 if blocked

set -e

SKILL="${1:?Usage: scan-blocklists.sh <skill-name>}"
BLOCKLIST="data/blocklist.json"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🔍 Stage 1: Scanning blocklists for '$SKILL'..."

# Check local blocklist
if [ -f "$PROJECT_DIR/$BLOCKLIST" ]; then
    BLOCKED=$(python3 -c "
import json
with open('$PROJECT_DIR/$BLOCKLIST') as f:
    data = json.load(f)
blocked = [s['name'] for s in data.get('blocked', [])]
print('BLOCKED' if '$SKILL' in blocked else 'CLEAN')
" 2>/dev/null)
    
    if [ "$BLOCKED" = "BLOCKED" ]; then
        echo "❌ BLOCKED: '$SKILL' is on the local blocklist"
        exit 1
    fi
fi

# Check VoltAgent awesome-list exclusions (if cached)
if [ -f "$PROJECT_DIR/data/voltagen-excluded.txt" ]; then
    if grep -qi "^$SKILL$" "$PROJECT_DIR/data/voltagen-excluded.txt"; then
        echo "⚠️  WARNING: '$SKILL' was excluded by VoltAgent awesome-list curation"
        echo "   (May be spam, duplicate, or flagged — proceed to Stage 2 with caution)"
    fi
fi

echo "✅ Stage 1 PASSED: No blocklist matches for '$SKILL'"
exit 0
