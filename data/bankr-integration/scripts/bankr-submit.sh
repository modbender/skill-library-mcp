#!/bin/bash
set -euo pipefail

CONFIG_FILE="$HOME/.openclaw/skills/bankr/config.json"
API_KEY=$(jq -r '.apiKey' "$CONFIG_FILE")
API_URL=$(jq -r '.apiUrl // "https://api.bankr.bot"' "$CONFIG_FILE")

PROMPT="$*"
if [ -z "$PROMPT" ]; then
    echo '{"error": "Usage: bankr-submit.sh <prompt>"}' >&2
    exit 1
fi

curl -sf -X POST "${API_URL}/agent/prompt" \
  -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d "$(jq -nc --arg prompt "$PROMPT" '{prompt: $prompt}')"
