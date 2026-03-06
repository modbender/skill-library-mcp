#!/usr/bin/env bash
# eywa-call.sh — Call Eywa MCP tools via HTTP.
# Usage: bash eywa-call.sh <tool_name> '<json_arguments>'
#
# Environment:
#   EYWA_URL   — MCP endpoint (default: https://eywa-mcp.armandsumo.workers.dev)
#   EYWA_ROOM  — Room slug (default: demo)
#   EYWA_AGENT — Agent identity prefix (default: openclaw). Server appends a unique suffix.

set -euo pipefail

TOOL="${1:?Usage: eywa-call.sh <tool_name> '<json_args>'}"
ARGS="${2:-\{\}}"

URL="${EYWA_URL:-https://eywa-mcp.armandsumo.workers.dev}"
ROOM="${EYWA_ROOM:-demo}"
AGENT="${EYWA_AGENT:-openclaw}"

ENDPOINT="${URL}/mcp?room=${ROOM}&agent=${AGENT}"

# Build JSON payload using printf to avoid heredoc expansion issues
REQ_ID="$(date +%s)$$"
PAYLOAD=$(printf '{"jsonrpc":"2.0","id":%s,"method":"tools/call","params":{"name":"%s","arguments":%s}}' \
  "${REQ_ID}" "${TOOL}" "${ARGS}")

# Call the MCP endpoint
RESPONSE=$(curl -s -X POST "${ENDPOINT}" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d "${PAYLOAD}" 2>&1)

# Parse SSE response: extract the data line
if echo "${RESPONSE}" | grep -q '^data: '; then
  DATA=$(echo "${RESPONSE}" | grep '^data: ' | head -1 | sed 's/^data: //')
else
  DATA="${RESPONSE}"
fi

# Extract text content from the MCP response
if command -v jq &>/dev/null; then
  TEXT=$(echo "${DATA}" | jq -r '.result.content[0].text // .error.message // "No response"' 2>/dev/null)
  if [ "${TEXT}" = "null" ] || [ -z "${TEXT}" ]; then
    TEXT=$(echo "${DATA}" | jq -r 'tostring' 2>/dev/null || echo "${DATA}")
  fi
else
  # Fallback without jq: print raw response
  TEXT="${DATA}"
fi

echo "${TEXT}"
