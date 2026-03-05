#!/bin/bash

# Default parameters
CURRENCY="CNY"
TARGET="USD"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --currency|-c)
      CURRENCY="$2"
      shift 2
      ;;
    --target|-t)
      TARGET="$2"
      shift 2
      ;;
    *)
      echo "Unknown parameter: $1"
      echo "Usage: $0 [--currency|-c <currency>] [--target|-t <target>]"
      exit 1
      ;;
  esac
done

# Convert to uppercase to ensure ISO 4217 code formatting
CURRENCY=$(echo "$CURRENCY" | tr '[:lower:]' '[:upper:]')
TARGET=$(echo "$TARGET" | tr '[:lower:]' '[:upper:]')

API_URL="https://60s.viki.moe/v2/exchange-rate?currency=${CURRENCY}"

# Request API
response=$(curl -s "$API_URL")

if [[ -z "$response" ]]; then
    echo "Error: Failed to fetch data from API."
    exit 1
fi

if [[ "$TARGET" == "AAA" ]]; then
    # Return all results directly
    echo "$response"
else
    # Parse the target rate
    rate=$(echo "$response" | jq -r --arg target "$TARGET" '.data.rates[]? | select(.currency == $target) | .rate')
    
    if [[ -z "$rate" || "$rate" == "null" ]]; then
        echo "Error: target currency not found. Please check if the ISO 4217 currency code is correct."
        exit 1
    else
        echo "$rate"
    fi
fi
