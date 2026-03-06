#!/bin/bash
# Create a transfer between two YNAB accounts
# Usage: ./transfer.sh SOURCE_ACCOUNT_ID DEST_ACCOUNT_NAME AMOUNT_EUROS DATE [MEMO]

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

SOURCE_ACCOUNT_ID="$1"
DEST_ACCOUNT_NAME="$2"
AMOUNT_EUROS="$3"
DATE="$4"
MEMO="${5:-Transfer}"

if [ -z "$SOURCE_ACCOUNT_ID" ] || [ -z "$DEST_ACCOUNT_NAME" ] || [ -z "$AMOUNT_EUROS" ] || [ -z "$DATE" ]; then
  echo "Usage: $0 SOURCE_ACCOUNT_ID DEST_ACCOUNT_NAME AMOUNT_EUROS DATE [MEMO]" >&2
  echo "Example: $0 abc123 'Savings' 100.50 2026-02-21 'Monthly savings'" >&2
  exit 1
fi

YNAB_API="https://api.ynab.com/v1"

# Convert euros to milliunits (negative for outbound transfer)
AMOUNT_MILLIUNITS=$(echo "$AMOUNT_EUROS * -1000" | bc | cut -d. -f1)

# Get destination account's transfer_payee_id
echo "Getting transfer payee ID for '$DEST_ACCOUNT_NAME'..." >&2
TRANSFER_PAYEE_ID=$(curl -s "$YNAB_API/budgets/$BUDGET_ID/accounts" \
  -H "Authorization: Bearer $API_KEY" | \
  jq -r ".data.accounts[] | select(.name == \"$DEST_ACCOUNT_NAME\") | .transfer_payee_id")

if [ -z "$TRANSFER_PAYEE_ID" ] || [ "$TRANSFER_PAYEE_ID" = "null" ]; then
  echo "Error: Account '$DEST_ACCOUNT_NAME' not found or has no transfer_payee_id" >&2
  exit 1
fi

echo "Creating transfer: €$AMOUNT_EUROS from $SOURCE_ACCOUNT_ID to $DEST_ACCOUNT_NAME..." >&2

# Create transfer transaction
RESPONSE=$(curl -s -X POST "$YNAB_API/budgets/$BUDGET_ID/transactions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"transaction\": {
      \"account_id\": \"$SOURCE_ACCOUNT_ID\",
      \"date\": \"$DATE\",
      \"amount\": $AMOUNT_MILLIUNITS,
      \"payee_id\": \"$TRANSFER_PAYEE_ID\",
      \"memo\": \"$MEMO\",
      \"approved\": true
    }
  }")

# Check for errors
ERROR=$(echo "$RESPONSE" | jq -r '.error // empty')
if [ -n "$ERROR" ]; then
  echo "Error: $ERROR" >&2
  echo "$RESPONSE" | jq . >&2
  exit 1
fi

# Show result
TRANSACTION_ID=$(echo "$RESPONSE" | jq -r '.data.transaction.id')
TRANSFER_TRANSACTION_ID=$(echo "$RESPONSE" | jq -r '.data.transaction.transfer_transaction_id')

echo "✅ Transfer created successfully!" >&2
echo "Outbound transaction ID: $TRANSACTION_ID" >&2
echo "Inbound transaction ID: $TRANSFER_TRANSACTION_ID" >&2
echo "$RESPONSE" | jq .
