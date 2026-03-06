#!/usr/bin/env bash
set -euo pipefail

# Apiosk Publisher - My APIs
# List your registered APIs and revenue stats with signed wallet auth.

GATEWAY_URL="https://gateway.apiosk.com"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=auth-utils.sh
source "$SCRIPT_DIR/auth-utils.sh"

WALLET=""
PRIVATE_KEY=""

print_help() {
  echo "Usage: $0 [OPTIONS]"
  echo ""
  echo "Options:"
  echo "  --wallet ADDRESS         Wallet address (optional: defaults from ~/.apiosk)"
  echo "  --private-key HEX        Wallet private key for signature (optional)"
  echo "  --help                   Show this help"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --wallet)
      WALLET="$2"
      shift 2
      ;;
    --private-key)
      PRIVATE_KEY="$2"
      shift 2
      ;;
    --help)
      print_help
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      print_help
      exit 1
      ;;
  esac
done

WALLET="$(load_wallet_address "$WALLET" || true)"
if [[ -z "$WALLET" ]]; then
  echo "Error: Wallet not found. Provide --wallet or create ~/.apiosk/wallet.json"
  exit 1
fi

if ! validate_wallet_format "$WALLET"; then
  echo "Error: Invalid wallet address format"
  exit 1
fi

PRIVATE_KEY="$(load_private_key "$PRIVATE_KEY" || true)"
if [[ -z "$PRIVATE_KEY" ]]; then
  echo "Error: Private key required for signed auth."
  echo "Provide --private-key, APIOSK_PRIVATE_KEY, or ~/.apiosk/wallet.json with private_key."
  exit 1
fi

require_signing_bin

RESOURCE="mine:${WALLET}"
sign_wallet_auth "my_apis" "$RESOURCE" "$WALLET" "$PRIVATE_KEY"

echo "Fetching your APIs..."
echo ""

RAW_RESPONSE="$(curl -s -w "\n%{http_code}" "$GATEWAY_URL/v1/apis/mine?wallet=$WALLET" \
  -H "x-wallet-address: $WALLET" \
  -H "x-wallet-signature: $AUTH_SIGNATURE" \
  -H "x-wallet-timestamp: $AUTH_TIMESTAMP" \
  -H "x-wallet-nonce: $AUTH_NONCE")"

HTTP_CODE="$(echo "$RAW_RESPONSE" | tail -n1)"
RESPONSE="$(echo "$RAW_RESPONSE" | sed '$d')"

if ! echo "$RESPONSE" | jq empty 2>/dev/null; then
  echo "Gateway returned HTTP $HTTP_CODE"
  echo "$RESPONSE"
  if [[ "$HTTP_CODE" == "401" ]]; then
    echo "Auth failed. Check wallet/private key and retry."
  fi
  exit 1
fi

API_COUNT="$(echo "$RESPONSE" | jq '.apis | length')"
TOTAL_EARNINGS="$(echo "$RESPONSE" | jq -r '.total_earnings_usd')"

if [[ "$API_COUNT" -eq 0 ]]; then
  echo "No APIs registered yet."
  echo ""
  echo "Register your first API:"
  echo "  ./register-api.sh --help"
  exit 0
fi

echo "Your APIs ($API_COUNT total)"
echo "Total Earnings: \$$TOTAL_EARNINGS USD"
echo ""

echo "$RESPONSE" | jq -r '.apis[] |
  "----------------------------------------\n" +
  (.name + " (" + .slug + ")\n") +
  ("  Gateway: https://gateway.apiosk.com/" + .slug + "\n") +
  ("  Endpoint: " + .endpoint_url + "\n") +
  ("  Price: $" + (.price_usd|tostring) + "/request\n") +
  ("  Active: " + (.active|tostring) + " | Verified: " + (.verified|tostring) + "\n") +
  ("  Requests: " + (.total_requests|tostring) + "\n") +
  ("  Earned: $" + (.total_earned_usd|tostring) + " USD\n") +
  ("  Pending: $" + (.pending_withdrawal_usd|tostring) + " USD\n")'

echo "----------------------------------------"
echo ""
echo "Update an API: ./update-api.sh --slug SLUG --help"
echo "Delete an API: ./delete-api.sh --slug SLUG --help"
