#!/usr/bin/env bash
set -euo pipefail

# Apiosk Publisher - Delete API
# Deactivate an API with signed wallet auth.

GATEWAY_URL="https://gateway.apiosk.com"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=auth-utils.sh
source "$SCRIPT_DIR/auth-utils.sh"

SLUG=""
WALLET=""
PRIVATE_KEY=""

print_help() {
  echo "Usage: $0 --slug SLUG [OPTIONS]"
  echo ""
  echo "Options:"
  echo "  --slug SLUG              API slug to deactivate (required)"
  echo "  --wallet ADDRESS         Wallet address (optional: defaults from ~/.apiosk)"
  echo "  --private-key HEX        Wallet private key for signature (optional)"
  echo "  --help                   Show this help"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --slug)
      SLUG="$2"
      shift 2
      ;;
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

if [[ -z "$SLUG" ]]; then
  echo "Error: --slug is required"
  print_help
  exit 1
fi

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

RESOURCE="delete:${SLUG}"
sign_wallet_auth "delete_api" "$RESOURCE" "$WALLET" "$PRIVATE_KEY"

echo "Deactivating API '$SLUG'..."
echo ""

RAW_RESPONSE="$(curl -s -w "\n%{http_code}" -X DELETE "$GATEWAY_URL/v1/apis/$SLUG?wallet=$WALLET" \
  -H "x-wallet-address: $WALLET" \
  -H "x-wallet-signature: $AUTH_SIGNATURE" \
  -H "x-wallet-timestamp: $AUTH_TIMESTAMP" \
  -H "x-wallet-nonce: $AUTH_NONCE")"

HTTP_CODE="$(echo "$RAW_RESPONSE" | tail -n1)"
RESPONSE="$(echo "$RAW_RESPONSE" | sed '$d')"

if ! echo "$RESPONSE" | jq empty 2>/dev/null; then
  echo "Gateway returned HTTP $HTTP_CODE"
  echo "$RESPONSE"
  exit 1
fi

SUCCESS="$(echo "$RESPONSE" | jq -r '.success')"

if [[ "$SUCCESS" == "true" ]]; then
  echo "API deactivated successfully."
  echo "$(echo "$RESPONSE" | jq -r '.message')"
else
  echo "Deactivation failed"
  echo "$(echo "$RESPONSE" | jq -r '.message')"
  exit 1
fi
