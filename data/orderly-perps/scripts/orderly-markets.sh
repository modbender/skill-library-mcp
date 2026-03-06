#!/bin/bash
# Ori Orderly Markets Scanner
# Shows perp pairs with key metrics: price, 24h change, volume, OI, funding
# Usage: ./orderly-markets.sh [sort_by] [limit]
# sort_by: volume, oi, funding (default: volume)
# limit: number of results (default: 15)

set -euo pipefail

SORT_BY="${1:-volume}"
LIMIT="${2:-15}"

echo "📊 Ori Orderly Markets Scanner"
echo "═══════════════════════════════════════════════════════════════════════════════════════"
echo "Fetching perp data from Orderly Network..."
echo ""

# Popular trading pairs to query (majors + trending)
SYMBOLS=(
    "PERP_BTC_USDC"
    "PERP_ETH_USDC"
    "PERP_SOL_USDC"
    "PERP_DOGE_USDC"
    "PERP_XRP_USDC"
    "PERP_LINK_USDC"
    "PERP_SUI_USDC"
    "PERP_HYPE_USDC"
    "PERP_TRUMP_USDC"
    "PERP_WIF_USDC"
    "PERP_1000PEPE_USDC"
    "PERP_FARTCOIN_USDC"
    "PERP_VIRTUAL_USDC"
    "PERP_AIXBT_USDC"
    "PERP_GOAT_USDC"
    "PERP_TAO_USDC"
    "PERP_H_USDC"
    "PERP_SKR_USDC"
    "PERP_ZORA_USDC"
    "PERP_ARB_USDC"
    "PERP_OP_USDC"
    "PERP_AVAX_USDC"
    "PERP_BNB_USDC"
    "PERP_NEAR_USDC"
    "PERP_BERA_USDC"
    "PERP_PENDLE_USDC"
    "PERP_JUP_USDC"
    "PERP_TON_USDC"
    "PERP_FET_USDC"
    "PERP_CRV_USDC"
)

# Temp file for results
TMPFILE=$(mktemp)
trap "rm -f $TMPFILE" EXIT

# Fetch all symbols sequentially (more reliable than parallel)
for symbol in "${SYMBOLS[@]}"; do
    data=$(curl -s --max-time 5 "https://api-evm.orderly.org/v1/public/futures/${symbol}" 2>/dev/null || echo "")
    if [ -n "$data" ] && echo "$data" | jq -e '.success == true' >/dev/null 2>&1; then
        echo "$data" | jq -r '
            .data |
            [
                .symbol,
                .mark_price,
                .index_price,
                ."24h_volume",
                ."24h_amount",
                .open_interest,
                ((."24h_close" - ."24h_open") / ."24h_open" * 100),
                (.last_funding_rate * 3 * 365 * 100),
                .est_funding_rate
            ] | @tsv
        ' >> "$TMPFILE" 2>/dev/null || true
    fi
done

# Check if we got data
if [ ! -s "$TMPFILE" ]; then
    echo "❌ No data received from Orderly API"
    exit 1
fi

# Print header
printf "%-14s │ %12s │ %8s │ %12s │ %12s │ %12s\n" \
    "Symbol" "Price" "24h %" "Volume" "OI (USD)" "Funding APR"
echo "───────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────"

# Process results with sorting
if [ "$SORT_BY" == "funding" ]; then
    # Sort by absolute value of funding
    sorted_data=$(awk -F'\t' '{
        abs_funding = ($8 < 0) ? -$8 : $8
        print abs_funding "\t" $0
    }' "$TMPFILE" | sort -t$'\t' -k1 -rn | cut -f2- | head -n "$LIMIT")
else
    sort_field=5  # default: amount (volume)
    case "$SORT_BY" in
        oi) sort_field=6 ;;
        change) sort_field=7 ;;
    esac
    sorted_data=$(sort -t$'\t' -k${sort_field} -rn "$TMPFILE" | head -n "$LIMIT")
fi

echo "$sorted_data" | while IFS=$'\t' read -r symbol mark_price index_price vol24h amount24h oi change24h funding_apr est_funding; do
    [ -z "$symbol" ] && continue
    
    # Format symbol
    display=$(echo "$symbol" | sed 's/PERP_//' | sed 's/_USDC//')
    
    # Format price
    if (( $(echo "$mark_price >= 1000" | bc -l 2>/dev/null || echo 0) )); then
        price_fmt=$(printf "%.0f" "$mark_price")
    elif (( $(echo "$mark_price >= 1" | bc -l 2>/dev/null || echo 0) )); then
        price_fmt=$(printf "%.2f" "$mark_price")
    elif (( $(echo "$mark_price >= 0.001" | bc -l 2>/dev/null || echo 0) )); then
        price_fmt=$(printf "%.5f" "$mark_price")
    else
        price_fmt=$(printf "%.8f" "$mark_price")
    fi
    
    # Format change
    change_fmt=$(printf "%+.2f%%" "$change24h")
    
    # Format volume
    if (( $(echo "$amount24h >= 1000000" | bc -l 2>/dev/null || echo 0) )); then
        vol_fmt=$(printf "%.1fM" "$(echo "$amount24h / 1000000" | bc -l)")
    elif (( $(echo "$amount24h >= 1000" | bc -l 2>/dev/null || echo 0) )); then
        vol_fmt=$(printf "%.1fK" "$(echo "$amount24h / 1000" | bc -l)")
    else
        vol_fmt=$(printf "%.0f" "$amount24h")
    fi
    
    # Format OI in USD
    oi_usd=$(echo "$oi * $index_price" | bc -l 2>/dev/null || echo 0)
    if (( $(echo "$oi_usd >= 1000000" | bc -l 2>/dev/null || echo 0) )); then
        oi_fmt=$(printf "%.1fM" "$(echo "$oi_usd / 1000000" | bc -l)")
    elif (( $(echo "$oi_usd >= 1000" | bc -l 2>/dev/null || echo 0) )); then
        oi_fmt=$(printf "%.1fK" "$(echo "$oi_usd / 1000" | bc -l)")
    else
        oi_fmt=$(printf "%.0f" "$oi_usd")
    fi
    
    # Format funding with indicator
    funding_fmt=$(printf "%+.1f%%" "$funding_apr")
    if (( $(echo "$funding_apr > 20" | bc -l 2>/dev/null || echo 0) )); then
        funding_indicator="🔴"  # High positive = longs paying
    elif (( $(echo "$funding_apr < -20" | bc -l 2>/dev/null || echo 0) )); then
        funding_indicator="🟢"  # High negative = shorts paying
    else
        funding_indicator="⚪"
    fi
    
    printf "%-14s │ %12s │ %8s │ %12s │ %12s │ %s %9s\n" \
        "$display" "$price_fmt" "$change_fmt" "$vol_fmt" "$oi_fmt" "$funding_indicator" "$funding_fmt"
done

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════════════"
echo "🟢 = Negative funding (shorts paying longs - bullish signal)"
echo "🔴 = Positive funding (longs paying shorts - bearish signal)"
echo ""
echo "Sorted by: $SORT_BY | Top $LIMIT pairs | Scanned ${#SYMBOLS[@]} markets"
echo "Data: Orderly Network (api-evm.orderly.org)"
