#!/bin/bash
# View your API usage statistics

WALLET_FILE="$HOME/.apiosk/wallet.json"
CONFIG_FILE="$HOME/.apiosk/config.json"

if [ ! -f "$WALLET_FILE" ]; then
  echo "❌ Wallet not found. Run ./setup-wallet.sh first"
  exit 1
fi

WALLET_ADDRESS=$(jq -r '.address' "$WALLET_FILE")
GATEWAY_URL=$(jq -r '.gateway_url' "$CONFIG_FILE")

# Parse arguments
PERIOD="all"
if [ "$1" == "--today" ]; then
  PERIOD="today"
elif [ "$1" == "--week" ]; then
  PERIOD="week"
elif [ "$1" == "--month" ]; then
  PERIOD="month"
fi

echo "🦞 Apiosk Usage Stats ($PERIOD)"
echo ""

# Fetch usage
USAGE=$(curl -s "$GATEWAY_URL/v1/usage?address=$WALLET_ADDRESS&period=$PERIOD")

if [ $? -ne 0 ]; then
  echo "❌ Failed to fetch usage stats"
  exit 1
fi

# Display summary
echo "📊 Summary:"
echo "$USAGE" | jq -r '"Total Requests: \(.total_requests)\nTotal Spent: $\(.total_spent_usdc) USDC"'

echo ""
echo "📈 By API:"
echo "$USAGE" | jq -r '.by_api | to_entries[] | "\(.key):\t\(.value.requests) req\t$\(.value.spent) USDC"' | column -t -s $'\t'

echo ""
echo "💡 Tip: Use --today, --week, or --month to filter"
echo ""
