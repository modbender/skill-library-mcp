#!/bin/bash

# Check Lightning invoice payment status
CONFIG_FILE="$HOME/.openclaw/openclaw.json"

# Check invoice_id argument
if [ -z "$1" ]; then
  echo "Usage: $0 <invoice_id>"
  echo "Example: $0 OnXsgW4-OvVTOt7LVDCD4A"
  exit 1
fi

INVOICE_ID="$1"

# Extract base URL and API key from config
BASE_URL=$(jq -r '.models.providers.routstr.baseUrl' "$CONFIG_FILE")

# Check status
curl -s "${BASE_URL}/balance/lightning/invoice/${INVOICE_ID}/status" | jq .
