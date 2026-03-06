#!/bin/bash
# funding-report.sh - Generate funding farming performance reports
# Usage: funding-report.sh [--daily|--weekly|--all]

set -e

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

DATA_DIR="${ORDERLY_DATA_DIR:-$HOME/.orderly-data}"
FUNDING_FILE="$DATA_DIR/funding-payments.json"
REPORT_DIR="$DATA_DIR/reports"

# Ensure directories exist
mkdir -p "$REPORT_DIR"
mkdir -p "data"

# Initialize funding payments file if doesn't exist
if [[ ! -f "$FUNDING_FILE" ]]; then
    echo '{"payments":[],"summary":{"totalCollected":0,"paymentCount":0,"startDate":null}}' > "$FUNDING_FILE"
fi

# Get period
PERIOD="${1:---all}"

echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  🍊 FUNDING FARMING REPORT${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
echo ""

# Fetch funding history from Orderly API directly
echo -e "${YELLOW}━━━ Fetching Funding History ━━━${NC}"

ACCOUNT_ID="0xa6d2117b3789119129dc061ac40c590e9a7eb0512854bc6f56549178636049f1"
PAYMENTS_RAW=$(curl -s "https://api-evm.orderly.org/v1/funding_fee/history?account_id=$ACCOUNT_ID" 2>/dev/null)
PAYMENTS=$(echo "$PAYMENTS_RAW" | jq -r '.data.rows // []' 2>/dev/null)

if [[ -z "$PAYMENTS" ]] || [[ "$PAYMENTS" == "[]" ]] || [[ "$PAYMENTS" == "null" ]]; then
    echo -e "${YELLOW}⏳ No funding payments received yet.${NC}"
    echo ""
    
    # Show current position and projections instead
    echo -e "${YELLOW}━━━ Current Position ━━━${NC}"
    bash tools/funding-tracker.sh 2>/dev/null | grep -E "Side|Size|Notional|Entry|Mark|Unsettled|Current|APR|Next|Expected" | head -15
else
    # Parse and display payments
    echo "$PAYMENTS" | jq -r '
        if type == "array" and length > 0 then
            "Found " + (length | tostring) + " funding payments:\n",
            (.[] | 
                "  " + (.created_time | tostring) + 
                " | " + .symbol + 
                " | " + (if .funding_fee < 0 then "+" else "-" end) + ((.funding_fee | fabs) | tostring) + " USDC"
            )
        else
            "No payments to display"
        end
    '
fi

# Calculate summary stats
echo ""
echo -e "${YELLOW}━━━ Summary Statistics ━━━${NC}"

if [[ -z "$PAYMENTS" ]] || [[ "$PAYMENTS" == "[]" ]] || [[ "$PAYMENTS" == "null" ]]; then
    TOTAL=0
    COUNT=0
    AVG=0
else
    TOTAL=$(echo "$PAYMENTS" | jq '[.[] | .funding_fee] | add // 0 | . * -1' 2>/dev/null || echo "0")
    COUNT=$(echo "$PAYMENTS" | jq 'length' 2>/dev/null || echo "0")
    AVG=$(echo "$PAYMENTS" | jq 'if length > 0 then ([.[] | .funding_fee] | add / length * -1) else 0 end' 2>/dev/null || echo "0")
fi

echo -e "  Total Collected: ${GREEN}\$$(printf '%.4f' $TOTAL)${NC}"
echo -e "  Payment Count:   $COUNT"
echo -e "  Average Payment: \$$(printf '%.4f' $AVG)"

# Project future earnings
echo ""
echo -e "${YELLOW}━━━ Projections ━━━${NC}"

# Get current funding rate and position data
FUNDING_DATA=$(curl -s "https://api-evm.orderly.org/v1/public/funding_rate/PERP_SPX500_USDC" 2>/dev/null)
FUNDING_RATE=$(echo "$FUNDING_DATA" | jq -r '.data.last_funding_rate // -0.00165')
MARK_PRICE=$(echo "$FUNDING_DATA" | jq -r '.data.mark_price // 6912')

# Default position size (we know we have 0.002)
POSITION_SIZE="0.002"

# Calculate projections using bc with proper scale
NOTIONAL=$(echo "scale=4; $POSITION_SIZE * $MARK_PRICE" | bc 2>/dev/null || echo "13.82")
# For negative funding rate, we collect (multiply by -1 to make it positive income)
RATE_ABS=$(echo "$FUNDING_RATE" | sed 's/-//')
PAYMENT_8H=$(echo "scale=6; $NOTIONAL * $RATE_ABS" | bc 2>/dev/null || echo "0.023")
PAYMENT_DAILY=$(echo "scale=6; $PAYMENT_8H * 3" | bc 2>/dev/null || echo "0.069")
PAYMENT_WEEKLY=$(echo "scale=4; $PAYMENT_DAILY * 7" | bc 2>/dev/null || echo "0.483")
PAYMENT_MONTHLY=$(echo "scale=2; $PAYMENT_DAILY * 30" | bc 2>/dev/null || echo "2.07")

echo -e "  Per 8h:    ${GREEN}\$$(printf '%.4f' $PAYMENT_8H)${NC}"
echo -e "  Per Day:   ${GREEN}\$$(printf '%.4f' $PAYMENT_DAILY)${NC}"
echo -e "  Per Week:  ${GREEN}\$$(printf '%.4f' $PAYMENT_WEEKLY)${NC}"
echo -e "  Per Month: ${GREEN}\$$(printf '%.2f' $PAYMENT_MONTHLY)${NC}"

# APR calculation
DEPOSIT=3
APR=$(echo "scale=1; $PAYMENT_MONTHLY * 12 / $DEPOSIT * 100" | bc 2>/dev/null || echo "180")
echo ""
echo -e "  Annualized Return: ${GREEN}$(printf '%.1f' $APR)%${NC} on \$${DEPOSIT} deposit"

# Save report
REPORT_FILE="$REPORT_DIR/funding-report-$(date +%Y-%m-%d).md"
cat > "$REPORT_FILE" << EOF
# Funding Farming Report - $(date +%Y-%m-%d)

## Summary
- **Total Collected:** \$$(printf '%.4f' $TOTAL)
- **Payment Count:** $COUNT
- **Average Payment:** \$$(printf '%.4f' $AVG)

## Projections (Current Rate)
- Per 8h: \$$(printf '%.4f' $PAYMENT_8H)
- Per Day: \$$(printf '%.4f' $PAYMENT_DAILY)
- Per Week: \$$(printf '%.4f' $PAYMENT_WEEKLY)
- Per Month: \$$(printf '%.2f' $PAYMENT_MONTHLY)

## Position
- Symbol: PERP_SPX500_USDC
- Side: LONG
- Size: $POSITION_SIZE contracts
- Notional: ~\$$NOTIONAL
- Funding Rate: ${FUNDING_RATE}/8h

## Notes
Report generated at $(date -u +"%Y-%m-%dT%H:%M:%SZ")
EOF

echo ""
echo -e "${CYAN}Report saved: $REPORT_FILE${NC}"
echo ""
