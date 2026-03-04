#!/bin/bash
# NOFX Market Report Generator
# Usage: ./generate-report.sh [format]
# format: brief | full (default: brief)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_SCRIPT="$SCRIPT_DIR/nofx-api.sh"

format="${1:-brief}"

# Fetch all data
ai500=$("$API_SCRIPT" ai500 2>/dev/null)
ai300=$("$API_SCRIPT" ai300 10 2>/dev/null)
flow_in=$("$API_SCRIPT" flow-in 10 1h institution 2>/dev/null)
oi_up=$("$API_SCRIPT" oi-up 10 1h 2>/dev/null)
oi_down=$("$API_SCRIPT" oi-down 10 1h 2>/dev/null)
price=$("$API_SCRIPT" price 1h 2>/dev/null)

# Get current time
timestamp=$(date "+%Y-%m-%d %H:%M")

# Generate report
cat << EOF
📊 **NOFX Market Report | $timestamp**

---

🤖 **AI500 High Potential Signals**
EOF

echo "$ai500" | jq -r '
  .data.coins[:5] | 
  "| Coin | AI Score | Cumulative Gain |",
  "|------|----------|-----------------|",
  (.[] | "| \(.pair | gsub("USDT$";"")) | \(.score | . * 100 | floor / 100) | +\(.increase_percent | . * 100 | floor / 100)% |")
' 2>/dev/null || echo "No AI500 data"

cat << EOF

---

💰 **Institutional Inflow TOP10** (1h)
EOF

echo "$flow_in" | jq -r '
  .data.netflows[:10] | to_entries | 
  .[] | 
  "\(.key + 1). \(.value.symbol | gsub("USDT$";"")) +$\((.value.amount / 1000000) | . * 100 | floor / 100)M"
' 2>/dev/null || echo "No flow data"

cat << EOF

---

🚀 **1h Gainers TOP10**
EOF

echo "$price" | jq -r '
  .data.data["1h"].top[:10] | to_entries |
  .[] |
  "\(.key + 1). \(.value.symbol) +\((.value.price_delta * 100) | . * 100 | floor / 100)%"
' 2>/dev/null || echo "No price data"

cat << EOF

---

📈 **1h OI Increase TOP10**
EOF

echo "$oi_up" | jq -r '
  .data.positions[:10] | to_entries |
  .[] |
  "\(.key + 1). \(.value.symbol | gsub("USDT$";"")) +$\((.value.oi_delta_value / 1000000) | . * 100 | floor / 100)M"
' 2>/dev/null || echo "No OI data"

cat << EOF

---

📉 **1h OI Decrease TOP10**
EOF

echo "$oi_down" | jq -r '
  .data.positions[:10] | to_entries |
  .[] |
  "\(.key + 1). \(.value.symbol | gsub("USDT$";"")) $\((.value.oi_delta_value / 1000000) | . * 100 | floor / 100)M"
' 2>/dev/null || echo "No OI data"

# Price losers / alerts
losers=$(echo "$price" | jq -r '.data.data["1h"].top | map(select(.price_delta < -0.05)) | .[:5]' 2>/dev/null)
if [ -n "$losers" ] && [ "$losers" != "[]" ]; then
cat << EOF

---

⚠️ **Drop Alert**
EOF
echo "$losers" | jq -r '.[] | "- 🔴 \(.symbol) \((.price_delta * 100) | . * 100 | floor / 100)%"' 2>/dev/null
fi

echo ""
echo "---"
