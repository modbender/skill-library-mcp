#!/usr/bin/env bash
set -euo pipefail

API_BASE_DEFAULT="https://x402pulse.xyz"
API_BASE="${API_BASE:-$API_BASE_DEFAULT}"

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <agentAddress>" >&2
  echo "Env: API_BASE (default: $API_BASE_DEFAULT)" >&2
  exit 2
fi

AGENT_ADDRESS="$1"
if [[ ! "$AGENT_ADDRESS" =~ ^0x[a-fA-F0-9]{40}$ ]]; then
  echo "Error: Invalid agent address format. Expected 0x followed by 40 hex characters." >&2
  exit 1
fi

curl -sS -f \
  --connect-timeout "${CONNECT_TIMEOUT:-10}" \
  --max-time "${MAX_TIME:-30}" \
  "$API_BASE/api/status/$AGENT_ADDRESS"
