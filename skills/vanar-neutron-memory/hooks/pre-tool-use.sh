#!/usr/bin/env bash
# Auto-Recall: Query memories before AI turn and inject as context

# Check if auto-recall is enabled (default: false — opt-in only)
VANAR_AUTO_RECALL="${VANAR_AUTO_RECALL:-false}"
[[ "$VANAR_AUTO_RECALL" != "true" ]] && exit 0

set -euo pipefail

# jq is required for safe JSON construction
command -v jq &> /dev/null || exit 0

API_BASE="${NEUTRON_API_BASE:-https://api-neutron.vanarchain.com}"
CONFIG_FILE="${HOME}/.config/neutron/credentials.json"

# Load API key
API_KEY="${API_KEY:-${NEUTRON_API_KEY:-}}"

if [[ -z "$API_KEY" ]] && [[ -f "$CONFIG_FILE" ]]; then
    API_KEY=$(jq -r '.api_key // empty' "$CONFIG_FILE" 2>/dev/null || true)
fi

# Skip if no credentials
if [[ -z "$API_KEY" ]]; then
    exit 0
fi

# Get the user's latest message from stdin (OpenClaw passes context)
USER_MESSAGE="${OPENCLAW_USER_MESSAGE:-}"

if [[ -z "$USER_MESSAGE" ]]; then
    exit 0
fi

# Build JSON body safely using jq (prevents JSON injection)
json_body=$(jq -n --arg q "$USER_MESSAGE" '{"query":$q,"limit":5,"threshold":0.5}')

# Query for relevant memories
response=$(curl -s -X POST "${API_BASE}/memory/search" \
    -H "Authorization: Bearer ${API_KEY}" \
    -H "Content-Type: application/json" \
    -d "$json_body" 2>/dev/null || echo "{}")

# Extract memories if any
memories=$(echo "$response" | jq -r '.results[]?.content // empty' 2>/dev/null | head -500)

if [[ -n "$memories" ]]; then
    echo "---"
    echo "RECALLED MEMORIES:"
    echo "$memories"
    echo "---"
fi
