#!/bin/bash
# Authenticate with slashbot.net and print bearer token
# Usage: TOKEN=$(./slashbot-auth.sh /path/to/private.pem [url])
# Requires: openssl, jq, curl

set -euo pipefail

KEY="${1:?Usage: slashbot-auth.sh <private-key-path> [slashbot-url]}"
SLASHBOT_URL="${2:-https://slashbot.net}"

CHALLENGE=$(curl -s -X POST "$SLASHBOT_URL/api/auth/challenge" \
  -H "Content-Type: application/json" \
  -d '{"alg": "rsa-sha256"}' | jq -r '.challenge')

SIGNATURE=$(echo -n "$CHALLENGE" | openssl dgst -sha256 -sign "$KEY" | base64 -w0)
PUBKEY_FULL=$(openssl rsa -in "$KEY" -pubout 2>/dev/null)

curl -s -X POST "$SLASHBOT_URL/api/auth/verify" \
  -H "Content-Type: application/json" \
  -d "{
    \"alg\": \"rsa-sha256\",
    \"public_key\": $(echo "$PUBKEY_FULL" | jq -Rs .),
    \"challenge\": \"${CHALLENGE}\",
    \"signature\": \"${SIGNATURE}\"
  }" | jq -r '.access_token'
