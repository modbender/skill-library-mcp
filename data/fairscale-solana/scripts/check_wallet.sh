#!/bin/bash
# FairScale Wallet Check Script
# Usage: ./check_wallet.sh <WALLET_ADDRESS> <API_KEY>

WALLET=$1
API_KEY=$2

if [ -z "$WALLET" ] || [ -z "$API_KEY" ]; then
  echo "Usage: ./check_wallet.sh <WALLET_ADDRESS> <API_KEY>"
  exit 1
fi

curl -s "https://api2.fairscale.xyz/score?wallet=$WALLET" \
  -H "accept: application/json" \
  -H "fairkey: $API_KEY" | jq .
