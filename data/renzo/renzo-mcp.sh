#!/usr/bin/env bash
set -euo pipefail

# SECURITY MANIFEST:
#   Environment variables accessed: none
#   External endpoints called: https://mcp.renzoprotocol.com/mcp (only, via JSON-RPC POST)
#   Local files read: none
#   Local files written: none

MCP_URL="https://mcp.renzoprotocol.com/mcp"

usage() {
  cat <<'USAGE'
Usage: renzo-mcp.sh <tool_name> [arguments_json]

Tools:
  get_ezeth_info                         ezETH metrics (APR, supply, TVL, price, exchange rate)
  get_protocol_stats                     Aggregate protocol statistics
  get_supported_chains                   List supported blockchain networks
  get_operators [arguments_json]         List operators (optional: {"product":"ezETH"})
  get_vaults [arguments_json]            List vaults (optional: {"ecosystem":"eigenlayer"})
  get_vault_details <arguments_json>     Vault details + live LTV (required: {"vaultId":"ezREZ"})
  get_vault_strategy <arguments_json>    AVS allocations & operators for EigenLayer vaults (required: {"vaultId":"ezETH"})
  get_token_balances <arguments_json>    User's Renzo token balances (required: {"address":"0x..."})
  get_withdrawal_requests <arguments_json> User's pending ezETH withdrawals (required: {"address":"0x..."})

Examples:
  renzo-mcp.sh get_ezeth_info
  renzo-mcp.sh get_vaults '{"ecosystem":"jito"}'
  renzo-mcp.sh get_vault_details '{"vaultId":"ezREZ"}'
  renzo-mcp.sh get_operators '{"product":"pzETH"}'
  renzo-mcp.sh get_vault_strategy '{"vaultId":"ezETH"}'
  renzo-mcp.sh get_token_balances '{"address":"0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"}'
  renzo-mcp.sh get_withdrawal_requests '{"address":"0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"}'
USAGE
  exit 1
}

if [[ $# -lt 1 ]]; then
  usage
fi

TOOL_NAME="$1"
ARGUMENTS="${2:-"{}"}"

VALID_TOOLS=(
  get_ezeth_info
  get_protocol_stats
  get_supported_chains
  get_operators
  get_vaults
  get_vault_details
  get_vault_strategy
  get_token_balances
  get_withdrawal_requests
)

is_valid=false
for t in "${VALID_TOOLS[@]}"; do
  if [[ "$TOOL_NAME" == "$t" ]]; then
    is_valid=true
    break
  fi
done

if [[ "$is_valid" == "false" ]]; then
  echo "Error: Unknown tool '$TOOL_NAME'" >&2
  echo "Valid tools: ${VALID_TOOLS[*]}" >&2
  exit 1
fi

if ! echo "$ARGUMENTS" | jq empty 2>/dev/null; then
  echo "Error: Invalid JSON arguments: $ARGUMENTS" >&2
  exit 1
fi

PAYLOAD=$(jq -n \
  --arg name "$TOOL_NAME" \
  --argjson args "$ARGUMENTS" \
  '{
    jsonrpc: "2.0",
    id: 1,
    method: "tools/call",
    params: { name: $name, arguments: $args }
  }')

RESPONSE=$(curl -s -f --max-time 30 -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d "$PAYLOAD" 2>&1) || {
  echo "Error: Failed to reach Renzo MCP server at $MCP_URL" >&2
  echo "Check your network connection and try again." >&2
  exit 1
}

# Handle SSE format: extract JSON from "data: {...}" lines
# Also handle plain JSON responses
if echo "$RESPONSE" | grep -q '^data: '; then
  JSON_DATA=$(echo "$RESPONSE" | grep '^data: ' | tail -1 | sed 's/^data: //')
else
  JSON_DATA="$RESPONSE"
fi

if ! echo "$JSON_DATA" | jq empty 2>/dev/null; then
  echo "Error: Unexpected response format from MCP server" >&2
  echo "$RESPONSE" >&2
  exit 1
fi

ERROR=$(echo "$JSON_DATA" | jq -r '.error // empty')
if [[ -n "$ERROR" ]]; then
  echo "Error from MCP server:" >&2
  echo "$JSON_DATA" | jq '.error' >&2
  exit 1
fi

# Extract the text content from the MCP response wrapper
# result.content is an array of {type, text} blocks
echo "$JSON_DATA" | jq -r '.result.content[0].text' | jq .
