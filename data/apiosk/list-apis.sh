#!/bin/bash
# List all available Apiosk APIs with pricing

GATEWAY_URL="https://gateway.apiosk.com"

echo "🦞 Available Apiosk APIs"
echo ""

# Fetch API list
APIS=$(curl -s "$GATEWAY_URL/v1/apis")

if [ $? -ne 0 ]; then
  echo "❌ Failed to fetch APIs from $GATEWAY_URL"
  exit 1
fi

# Parse and display
echo "$APIS" | jq -r '.apis[] | "\(.id)\t$\(.price_usd)/req\t\(.description)"' | column -t -s $'\t'

echo ""
echo "Total APIs: $(echo "$APIS" | jq '.apis | length')"
echo ""
echo "Usage: ./call-api.sh <api-id> --params '{\"key\":\"value\"}'"
echo "Docs: https://apiosk.com/#docs"
echo ""
