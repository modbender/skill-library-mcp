#!/bin/bash
# Funding Tracker - Monitor funding payments and position PnL
# Usage: ./funding-tracker.sh [symbol]

SYMBOL="${1:-PERP_SPX500_USDC}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KEYS_FILE="${ORDERLY_KEYS_FILE:-$HOME/.orderly-keys.json}"
DATA_DIR="${ORDERLY_DATA_DIR:-$HOME/.orderly-data}"
FUNDING_LOG="$DATA_DIR/funding-history.json"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

if [[ ! -f "$KEYS_FILE" ]]; then
    echo "Error: Orderly keys not found at $KEYS_FILE"
    exit 1
fi

mkdir -p "$DATA_DIR"

# Get current funding rate
FUNDING_DATA=$(curl -s "https://api-evm.orderly.org/v1/public/funding_rate/$SYMBOL")
CURRENT_RATE=$(echo "$FUNDING_DATA" | jq -r '.data.est_funding_rate // 0')
LAST_RATE=$(echo "$FUNDING_DATA" | jq -r '.data.last_funding_rate // 0')
NEXT_TIME=$(echo "$FUNDING_DATA" | jq -r '.data.next_funding_time // 0')

# Convert to percentage and APR
RATE_PCT=$(echo "$LAST_RATE * 100" | bc -l 2>/dev/null || echo "0")
APR=$(echo "$LAST_RATE * 3 * 365 * 100" | bc -l 2>/dev/null || echo "0")

# Get position data via node
POSITION_DATA=$(ORDERLY_KEYS_FILE="$KEYS_FILE" node -e "
const crypto = require('crypto');
const fs = require('fs');

const keysFile = process.env.ORDERLY_KEYS_FILE || (process.env.HOME + '/.orderly-keys.json');
const keys = JSON.parse(fs.readFileSync(keysFile, 'utf8'));
const timestamp = Date.now();
const method = 'GET';
const urlPath = '/v1/positions';
const message = timestamp + method + urlPath;

const secretKeyBytes = Buffer.from(keys.priv_key_hex, 'hex');
const privateKey = crypto.createPrivateKey({
  key: Buffer.concat([
    Buffer.from('302e020100300506032b657004220420', 'hex'),
    secretKeyBytes
  ]),
  format: 'der',
  type: 'pkcs8'
});
const signature = crypto.sign(null, Buffer.from(message), privateKey).toString('base64');

fetch('https://api-evm.orderly.org/v1/positions', {
  headers: {
    'orderly-account-id': keys.account_id,
    'orderly-key': keys.orderly_key,
    'orderly-signature': signature,
    'orderly-timestamp': timestamp.toString()
  }
})
.then(r => r.json())
.then(d => console.log(JSON.stringify(d)));
" 2>/dev/null)

# Parse position
POS=$(echo "$POSITION_DATA" | jq -r ".data.rows[] | select(.symbol == \"$SYMBOL\")")

if [[ -z "$POS" || "$POS" == "null" ]]; then
    echo -e "${YELLOW}No position found for $SYMBOL${NC}"
    echo ""
    echo -e "${CYAN}Current Funding Rate: ${NC}${RATE_PCT:0:8}%"
    echo -e "${CYAN}Estimated APR: ${NC}${APR:0:6}%"
    exit 0
fi

# Extract position details
QTY=$(echo "$POS" | jq -r '.position_qty')
ENTRY=$(echo "$POS" | jq -r '.average_open_price')
MARK=$(echo "$POS" | jq -r '.mark_price')
PNL=$(echo "$POS" | jq -r '.unsettled_pnl')
LIQ=$(echo "$POS" | jq -r '.est_liq_price')
COST=$(echo "$POS" | jq -r '.cost_position')
TOTAL_COLLATERAL=$(echo "$POSITION_DATA" | jq -r '.data.total_collateral_value')
FREE_COLLATERAL=$(echo "$POSITION_DATA" | jq -r '.data.free_collateral')

# Calculate PnL percentage
PNL_PCT=$(echo "scale=4; $PNL / $COST * 100" | bc 2>/dev/null || echo "0")

# Determine side
if (( $(echo "$QTY > 0" | bc -l) )); then
    SIDE="LONG"
    SIDE_COLOR=$GREEN
else
    SIDE="SHORT"
    SIDE_COLOR=$RED
fi

# Calculate time to next funding
NOW=$(date +%s)
NEXT_SEC=$((NEXT_TIME / 1000))
TIME_DIFF=$((NEXT_SEC - NOW))
HOURS=$((TIME_DIFF / 3600))
MINS=$(( (TIME_DIFF % 3600) / 60 ))

# Expected funding payment per period
NOTIONAL=$(echo "$QTY * $MARK" | bc -l 2>/dev/null || echo "0")
if [[ "$SIDE" == "LONG" ]]; then
    # Long collects when rate is negative
    PAYMENT=$(echo "$NOTIONAL * $LAST_RATE * -1" | bc -l 2>/dev/null || echo "0")
else
    # Short collects when rate is positive  
    PAYMENT=$(echo "$NOTIONAL * $LAST_RATE" | bc -l 2>/dev/null || echo "0")
fi

# Display
echo ""
echo -e "═══════════════════════════════════════════════════"
echo -e "  ${CYAN}FUNDING TRACKER${NC} - $SYMBOL"
echo -e "═══════════════════════════════════════════════════"
echo ""
echo -e "📊 ${CYAN}Position${NC}"
echo -e "   Side: ${SIDE_COLOR}$SIDE${NC}"
echo -e "   Size: $QTY contracts"
echo -e "   Notional: \$${NOTIONAL:0:8}"
echo -e "   Entry: \$${ENTRY}"
echo -e "   Mark:  \$${MARK}"
echo ""
echo -e "💰 ${CYAN}P&L${NC}"
if (( $(echo "$PNL >= 0" | bc -l) )); then
    echo -e "   Unsettled: ${GREEN}+\$${PNL:0:8}${NC} (${PNL_PCT:0:6}%)"
else
    echo -e "   Unsettled: ${RED}\$${PNL:0:9}${NC} (${PNL_PCT:0:6}%)"
fi
echo -e "   Liquidation: \$${LIQ:0:10}"
echo ""
echo -e "📈 ${CYAN}Funding Rate${NC}"
echo -e "   Current: ${RATE_PCT:0:8}%"
echo -e "   APR: ${APR:0:6}%"
echo -e "   Next Payment: ${HOURS}h ${MINS}m"
if (( $(echo "$PAYMENT >= 0" | bc -l) )); then
    echo -e "   Expected: ${GREEN}+\$${PAYMENT:0:8}${NC} (you collect)"
else
    echo -e "   Expected: ${RED}\$${PAYMENT:0:8}${NC} (you pay)"
fi
echo ""
echo -e "💳 ${CYAN}Collateral${NC}"
echo -e "   Total: \$${TOTAL_COLLATERAL}"
echo -e "   Free: \$${FREE_COLLATERAL}"
echo ""

# Log to history
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
if [[ -f "$FUNDING_LOG" ]]; then
    HISTORY=$(cat "$FUNDING_LOG")
else
    HISTORY="[]"
fi

NEW_ENTRY=$(cat <<EOF
{
  "timestamp": "$TIMESTAMP",
  "symbol": "$SYMBOL",
  "side": "$SIDE",
  "qty": $QTY,
  "entry_price": $ENTRY,
  "mark_price": $MARK,
  "pnl": $PNL,
  "funding_rate": $LAST_RATE,
  "expected_payment": $PAYMENT,
  "total_collateral": $TOTAL_COLLATERAL
}
EOF
)

echo "$HISTORY" | jq ". + [$NEW_ENTRY]" > "$FUNDING_LOG" 2>/dev/null

echo -e "📝 Logged to data/funding-history.json"
echo ""
