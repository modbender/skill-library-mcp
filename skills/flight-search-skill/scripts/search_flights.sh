#!/bin/bash
# Search flights using Amadeus API
# Usage: ./search_flights.sh ORIGIN DEST DEPARTURE_DATE [RETURN_DATE]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
PYTHON_SCRIPT="$SKILL_DIR/lib/amadeus_client.py"

# Check arguments
if [ $# -lt 3 ]; then
    echo "Usage: $0 ORIGIN DEST DEPARTURE_DATE [RETURN_DATE]"
    echo ""
    echo "Example:"
    echo "  $0 CNF BKK 2026-12-15"
    echo "  $0 CNF BKK 2026-12-15 2027-01-10"
    exit 1
fi

ORIGIN="$1"
DESTINATION="$2"
DEPARTURE="$3"
RETURN="${4:-}"

# Execute (safe - no eval, direct argument passing)
echo "🔍 Searching flights: $ORIGIN → $DESTINATION" >&2
echo "📅 Departure: $DEPARTURE" >&2
[ -n "$RETURN" ] && echo "📅 Return: $RETURN" >&2
echo "" >&2

if [ -n "$RETURN" ]; then
    python3 "$PYTHON_SCRIPT" \
        --origin "$ORIGIN" \
        --destination "$DESTINATION" \
        --departure "$DEPARTURE" \
        --return "$RETURN"
else
    python3 "$PYTHON_SCRIPT" \
        --origin "$ORIGIN" \
        --destination "$DESTINATION" \
        --departure "$DEPARTURE"
fi
