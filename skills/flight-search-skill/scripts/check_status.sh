#!/bin/bash
# Check flight status using AviationStack API
# Usage: ./check_status.sh FLIGHT_NUMBER [DATE]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
PYTHON_SCRIPT="$SKILL_DIR/lib/aviationstack_client.py"

# Check arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 FLIGHT_NUMBER [DATE]"
    echo ""
    echo "Example:"
    echo "  $0 AA123"
    echo "  $0 LA1234 2026-03-15"
    echo "  $0 G34567"
    exit 1
fi

FLIGHT="$1"
DATE="${2:-}"

# Execute (safe - no eval, direct argument passing)
echo "✈️ Checking flight status: $FLIGHT" >&2
[ -n "$DATE" ] && echo "📅 Date: $DATE" >&2
echo "" >&2

if [ -n "$DATE" ]; then
    python3 "$PYTHON_SCRIPT" \
        --flight "$FLIGHT" \
        --date "$DATE"
else
    python3 "$PYTHON_SCRIPT" \
        --flight "$FLIGHT"
fi
