#!/usr/bin/env bash
# UCM Agent Registration Script
# Usage: bash register.sh [agent-name] [description]
#
# Registers a new agent on UCM and returns the API key.
# The agent receives $1.00 in free credits immediately.
# Credentials are saved to ~/.config/ucm/credentials.json
#
# Dependencies: curl (required), jq or python3 (optional, for pretty output)

set -euo pipefail

REGISTRY_URL="https://registry.ucm.ai"
AGENT_NAME="${1:-my-agent}"
DESCRIPTION="${2:-}"
CREDENTIALS_PATH="$HOME/.config/ucm/credentials.json"

# Check if already registered
if [ -f "$CREDENTIALS_PATH" ]; then
  EXISTING_KEY=""
  if command -v jq >/dev/null 2>&1; then
    EXISTING_KEY=$(jq -r '.api_key // empty' "$CREDENTIALS_PATH" 2>/dev/null)
  elif command -v python3 >/dev/null 2>&1; then
    EXISTING_KEY=$(python3 -c "import sys,json; print(json.load(open('$CREDENTIALS_PATH')).get('api_key',''))" 2>/dev/null)
  else
    EXISTING_KEY=$(grep -o '"api_key":"[^"]*"' "$CREDENTIALS_PATH" 2>/dev/null | head -1 | sed 's/"api_key":"//;s/"$//')
  fi
  if [ -n "$EXISTING_KEY" ]; then
    echo "Already registered! Credentials found at $CREDENTIALS_PATH"
    echo ""
    echo "API Key: $EXISTING_KEY"
    echo ""
    echo "Set it as an environment variable:"
    echo "  export UCM_API_KEY=\"$EXISTING_KEY\""
    exit 0
  fi
fi

# Sanitize inputs for JSON (escape quotes and backslashes)
sanitize() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'; }

SAFE_NAME=$(sanitize "$AGENT_NAME")
SAFE_DESC=$(sanitize "$DESCRIPTION")

# Build request body
if [ -n "$SAFE_DESC" ]; then
  BODY="{\"name\":\"${SAFE_NAME}\",\"description\":\"${SAFE_DESC}\"}"
else
  BODY="{\"name\":\"${SAFE_NAME}\"}"
fi

# Register
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${REGISTRY_URL}/v1/agents/register" \
  -H "Content-Type: application/json" \
  -d "$BODY")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY_RESPONSE=$(echo "$RESPONSE" | sed '$d')

# Extract fields using available JSON parser, falling back to grep
extract_field() {
  local json="$1" field="$2"
  if command -v jq >/dev/null 2>&1; then
    echo "$json" | jq -r ".$field // empty"
  elif command -v python3 >/dev/null 2>&1; then
    echo "$json" | python3 -c "import sys,json; print(json.load(sys.stdin).get('$field',''))" 2>/dev/null
  else
    echo "$json" | grep -o "\"$field\":\"[^\"]*\"" | head -1 | sed "s/\"$field\":\"//;s/\"$//"
  fi
}

if [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 300 ]; then
  API_KEY=$(extract_field "$BODY_RESPONSE" "api_key")
  AGENT_ID=$(extract_field "$BODY_RESPONSE" "agent_id")
  if [ -n "$API_KEY" ]; then
    # Save credentials
    mkdir -p "$(dirname "$CREDENTIALS_PATH")"
    if command -v jq >/dev/null 2>&1; then
      echo "$BODY_RESPONSE" | jq '{api_key: .api_key, agent_id: .agent_id, registered_at: .credentials_to_save.registered_at}' > "$CREDENTIALS_PATH"
    else
      REGISTERED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
      printf '{\n  "api_key": "%s",\n  "agent_id": "%s",\n  "registered_at": "%s"\n}\n' "$API_KEY" "$AGENT_ID" "$REGISTERED_AT" > "$CREDENTIALS_PATH"
    fi

    echo "Registration successful!"
    echo ""
    echo "API Key: $API_KEY"
    echo "Credentials saved to: $CREDENTIALS_PATH"
    echo ""
    echo "Set it as an environment variable:"
    echo "  export UCM_API_KEY=\"$API_KEY\""
    echo ""
    echo "You have \$1.00 in free credits. Try a web search:"
    echo "  curl -s -X POST ${REGISTRY_URL}/v1/call \\"
    echo "    -H \"Authorization: Bearer \$UCM_API_KEY\" \\"
    echo "    -H \"Content-Type: application/json\" \\"
    echo "    -d '{\"service_id\":\"ucm/web-search\",\"endpoint\":\"search\",\"params\":{\"query\":\"hello world\"}}'"
  else
    echo "$BODY_RESPONSE"
  fi
else
  echo "Registration failed (HTTP $HTTP_CODE):"
  echo "$BODY_RESPONSE"
  exit 1
fi
