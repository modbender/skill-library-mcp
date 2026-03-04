#!/usr/bin/env bash
# Stock Market Intelligence — one-command setup
# Registers a free API key and saves it to your environment.
#
# Usage:
#   bash scripts/setup.sh          # interactive (for humans)
#   bash scripts/setup.sh --auto   # non-interactive (for AI agents/scripts)

set -euo pipefail

BASE_URL="https://api.traderhc.com"
AUTO=false

# Parse flags
for arg in "$@"; do
  case "$arg" in
    --auto) AUTO=true ;;
  esac
done

# Check if already configured
if [ -n "${AGENTHC_API_KEY:-}" ]; then
  if [ "$AUTO" = true ]; then
    echo "$AGENTHC_API_KEY"
  else
    echo "Already configured! AGENTHC_API_KEY is set."
    echo "Test it: bash scripts/agenthc.sh market_intelligence"
  fi
  exit 0
fi

# Get agent name
if [ "$AUTO" = true ]; then
  AGENT_NAME="OpenClawAgent"
else
  echo "=== Stock Market Intelligence Setup ==="
  echo ""
  read -r -p "Name your agent (default: MyAgent): " AGENT_NAME
  AGENT_NAME="${AGENT_NAME:-MyAgent}"
fi

# Sanitize input
if [[ ! "$AGENT_NAME" =~ ^[a-zA-Z0-9\ _-]+$ ]]; then
  echo "Error: Agent name must be alphanumeric" >&2
  exit 1
fi

if [ "$AUTO" = false ]; then
  echo ""
  echo "Registering '$AGENT_NAME' (free, no KYC)..."
fi

# Register
RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/agents/register" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"$AGENT_NAME\", \"description\": \"OpenClaw agent via ClawHub\"}")

# Extract API key
API_KEY=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('api_key',''))" 2>/dev/null || echo "")

if [ -z "$API_KEY" ]; then
  echo "Registration failed." >&2
  echo "$RESPONSE" >&2
  exit 1
fi

# Auto mode: just print the key and exit
if [ "$AUTO" = true ]; then
  echo "$API_KEY"
  exit 0
fi

# Interactive mode: print key and usage instructions
echo ""
echo "Registered! Your API key: $API_KEY"
echo ""
echo "To use it, run:"
echo "  export AGENTHC_API_KEY=\"$API_KEY\""
echo "  bash scripts/agenthc.sh market_intelligence"
echo ""
echo "To make it permanent, add this line to your shell config (~/.zshrc or ~/.bashrc):"
echo "  export AGENTHC_API_KEY=\"$API_KEY\""
echo ""
echo "Free modules: market_intelligence, educational_content, polymarket_intelligence"
echo "Full docs: https://api.traderhc.com/docs"
