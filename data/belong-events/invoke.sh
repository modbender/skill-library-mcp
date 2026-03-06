#!/bin/bash
# Belong Events skill - JSON-RPC wrapper for OpenClaw agents
# Usage: invoke.sh <method> [params-json]
# Example: invoke.sh discover_events '{"city":"Miami"}'

set -euo pipefail

# Default production gateway is Belong-owned domain; override with BELONG_EVENTS_ENDPOINT for staging/self-hosted.
ENDPOINT="${BELONG_EVENTS_ENDPOINT:-https://join.belong.net/functions/v1/openclaw-skill-proxy}"
API_KEY="${BELONG_EVENTS_API_KEY:-}"

METHOD="${1:?Usage: invoke.sh <method> [params-json]}"
PARAMS="${2:-{}}"

HEADERS=(-H "Content-Type: application/json")
if [ -n "$API_KEY" ]; then
  HEADERS+=(-H "X-OpenClaw-Key: $API_KEY")
fi

exec curl -sS -X POST "$ENDPOINT" \
  "${HEADERS[@]}" \
  -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$METHOD\",\"params\":$PARAMS}"
