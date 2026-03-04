#!/bin/bash
# Ori Funding Rate Scanner - Identifies perp opportunities via Orderly Network API
# Extreme funding rates can indicate mean reversion opportunities

set -e

# Configuration
ORDERLY_API="https://api-evm.orderly.org/v1"

echo "📈 Ori Funding Rate Scanner"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "Scanning Orderly Network perp funding rates..."
echo ""

# Get funding rates
funding_data=$(curl -s "${ORDERLY_API}/public/funding_rates")

if [ -z "$funding_data" ] || [ "$(echo "$funding_data" | jq -r '.success')" != "true" ]; then
    echo "❌ Failed to fetch funding rates"
    exit 1
fi

# Calculate hourly rate (funding is 8-hourly on most perps)
# Annualized = hourly * 24 * 365

echo "🔥 HIGH FUNDING (Longs paying shorts - short opportunity)"
echo "───────────────────────────────────────────────────────────────────────────────"
echo "$funding_data" | jq -r '
  .data.rows
  | sort_by(.last_funding_rate)
  | reverse
  | .[:10]
  | .[]
  | "\(.symbol) | Last: \(.last_funding_rate * 100 | . * 1000 | round / 1000)% | Est: \(.est_funding_rate * 100 | . * 1000 | round / 1000)%"
'

echo ""
echo "❄️ NEGATIVE FUNDING (Shorts paying longs - long opportunity)"
echo "───────────────────────────────────────────────────────────────────────────────"
echo "$funding_data" | jq -r '
  .data.rows
  | sort_by(.last_funding_rate)
  | .[:10]
  | .[]
  | "\(.symbol) | Last: \(.last_funding_rate * 100 | . * 1000 | round / 1000)% | Est: \(.est_funding_rate * 100 | . * 1000 | round / 1000)%"
'

echo ""
echo "💡 EXTREME RATES (annualized)"
echo "───────────────────────────────────────────────────────────────────────────────"

# Find symbols with extreme funding (annualized > 50% or < -50%)
echo "$funding_data" | jq -r '
  .data.rows
  | map(select(
      (.last_funding_rate > 0.0003) or (.last_funding_rate < -0.0003)
    ))
  | sort_by(.last_funding_rate)
  | reverse
  | .[]
  | "\(.symbol) | \(.last_funding_rate * 100 * 3 * 365 | . * 10 | round / 10)% APR"
'

if [ "$(echo "$funding_data" | jq '[.data.rows[] | select((.last_funding_rate > 0.0003) or (.last_funding_rate < -0.0003))] | length')" -eq 0 ]; then
    echo "(No extreme rates detected - market is relatively flat)"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "✅ Scan complete at $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo ""
echo "📖 How to read:"
echo "   - Positive funding = longs pay shorts (bearish crowd)"
echo "   - Negative funding = shorts pay longs (bullish crowd)"  
echo "   - Extreme rates often revert = contrarian signal"
