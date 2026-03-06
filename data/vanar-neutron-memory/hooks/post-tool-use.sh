#!/usr/bin/env bash
# Auto-Capture: Save conversation after AI turn

# Check if auto-capture is enabled (default: false — opt-in only)
VANAR_AUTO_CAPTURE="${VANAR_AUTO_CAPTURE:-false}"
[[ "$VANAR_AUTO_CAPTURE" != "true" ]] && exit 0

# jq is required for safe JSON construction
command -v jq &> /dev/null || exit 0

API_BASE="${NEUTRON_API_BASE:-https://api-neutron.vanarchain.com}"
CONFIG_FILE="${HOME}/.config/neutron/credentials.json"

API_KEY="${API_KEY:-${NEUTRON_API_KEY:-}}"

if [[ -z "$API_KEY" ]] && [[ -f "$CONFIG_FILE" ]]; then
    API_KEY=$(jq -r '.api_key // empty' "$CONFIG_FILE" 2>/dev/null || true)
fi

[[ -z "$API_KEY" ]] && exit 0

USER_MSG="${OPENCLAW_USER_MESSAGE:-}"
AI_RESP="${OPENCLAW_AI_RESPONSE:-}"

[[ -z "$USER_MSG" && -z "$AI_RESP" ]] && exit 0

TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
TITLE="Conversation - ${TS}"
CONTENT="User: ${USER_MSG}
Assistant: ${AI_RESP}"

# Build form field values safely using jq (prevents JSON injection)
text_json=$(jq -n --arg t "$CONTENT" '[$t]')
title_json=$(jq -n --arg t "$TITLE" '[$t]')

curl -s -X POST "${API_BASE}/memory/save" \
    -H "Authorization: Bearer ${API_KEY}" \
    -F "text=${text_json}" \
    -F 'textTypes=["text"]' \
    -F 'textSources=["auto_capture"]' \
    -F "textTitles=${title_json}" > /dev/null 2>&1
