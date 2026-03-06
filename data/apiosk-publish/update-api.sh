#!/usr/bin/env bash
set -euo pipefail

# Apiosk Publisher - Update API
# Update your API configuration with signed wallet auth.

GATEWAY_URL="https://gateway.apiosk.com"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=auth-utils.sh
source "$SCRIPT_DIR/auth-utils.sh"

# Default values
SLUG=""
WALLET=""
PRIVATE_KEY=""
ENDPOINT=""
PRICE=""
DESCRIPTION=""
ACTIVE=""

print_help() {
  echo "Usage: $0 --slug SLUG [OPTIONS]"
  echo ""
  echo "Options:"
  echo "  --slug SLUG              API slug to update (required)"
  echo "  --wallet ADDRESS         Wallet address (optional: defaults from ~/.apiosk)"
  echo "  --private-key HEX        Wallet private key for signature (optional)"
  echo "  --endpoint URL           New endpoint URL (HTTPS required)"
  echo "  --price USD              New price per request (0.0001-10.00)"
  echo "  --description TEXT       New description"
  echo "  --active BOOL            Active status (true/false)"
  echo "  --help                   Show this help"
}

# Parse arguments
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
    --endpoint)
      ENDPOINT="$2"
      shift 2
      ;;
    --price)
      PRICE="$2"
      shift 2
      ;;
    --description)
      DESCRIPTION="$2"
      shift 2
      ;;
    --active)
      ACTIVE="$2"
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

if [[ -n "$ENDPOINT" && ! "$ENDPOINT" =~ ^https:// ]]; then
  echo "Error: Endpoint must use HTTPS"
  exit 1
fi

require_signing_bin

RESOURCE="update:${SLUG}"
sign_wallet_auth "update_api" "$RESOURCE" "$WALLET" "$PRIVATE_KEY"

# Build JSON payload (only include provided fields)
PAYLOAD_ARGS=(--arg wallet "$WALLET")
JQ_FIELDS="{ owner_wallet: \$wallet"

if [[ -n "$ENDPOINT" ]]; then
  PAYLOAD_ARGS+=(--arg endpoint "$ENDPOINT")
  JQ_FIELDS+=", endpoint_url: \$endpoint"
fi

if [[ -n "$PRICE" ]]; then
  PAYLOAD_ARGS+=(--argjson price "$PRICE")
  JQ_FIELDS+=", price_usd: \$price"
fi

if [[ -n "$DESCRIPTION" ]]; then
  PAYLOAD_ARGS+=(--arg description "$DESCRIPTION")
  JQ_FIELDS+=", description: \$description"
fi

if [[ -n "$ACTIVE" ]]; then
  ACTIVE_BOOL="false"
  if [[ "$ACTIVE" == "true" || "$ACTIVE" == "1" ]]; then
    ACTIVE_BOOL="true"
  fi
  PAYLOAD_ARGS+=(--argjson active "$ACTIVE_BOOL")
  JQ_FIELDS+=", active: \$active"
fi

JQ_FIELDS+=" }"
PAYLOAD="$(jq -n "${PAYLOAD_ARGS[@]}" "$JQ_FIELDS")"

echo "Updating API '$SLUG'..."
echo ""

RAW_RESPONSE="$(curl -s -w "\n%{http_code}" -X POST "$GATEWAY_URL/v1/apis/$SLUG" \
  -H "Content-Type: application/json" \
  -H "x-wallet-address: $WALLET" \
  -H "x-wallet-signature: $AUTH_SIGNATURE" \
  -H "x-wallet-timestamp: $AUTH_TIMESTAMP" \
  -H "x-wallet-nonce: $AUTH_NONCE" \
  -d "$PAYLOAD")"

HTTP_CODE="$(echo "$RAW_RESPONSE" | tail -n1)"
RESPONSE="$(echo "$RAW_RESPONSE" | sed '$d')"

if ! echo "$RESPONSE" | jq empty 2>/dev/null; then
  echo "Gateway returned HTTP $HTTP_CODE"
  echo "$RESPONSE"
  exit 1
fi

SUCCESS="$(echo "$RESPONSE" | jq -r '.success')"

if [[ "$SUCCESS" == "true" ]]; then
  echo "API updated successfully."
  echo ""
  echo "$(echo "$RESPONSE" | jq -r '.message')"
else
  echo "Update failed"
  echo ""
  echo "$(echo "$RESPONSE" | jq -r '.message')"
  exit 1
fi
