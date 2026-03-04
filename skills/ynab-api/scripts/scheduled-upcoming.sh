#!/bin/bash
# Show upcoming scheduled transactions
# Usage: ./scheduled-upcoming.sh [days]  # default: 7 days

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

DAYS="${1:-7}"
YNAB_API="https://api.ynab.com/v1"
TODAY=$(date -u '+%Y-%m-%d')
END_DATE=$(date -u -d "+$DAYS days" '+%Y-%m-%d')

# Get scheduled transactions
SCHEDULED=$(curl -s "$YNAB_API/budgets/$BUDGET_ID/scheduled_transactions" \
  -H "Authorization: Bearer $API_KEY")

# Check for errors
ERROR=$(echo "$SCHEDULED" | jq -r '.error.detail // empty')
if [ -n "$ERROR" ]; then
  echo "Error: $ERROR" >&2
  exit 1
fi

echo "📅 TRANSAZIONI PROGRAMMATE - Prossimi $DAYS giorni"
echo ""

# Filter and display upcoming transactions
UPCOMING=$(echo "$SCHEDULED" | jq -r --arg today "$TODAY" --arg end "$END_DATE" '
.data.scheduled_transactions[]
| select(.date_next >= $today and .date_next <= $end and .deleted == false)
| . as $tx
| ($tx.amount / 1000) as $amount
| if $amount < 0 then "💸" else "💰" end as $icon
| "\($tx.date_next) \($icon) \($tx.payee_name): €\($amount) - \($tx.memo // "N/A")"
' | sort)

if [ -z "$UPCOMING" ]; then
  echo "Nessuna transazione programmata nei prossimi $DAYS giorni"
else
  echo "$UPCOMING"
  echo ""
  
  # Calculate total
  TOTAL=$(echo "$SCHEDULED" | jq --arg today "$TODAY" --arg end "$END_DATE" '
  [.data.scheduled_transactions[]
  | select(.date_next >= $today and .date_next <= $end and .deleted == false)
  | .amount / 1000] | add // 0
  ')
  
  echo "---"
  echo "TOTALE: €$TOTAL"
fi
