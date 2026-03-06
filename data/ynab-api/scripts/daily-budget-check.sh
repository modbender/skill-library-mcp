#!/bin/bash
# Daily budget check - comprehensive morning report
# Designed to be called by cron job with proper error handling

# Load config
if [ -f ~/.config/ynab/config.json ]; then
  API_KEY=$(jq -r '.api_key' ~/.config/ynab/config.json)
  BUDGET_ID=$(jq -r '.budget_id // "last-used"' ~/.config/ynab/config.json)
elif [ -f /home/node/clawd/config/ynab.json ]; then
  API_KEY=$(jq -r '.api_key' /home/node/clawd/config/ynab.json)
  BUDGET_ID="${YNAB_BUDGET_ID:-last-used}"
else
  echo "❌ Errore configurazione: file YNAB non trovato"
  exit 0  # Exit gracefully, don't crash cron job
fi

YNAB_API="https://api.ynab.com/v1"
TODAY=$(date -u '+%Y-%m-%d')
TOMORROW=$(date -u -d "+1 day" '+%Y-%m-%d')
END_7_DAYS=$(date -u -d "+7 days" '+%Y-%m-%d')

# Retry function for API calls
api_call() {
  local url="$1"
  local max_retries=3
  local retry_delay=2
  local response
  
  for i in $(seq 1 $max_retries); do
    response=$(curl -s -w "\n%{http_code}" "$url" -H "Authorization: Bearer $API_KEY")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
      echo "$body"
      return 0
    fi
    
    # Check if it's an error we should retry
    if [ "$http_code" = "429" ] || [ "$http_code" = "500" ] || [ "$http_code" = "502" ] || [ "$http_code" = "503" ]; then
      if [ $i -lt $max_retries ]; then
        sleep $retry_delay
        retry_delay=$((retry_delay * 2))
        continue
      fi
    fi
    
    # Non-retryable error or max retries reached
    echo "ERROR:$http_code" >&2
    return 1
  done
}

# Get current month data with error handling
MONTH_DATA=$(api_call "$YNAB_API/budgets/$BUDGET_ID/months/current")
if [ $? -ne 0 ]; then
  echo "*⚠️ BUDGET CHECK MATTUTINO*"
  echo ""
  echo "❌ Impossibile recuperare dati YNAB"
  echo ""
  echo "L'API YNAB non è al momento raggiungibile."
  echo "Riproverò domani alle 07:15."
  echo ""
  echo "_Ultimo tentativo: $(date '+%Y-%m-%d %H:%M')_"
  exit 0  # Graceful exit
fi

# Get scheduled transactions with error handling
SCHEDULED=$(api_call "$YNAB_API/budgets/$BUDGET_ID/scheduled_transactions")
if [ $? -ne 0 ]; then
  # Continue without scheduled transactions data
  SCHEDULED="{}"
fi

# Build report
echo "*☀️ BUDGET CHECK MATTUTINO*"
echo ""

# Age of Money
AGE_OF_MONEY=$(echo "$MONTH_DATA" | jq -r '.data.month.age_of_money // 0')
if [ "$AGE_OF_MONEY" -ge 120 ]; then
  AOM_ICON="✅"
elif [ "$AGE_OF_MONEY" -ge 60 ]; then
  AOM_ICON="🟡"
else
  AOM_ICON="⚠️"
fi
echo "*💰 Age of Money: $AGE_OF_MONEY giorni* $AOM_ICON"
echo ""

# Upcoming scheduled transactions (next 7 days)
UPCOMING_COUNT=$(echo "$SCHEDULED" | jq --arg today "$TODAY" --arg enddate "$END_7_DAYS" '[.data.scheduled_transactions[]? | select(.date_next >= $today and .date_next <= $enddate and .deleted == false)] | length' 2>/dev/null || echo "0")

if [ "$UPCOMING_COUNT" -gt 0 ]; then
  echo "*📅 Prossime uscite (7gg)*"
  echo "$SCHEDULED" | jq -r --arg today "$TODAY" --arg tomorrow "$TOMORROW" --arg enddate "$END_7_DAYS" '
  .data.scheduled_transactions[]?
  | select(.date_next >= $today and .date_next <= $enddate and .deleted == false and .amount < 0)
  | . as $tx
  | ($tx.amount / -1000) as $amount
  | if $tx.date_next == $today then "• Oggi: " elif $tx.date_next == $tomorrow then "• Domani: " else "• \($tx.date_next): " end + "\($tx.payee_name) €\($amount)"
  ' 2>/dev/null | head -5
  echo ""
fi

# Overspending alerts
OVERSPENT=$(echo "$MONTH_DATA" | jq -r '
.data.month.categories[]
| select(.goal_type != null and .deleted == false)
| . as $cat
| ($cat.activity / -1000) as $spent
| ($cat.goal_target / 1000) as $target
| if $target > 0 and $spent > $target then
    "\($cat.name): €\($spent | floor) / €\($target) (+€\(($spent - $target) | floor))"
  else empty end
' 2>/dev/null | head -3)

if [ -n "$OVERSPENT" ]; then
  echo "*⚠️ Alert Budget Superato*"
  echo "$OVERSPENT" | while IFS= read -r line; do
    echo "• $line"
  done
  echo ""
fi

# Goals needing attention (< 20% complete and significant target)
GOALS_LOW=$(echo "$MONTH_DATA" | jq -r '
.data.month.categories[]
| select(.goal_type != null and .deleted == false)
| . as $cat
| ($cat.activity / -1000) as $spent
| ($cat.goal_target / 1000) as $target
| if $target >= 100 then
    ($spent / $target * 100) as $pct
    | if $pct < 20 then
        "\($cat.name): \($pct | floor)% (€\($spent | floor)/€\($target))"
      else empty end
  else empty end
' 2>/dev/null | head -3)

if [ -n "$GOALS_LOW" ]; then
  echo "*🎯 Obiettivi in ritardo*"
  echo "$GOALS_LOW" | while IFS= read -r line; do
    echo "• $line"
  done
  echo ""
fi

# To be budgeted
TO_BE_BUDGETED=$(echo "$MONTH_DATA" | jq -r '.data.month.to_be_budgeted / 1000' 2>/dev/null || echo "0")
if (( $(awk -v n="$TO_BE_BUDGETED" 'BEGIN {print (n > 0)}') )); then
  echo "*💵 Da assegnare: €$TO_BE_BUDGETED*"
fi

exit 0
