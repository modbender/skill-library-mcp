#!/bin/bash
set -euo pipefail

CONFIG_FILE="$HOME/.openclaw/skills/bankr/config.json"
API_KEY=$(jq -r '.apiKey' "$CONFIG_FILE")
API_URL=$(jq -r '.apiUrl // "https://api.bankr.bot"' "$CONFIG_FILE")

JOB_ID="$1"
curl -sf -X GET "${API_URL}/agent/job/${JOB_ID}" \
  -H "X-API-Key: ${API_KEY}"
