#!/usr/bin/env bash
# check_price.sh - Query the current mint price for a plot on the Million Bit Homepage
#
# Usage:
#   ./check_price.sh <width> <height>          # Price for a plot of given size
#   ./check_price.sh <x1> <y1> <x2> <y2>      # Price for specific coordinates
#
# Output: JSON with price_wei, price_eth, pixels, size

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

# Parse arguments
if [ "$#" -eq 2 ]; then
    WIDTH="$1"
    HEIGHT="$2"
    X1=0
    Y1=0
    X2="$WIDTH"
    Y2="$HEIGHT"
elif [ "$#" -eq 4 ]; then
    X1="$1"
    Y1="$2"
    X2="$3"
    Y2="$4"
    WIDTH=$((X2 - X1))
    HEIGHT=$((Y2 - Y1))
else
    echo "Usage: $0 <width> <height>" >&2
    echo "       $0 <x1> <y1> <x2> <y2>" >&2
    exit 1
fi

# Validate
validate_coords "$X1" "$Y1" "$X2" "$Y2" || exit 1

# Call calculateCurrentPrice(x1, y1, x2, y2)
CALLDATA="${SEL_CALCULATE_PRICE}$(encode_uint16 "$X1")$(encode_uint16 "$Y1")$(encode_uint16 "$X2")$(encode_uint16 "$Y2")"
RESULT=$(eth_call "$CALLDATA")

if [ -z "$RESULT" ] || [ "$RESULT" = "null" ]; then
    echo '{"error": "Failed to query contract"}' >&2
    exit 1
fi

# Decode price (uint256 in hex)
PRICE_WEI=$(hex_to_dec "$RESULT")
PRICE_ETH=$(wei_to_eth "$PRICE_WEI")
PIXELS=$((WIDTH * HEIGHT))

# Also get totalSupply for context
SUPPLY_RESULT=$(eth_call "$SEL_TOTAL_SUPPLY")
TOTAL_SUPPLY=$(hex_to_dec "$SUPPLY_RESULT")

# Get basePrice
BASE_PRICE_RESULT=$(eth_call "$SEL_BASE_PRICE")
BASE_PRICE_WEI=$(hex_to_dec "$BASE_PRICE_RESULT")

# Output JSON
jq -n \
    --arg price_wei "$PRICE_WEI" \
    --arg price_eth "$PRICE_ETH" \
    --argjson pixels "$PIXELS" \
    --arg size "${WIDTH}x${HEIGHT}" \
    --argjson total_supply "$TOTAL_SUPPLY" \
    --arg base_price_wei "$BASE_PRICE_WEI" \
    '{
        price_wei: $price_wei,
        price_eth: $price_eth,
        pixels: $pixels,
        size: $size,
        total_supply: $total_supply,
        base_price_per_pixel_wei: $base_price_wei,
        note: "Price increases with each new mint. Larger plots = more pixels = higher cost but more visibility."
    }'
