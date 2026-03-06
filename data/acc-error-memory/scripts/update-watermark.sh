#!/bin/bash
# Update ACC watermark after processing
#
# Usage:
#   update-watermark.sh --timestamp "2026-02-11T10:00:00Z"
#   update-watermark.sh --from-pending    # Use latest timestamp from pending-errors.json

set -e

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
WATERMARK_FILE="$WORKSPACE/memory/acc-watcher-watermark.json"
PENDING_FILE="$WORKSPACE/memory/pending-errors.json"

TIMESTAMP=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --timestamp) TIMESTAMP="$2"; shift 2 ;;
        --from-pending)
            if [ -f "$PENDING_FILE" ]; then
                TIMESTAMP=$(python3 -c "
import json
data = json.load(open('$PENDING_FILE'))
if data:
    print(data[-1]['timestamp'])
" 2>/dev/null || echo "")
            fi
            shift
            ;;
        *) shift ;;
    esac
done

if [ -z "$TIMESTAMP" ]; then
    # Use current time as fallback
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
fi

# Update watermark
python3 << PYTHON
import json
from datetime import datetime

watermark = {
    "session": None,
    "line": 0,
    "timestamp": "$TIMESTAMP"
}

with open("$WATERMARK_FILE", "w") as f:
    json.dump(watermark, f, indent=2)

print(f"✓ Watermark updated: $TIMESTAMP")
PYTHON
