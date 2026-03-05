#!/usr/bin/env bash
# check_availability.sh - Check if specific coordinates are available on the Million Bit Homepage
#
# Usage: ./check_availability.sh <x1> <y1> <x2> <y2>
#
# Output: JSON with available (bool), coordinates

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <x1> <y1> <x2> <y2>" >&2
    echo "  Coordinates must be multiples of 16, within 0-1024" >&2
    exit 1
fi

X1="$1"
Y1="$2"
X2="$3"
Y2="$4"

# Validate
validate_coords "$X1" "$Y1" "$X2" "$Y2" || exit 1

# Call checkOverlap(x1, y1, x2, y2)
# Returns true if ANY cell in the range is occupied
CALLDATA="${SEL_CHECK_OVERLAP}$(encode_uint16 "$X1")$(encode_uint16 "$Y1")$(encode_uint16 "$X2")$(encode_uint16 "$Y2")"
RESULT=$(eth_call "$CALLDATA")

if [ -z "$RESULT" ] || [ "$RESULT" = "null" ]; then
    echo '{"error": "Failed to query contract"}' >&2
    exit 1
fi

# checkOverlap returns true if occupied, false if available
IS_OCCUPIED=$(hex_to_dec "$RESULT")
if [ "$IS_OCCUPIED" -eq 0 ]; then
    AVAILABLE="true"
else
    AVAILABLE="false"
fi

WIDTH=$((X2 - X1))
HEIGHT=$((Y2 - Y1))

jq -n \
    --argjson available "$AVAILABLE" \
    --argjson x1 "$X1" \
    --argjson y1 "$Y1" \
    --argjson x2 "$X2" \
    --argjson y2 "$Y2" \
    --arg size "${WIDTH}x${HEIGHT}" \
    '{
        available: $available,
        x1: $x1,
        y1: $y1,
        x2: $x2,
        y2: $y2,
        size: $size
    }'
