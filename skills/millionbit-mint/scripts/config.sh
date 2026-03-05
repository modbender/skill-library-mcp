#!/usr/bin/env bash
# Shared configuration for Million Bit Homepage OpenClaw skill scripts

# Contract and network
CONTRACT="0x25b9afe64bb3593ec7e9dc7ef386a9b04c53f96e"
RPC_URL="https://mainnet.base.org"
CHAIN_ID=8453

# Grid constants
GRID_UNIT=16
CANVAS_SIZE=1024
GRID_CELLS=64  # 1024 / 16

# Function selectors (first 4 bytes of keccak256 of canonical signature)
SEL_CALCULATE_PRICE="08588f5b"   # calculateCurrentPrice(uint16,uint16,uint16,uint16)
SEL_CHECK_OVERLAP="84bd3031"     # checkOverlap(uint16,uint16,uint16,uint16)
SEL_BASE_PRICE="c7876ea4"        # basePrice()
SEL_PRICE_INCREMENT="280d62ac"   # priceIncrement()
SEL_TOTAL_SUPPLY="18160ddd"      # totalSupply()
SEL_MINT="dd2e6e7d"              # mint(uint16,uint16,uint16,uint16,string)

# Resolve the directory this script lives in
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HELPERS_DIR="$SCRIPT_DIR/helpers"

# Encode a uint16 value as a 64-char hex string (32 bytes, left-padded with zeros)
encode_uint16() {
    printf "%064x" "$1"
}

# Make an eth_call to the contract and return the raw hex result
# Usage: eth_call <calldata_hex_no_prefix>
eth_call() {
    local calldata="0x$1"
    local payload
    payload=$(jq -n \
        --arg to "$CONTRACT" \
        --arg data "$calldata" \
        '{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":$to,"data":$data},"latest"]}')

    local response
    response=$(curl -s -X POST "$RPC_URL" \
        -H "Content-Type: application/json" \
        -d "$payload")

    echo "$response" | jq -r '.result'
}

# Decode a hex uint256 result to decimal (uses node for big numbers)
hex_to_dec() {
    local hex="${1#0x}"
    node -e "console.log(BigInt('0x${hex}').toString())"
}

# Convert wei to ETH (18 decimals) using node
wei_to_eth() {
    local wei="$1"
    node -e "
        const w = BigInt('$wei');
        const eth = Number(w) / 1e18;
        console.log(eth.toFixed(18));
    "
}

# Validate that a value is a multiple of GRID_UNIT (16)
validate_grid_aligned() {
    local val="$1"
    local name="$2"
    if (( val % GRID_UNIT != 0 )); then
        echo "Error: $name ($val) must be a multiple of $GRID_UNIT" >&2
        return 1
    fi
    if (( val < 0 || val > CANVAS_SIZE )); then
        echo "Error: $name ($val) must be between 0 and $CANVAS_SIZE" >&2
        return 1
    fi
    return 0
}

# Validate a complete set of coordinates
validate_coords() {
    local x1="$1" y1="$2" x2="$3" y2="$4"
    validate_grid_aligned "$x1" "x1" || return 1
    validate_grid_aligned "$y1" "y1" || return 1
    validate_grid_aligned "$x2" "x2" || return 1
    validate_grid_aligned "$y2" "y2" || return 1
    if (( x2 <= x1 )); then
        echo "Error: x2 ($x2) must be greater than x1 ($x1)" >&2
        return 1
    fi
    if (( y2 <= y1 )); then
        echo "Error: y2 ($y2) must be greater than y1 ($y1)" >&2
        return 1
    fi
    return 0
}
