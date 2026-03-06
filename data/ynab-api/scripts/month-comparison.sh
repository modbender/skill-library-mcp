#!/bin/bash
# Compare spending between two months
# Usage: ./month-comparison.sh [month1] [month2]  # default: current vs last month

set -e

# Load config
if [ -f ~/.config/ynab/config.json ]; then
  API_KEY=$(jq -r '.api_key' ~/.config/ynab/config.json)
  BUDGET_ID=$(jq -r '.budget_id // "last-used"' ~/.config/ynab/config.json)
elif [ -f /home/node/clawd/config/ynab.json ]; then
  API_KEY=$(jq -r '.api_key' /home/node/clawd/config/ynab.json)
  BUDGET_ID="${YNAB_BUDGET_ID:-last-used}"
else
  echo "Error: YNAB config not found" >&2
  exit 1
fi

YNAB_API="https://api.ynab.com/v1"

# Default: current month vs last month
if [ -z "$1" ]; then
  MONTH1=$(date -u '+%Y-%m-01')
  MONTH2=$(date -u -d "$(date -u '+%Y-%m-01') -1 month" '+%Y-%m-01')
else
  MONTH1="$1"
  MONTH2="$2"
fi

# Get month data
MONTH1_DATA=$(curl -s "$YNAB_API/budgets/$BUDGET_ID/months/$MONTH1" \
  -H "Authorization: Bearer $API_KEY")
MONTH2_DATA=$(curl -s "$YNAB_API/budgets/$BUDGET_ID/months/$MONTH2" \
  -H "Authorization: Bearer $API_KEY")

MONTH1_NAME=$(echo "$MONTH1_DATA" | jq -r '.data.month.month')
MONTH2_NAME=$(echo "$MONTH2_DATA" | jq -r '.data.month.month')

echo "📊 CONFRONTO SPESE"
echo "$MONTH1_NAME vs $MONTH2_NAME"
echo ""

# Combine categories from both months
CATEGORIES=$(echo "$MONTH1_DATA" "$MONTH2_DATA" | jq -s '
[.[0].data.month.categories[], .[1].data.month.categories[]]
| group_by(.id)
| map(select(.[0].deleted == false))
| map({
    name: .[0].name,
    id: .[0].id,
    activity_m1: (if .[0].month == "'"$MONTH1_NAME"'" then .[0].activity else (.[1].activity // 0) end),
    activity_m2: (if .[0].month == "'"$MONTH2_NAME"'" then (.[1].activity // 0) else .[0].activity end)
  })
')

# Calculate and display differences
echo "$CATEGORIES" | jq -r '
sort_by(-.activity_m1) | .[]
| ($m1: .activity_m1 / -1000) as $spent_m1
| ($m2: .activity_m2 / -1000) as $spent_m2
| if $spent_m1 > 0 or $spent_m2 > 0 then
    if $spent_m2 > 0 then
      (($spent_m1 - $spent_m2) / $spent_m2 * 100) as $pct_change
      | if $pct_change > 20 then "⚠️" elif $pct_change > 0 then "↗️" elif $pct_change < -20 then "✅" elif $pct_change < 0 then "↘️" else "=" end as $icon
      | "\(.name): €\($spent_m1 | floor) (era €\($spent_m2 | floor)) \($icon) \(if $pct_change > 0 then "+" else "" end)\($pct_change | floor)%"
    else
      "\(.name): €\($spent_m1 | floor) (nuova spesa)"
    end
  else empty end
' | head -15

# Total comparison
TOTAL_M1=$(echo "$MONTH1_DATA" | jq '[.data.month.categories[] | select(.activity < 0) | .activity] | add // 0 | . / -1000')
TOTAL_M2=$(echo "$MONTH2_DATA" | jq '[.data.month.categories[] | select(.activity < 0) | .activity] | add // 0 | . / -1000')

echo ""
echo "---"
echo "TOTALE $MONTH1_NAME: €$TOTAL_M1"
echo "TOTALE $MONTH2_NAME: €$TOTAL_M2"

if (( $(echo "$TOTAL_M2 > 0" | bc -l) )); then
  DIFF=$(echo "$TOTAL_M1 - $TOTAL_M2" | bc)
  PCT=$(echo "scale=1; ($TOTAL_M1 - $TOTAL_M2) / $TOTAL_M2 * 100" | bc)
  if (( $(echo "$DIFF > 0" | bc -l) )); then
    echo "Differenza: +€$DIFF (+$PCT%)"
  else
    echo "Differenza: €$DIFF ($PCT%)"
  fi
fi
