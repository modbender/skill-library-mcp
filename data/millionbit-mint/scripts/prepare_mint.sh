#!/usr/bin/env bash
# prepare_mint.sh - Full minting pipeline for Million Bit Homepage
#
# Prepares a complete transaction JSON that can be submitted via an EVM wallet skill.
#
# Usage: ./prepare_mint.sh <image_path> <x1> <y1> <x2> <y2> <url> [--dry-run]
#
# Steps:
#   1. Validate coordinates (16px boundaries, within 1024x1024)
#   2. Check/resize image to match plot dimensions
#   3. Check plot availability on-chain
#   4. Query current mint price
#   5. Encode pixel data (v1 format + pako compression)
#   6. ABI-encode the mint() calldata
#   7. Output transaction JSON
#
# Output: JSON with {to, value, data, chainId, description}
#
# Options:
#   --dry-run    Skip availability/price checks, just encode and output

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

# Parse arguments
DRY_RUN=false
POSITIONAL=()
for arg in "$@"; do
    case "$arg" in
        --dry-run)
            DRY_RUN=true
            ;;
        *)
            POSITIONAL+=("$arg")
            ;;
    esac
done

if [ "${#POSITIONAL[@]}" -lt 6 ]; then
    echo "Usage: $0 <image_path> <x1> <y1> <x2> <y2> <url> [--dry-run]" >&2
    echo "" >&2
    echo "Example: $0 logo.png 128 256 160 288 https://example.com" >&2
    echo "" >&2
    echo "This prepares a transaction JSON for minting a plot on the Million Bit Homepage." >&2
    echo "Submit the output to your EVM wallet skill to execute the mint." >&2
    exit 1
fi

IMAGE_PATH="${POSITIONAL[0]}"
X1="${POSITIONAL[1]}"
Y1="${POSITIONAL[2]}"
X2="${POSITIONAL[3]}"
Y2="${POSITIONAL[4]}"
URL="${POSITIONAL[5]}"

WIDTH=$((X2 - X1))
HEIGHT=$((Y2 - Y1))

# Step 1: Validate coordinates
echo "Validating coordinates..." >&2
validate_coords "$X1" "$Y1" "$X2" "$Y2" || exit 1

# Validate image exists
if [ ! -f "$IMAGE_PATH" ]; then
    echo "Error: Image file not found: $IMAGE_PATH" >&2
    exit 1
fi

# Step 2: Check image dimensions and resize if needed
echo "Checking image dimensions..." >&2
RESIZED_IMAGE="$IMAGE_PATH"
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

# Get image dimensions using sharp (via node one-liner)
IMG_INFO=$(node -e "
const sharp = require('sharp');
sharp('$IMAGE_PATH').metadata().then(m => {
    console.log(JSON.stringify({width: m.width, height: m.height}));
}).catch(e => { console.error(e.message); process.exit(1); });
")

IMG_WIDTH=$(echo "$IMG_INFO" | jq -r '.width')
IMG_HEIGHT=$(echo "$IMG_INFO" | jq -r '.height')

if [ "$IMG_WIDTH" -ne "$WIDTH" ] || [ "$IMG_HEIGHT" -ne "$HEIGHT" ]; then
    echo "Image is ${IMG_WIDTH}x${IMG_HEIGHT}, resizing to ${WIDTH}x${HEIGHT}..." >&2
    RESIZED_IMAGE="$TMPDIR/resized.png"
    "$SCRIPT_DIR/resize_image.sh" "$IMAGE_PATH" "$WIDTH" "$HEIGHT" "$RESIZED_IMAGE" >&2
fi

# Step 3: Check availability (skip in dry-run)
if [ "$DRY_RUN" = false ]; then
    echo "Checking plot availability at ($X1,$Y1)-($X2,$Y2)..." >&2
    AVAIL_JSON=$("$SCRIPT_DIR/check_availability.sh" "$X1" "$Y1" "$X2" "$Y2")
    AVAILABLE=$(echo "$AVAIL_JSON" | jq -r '.available')

    if [ "$AVAILABLE" != "true" ]; then
        echo "Error: Plot at ($X1,$Y1)-($X2,$Y2) is NOT available (already occupied)" >&2
        echo "$AVAIL_JSON"
        exit 1
    fi
    echo "Plot is available." >&2
fi

# Step 4: Query price (skip in dry-run)
PRICE_WEI="0"
PRICE_ETH="0"
if [ "$DRY_RUN" = false ]; then
    echo "Querying current mint price..." >&2
    PRICE_JSON=$("$SCRIPT_DIR/check_price.sh" "$X1" "$Y1" "$X2" "$Y2")
    PRICE_WEI=$(echo "$PRICE_JSON" | jq -r '.price_wei')
    PRICE_ETH=$(echo "$PRICE_JSON" | jq -r '.price_eth')
    echo "Price: $PRICE_ETH ETH ($PRICE_WEI wei)" >&2
fi

# Step 5: Encode pixel data
echo "Encoding pixel data..." >&2
PIXEL_FILE="$TMPDIR/pixels.bin"
ENCODE_JSON=$(node "$HELPERS_DIR/encode_pixels.js" "$RESIZED_IMAGE" "$X1" "$Y1" "$URL" --output "$PIXEL_FILE")
echo "Encoding: $(echo "$ENCODE_JSON" | jq -c '{segments, compression_ratio}')" >&2

# Step 6: ABI-encode mint calldata
echo "ABI-encoding mint calldata..." >&2
CALLDATA=$(node "$HELPERS_DIR/abi_encode.js" "$X1" "$Y1" "$X2" "$Y2" --pixel-file "$PIXEL_FILE")

# Step 7: Output transaction JSON
# Convert price to hex for the value field
VALUE_HEX=$(node -e "console.log('0x' + BigInt('$PRICE_WEI').toString(16))")

DESCRIPTION="Mint ${WIDTH}x${HEIGHT} plot at ($X1,$Y1) on Million Bit Homepage linking to $URL"

jq -n \
    --arg to "$CONTRACT" \
    --arg value "$VALUE_HEX" \
    --arg data "$CALLDATA" \
    --argjson chainId "$CHAIN_ID" \
    --arg description "$DESCRIPTION" \
    --arg price_eth "$PRICE_ETH" \
    --arg price_wei "$PRICE_WEI" \
    --arg size "${WIDTH}x${HEIGHT}" \
    --arg url "$URL" \
    '{
        to: $to,
        value: $value,
        data: $data,
        chainId: $chainId,
        description: $description,
        meta: {
            price_eth: $price_eth,
            price_wei: $price_wei,
            size: $size,
            url: $url
        }
    }'
