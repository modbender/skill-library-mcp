#!/bin/bash
# Initialize ClawChain connection configuration
# Usage: bash init-clawchain.sh [rpc-url]

RPC_URL="${1:-ws://localhost:9944}"

mkdir -p ${WORKSPACE:-$HOME/workspace}/memory

cat > ${WORKSPACE:-$HOME/workspace}/memory/clawchain-config.json << HEREDOC
{
  "rpc_url": "$RPC_URL",
  "node_endpoint": "http://localhost:9944",
  "websocket_endpoint": "$RPC_URL",
  "agent_did": "",
  "owner_address": "0x64e830dd7aF93431C898eA9e4C375C6706bd0Fc5"
}
HEREDOC

echo "✅ ClawChain config created at ${WORKSPACE:-$HOME/workspace}/memory/clawchain-config.json"
echo ""
echo "RPC URL: $RPC_URL"
echo ""
echo "Next steps:"
echo "  1. Start ClawChain node: clawchain-node --dev --rpc-external --ws-external"
echo "  2. Register your agent's DID"
echo "  3. Check reputation and token balance"
