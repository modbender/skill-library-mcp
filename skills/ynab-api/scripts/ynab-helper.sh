#!/bin/bash
# YNAB Helper Script
# Common operations for YNAB API

set -euo pipefail

# Load config
CONFIG_FILE="${YNAB_CONFIG:-$HOME/.config/ynab/config.json}"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "Error: Config file not found at $CONFIG_FILE"
  echo "Create a config file with: {\"api_key\": \"YOUR_KEY\", \"budget_id\": \"YOUR_BUDGET_ID\"}"
  exit 1
fi

API_KEY=$(jq -r '.api_key' "$CONFIG_FILE")
BUDGET_ID=$(jq -r '.budget_id' "$CONFIG_FILE")
YNAB_API="https://api.ynab.com/v1"

if [ -z "$API_KEY" ] || [ "$API_KEY" = "null" ]; then
  echo "Error: api_key not found in config"
  exit 1
fi

if [ -z "$BUDGET_ID" ] || [ "$BUDGET_ID" = "null" ]; then
  echo "Error: budget_id not found in config"
  exit 1
fi

# Commands
case "${1:-}" in
  search-payee)
    PAYEE="$2"
    curl -s "$YNAB_API/budgets/$BUDGET_ID/transactions" \
      -H "Authorization: Bearer $API_KEY" | \
      jq ".data.transactions[] | select(.payee_name | contains(\"$PAYEE\"))"
    ;;
    
  list-categories)
    curl -s "$YNAB_API/budgets/$BUDGET_ID/categories" \
      -H "Authorization: Bearer $API_KEY" | \
      jq '.data.category_groups[] | .name as $group | .categories[] | {group: $group, id: .id, name: .name}'
    ;;
    
  month-spending)
    MONTH="${2:-$(date +%Y-%m)}"
    curl -s "$YNAB_API/budgets/$BUDGET_ID/transactions?since_date=$MONTH-01" \
      -H "Authorization: Bearer $API_KEY" | \
      jq --arg month "$MONTH" '
        .data.transactions[] | 
        select(.date | startswith($month)) | 
        select(.amount < 0) | 
        select(.category_name != null) |
        # Add custom category exclusions here if needed:
        # select(.category_name != "CategoryToExclude") |
        {date, payee_name, category_name, amount: (.amount / -1000)}
      '
    ;;
    
  add-transaction)
    echo "Interactive transaction entry:"
    read -p "Account ID (or press Enter for default): " ACCOUNT_ID
    if [ -z "$ACCOUNT_ID" ]; then
      ACCOUNT_ID=$(jq -r '.default_account_id // .accounts[0]' "$CONFIG_FILE")
    fi
    
    read -p "Date (YYYY-MM-DD, default today): " DATE
    DATE="${DATE:-$(date +%Y-%m-%d)}"
    
    read -p "Amount (negative for expense): " AMOUNT
    AMOUNT_MILLI=$((AMOUNT * 1000))
    
    read -p "Payee name: " PAYEE
    read -p "Category ID: " CATEGORY_ID
    read -p "Memo (optional): " MEMO
    
    curl -X POST "$YNAB_API/budgets/$BUDGET_ID/transactions" \
      -H "Authorization: Bearer $API_KEY" \
      -H "Content-Type: application/json" \
      -d "{
        \"transaction\": {
          \"account_id\": \"$ACCOUNT_ID\",
          \"date\": \"$DATE\",
          \"amount\": $AMOUNT_MILLI,
          \"payee_name\": \"$PAYEE\",
          \"category_id\": \"$CATEGORY_ID\",
          \"memo\": \"$MEMO\",
          \"approved\": true
        }
      }" | jq .
    ;;
    
  *)
    cat <<EOF
YNAB Helper Script

Usage: $0 <command> [args]

Commands:
  search-payee <name>       - Find past transactions by payee
  list-categories           - List all budget categories with IDs
  month-spending [YYYY-MM]  - Show spending for a month (default: current)
  add-transaction           - Interactive transaction entry

Config: $CONFIG_FILE
  {
    "api_key": "YOUR_YNAB_API_KEY",
    "budget_id": "YOUR_BUDGET_ID",
    "default_account_id": "ACCOUNT_UUID" (optional)
  }

EOF
    exit 1
    ;;
esac
