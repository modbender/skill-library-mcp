#!/usr/bin/env bash
set -euo pipefail

# Apiosk Publisher - Register API
# Register a new API on the Apiosk marketplace with signed wallet auth.

GATEWAY_URL="https://gateway.apiosk.com"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=auth-utils.sh
source "$SCRIPT_DIR/auth-utils.sh"

# Default values
NAME=""
SLUG=""
ENDPOINT=""
PRICE=""
DESCRIPTION=""
CATEGORY="data"
LISTING_GROUP=""
WALLET=""
PRIVATE_KEY=""

print_help() {
  echo "Usage: $0 [OPTIONS]"
  echo ""
  echo "Options:"
  echo "  --name NAME                API name (required)"
  echo "  --slug SLUG                URL-safe identifier (required)"
  echo "  --endpoint URL             API base URL (HTTPS required) (required)"
  echo "  --price USD                Price per request (0.0001-10.00) (required)"
  echo "  --description TEXT         API description (required)"
  echo "  --category CATEGORY        Category (default: data)"
  echo "  --listing-group GROUP      api | datasets | compute (maps to category)"
  echo "  --wallet ADDRESS           Wallet address (optional: defaults from ~/.apiosk)"
  echo "  --private-key HEX          Wallet private key for signature (optional)"
  echo "  --help                     Show this help"
}

map_listing_group_to_category() {
  case "$1" in
    api) echo "data" ;;
    datasets) echo "dataset" ;;
    compute) echo "compute" ;;
    *)
      echo "Error: --listing-group must be one of: api, datasets, compute"
      exit 1
      ;;
  esac
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --name)
      NAME="$2"
      shift 2
      ;;
    --slug)
      SLUG="$2"
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
    --category)
      CATEGORY="$2"
      shift 2
      ;;
    --listing-group)
      LISTING_GROUP="$2"
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

if [[ -n "$LISTING_GROUP" ]]; then
  CATEGORY="$(map_listing_group_to_category "$LISTING_GROUP")"
fi

# Validate required fields
if [[ -z "$NAME" || -z "$SLUG" || -z "$ENDPOINT" || -z "$PRICE" || -z "$DESCRIPTION" ]]; then
  echo "Error: Missing required fields"
  print_help
  exit 1
fi

# Validate HTTPS
if [[ ! "$ENDPOINT" =~ ^https:// ]]; then
  echo "Error: Endpoint must use HTTPS"
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

RESOURCE="register:${SLUG}"
sign_wallet_auth "register_api" "$RESOURCE" "$WALLET" "$PRIVATE_KEY"

# Build JSON payload
PAYLOAD="$(jq -n \
  --arg name "$NAME" \
  --arg slug "$SLUG" \
  --arg endpoint "$ENDPOINT" \
  --argjson price "$PRICE" \
  --arg description "$DESCRIPTION" \
  --arg category "$CATEGORY" \
  --arg wallet "$WALLET" \
  '{
    name: $name,
    slug: $slug,
    endpoint_url: $endpoint,
    price_usd: $price,
    description: $description,
    category: $category,
    owner_wallet: $wallet
  }')"

echo "Registering API..."
echo "  Name: $NAME"
echo "  Slug: $SLUG"
echo "  Endpoint: $ENDPOINT"
echo "  Price: \$$PRICE/request"
echo "  Wallet: $WALLET"
echo "  Category: $CATEGORY"
echo ""

RAW_RESPONSE="$(curl -s -w "\n%{http_code}" -X POST "$GATEWAY_URL/v1/apis/register" \
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
  echo "API registered successfully."
  echo ""
  echo "Gateway URL: $(echo "$RESPONSE" | jq -r '.gateway_url')"
  echo "Status: $(echo "$RESPONSE" | jq -r '.status')"
  echo "Verified: $(echo "$RESPONSE" | jq -r '.verified')"
  echo ""
  echo "$(echo "$RESPONSE" | jq -r '.message')"
else
  echo "Registration failed"
  echo ""
  echo "$(echo "$RESPONSE" | jq -r '.message')"
  exit 1
fi
