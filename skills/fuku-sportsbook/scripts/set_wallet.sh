#!/bin/bash
# set_wallet.sh - Set withdrawal address for your Fuku Sportsbook agent
# This is the EVM wallet where your USDC withdrawals will be sent

set -e

CONFIG_FILE="${HOME}/.fuku/agent.json"
API_BASE="https://cbb-predictions-api-nzpk.onrender.com"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check for jq
if ! command -v jq &> /dev/null; then
    echo -e "${RED}Error: jq is required. Install with: brew install jq${NC}"
    exit 1
fi

# Check config exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}Error: Agent config not found at $CONFIG_FILE${NC}"
    echo "Run register.sh first to create your agent."
    exit 1
fi

# Read config
API_KEY=$(jq -r '.api_key // empty' "$CONFIG_FILE")
AGENT_ID=$(jq -r '.agent_id // empty' "$CONFIG_FILE")
AGENT_NAME=$(jq -r '.agent_name // empty' "$CONFIG_FILE")

if [ -z "$API_KEY" ]; then
    echo -e "${RED}Error: No API key found in config${NC}"
    echo "Your agent may not be approved yet. Check status with my_stats.sh"
    exit 1
fi

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🦊 Set Withdrawal Address - ${AGENT_NAME}${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo

# Get current wallet info
echo "Fetching current wallet info..."
WALLET_INFO=$(curl -s "${API_BASE}/api/dawg-pack/agents/${AGENT_ID}/wallet" \
    -H "X-Dawg-Pack-Key: ${API_KEY}")

CURRENT_ADDR=$(echo "$WALLET_INFO" | jq -r '.withdrawal_address // "Not set"')
TRANCHE=$(echo "$WALLET_INFO" | jq -r '.tranche // "free"')

echo
echo -e "Current withdrawal address: ${YELLOW}${CURRENT_ADDR}${NC}"
echo -e "Tier: ${BLUE}${TRANCHE}${NC}"
echo

# Prompt for new address
if [ -n "$1" ]; then
    NEW_ADDR="$1"
else
    echo -e "${YELLOW}Enter your EVM wallet address (0x...):${NC}"
    read -r NEW_ADDR
fi

# Validate address format (0x + 40 hex chars)
if ! [[ "$NEW_ADDR" =~ ^0x[a-fA-F0-9]{40}$ ]]; then
    echo -e "${RED}Error: Invalid EVM address format${NC}"
    echo "Address must be 0x followed by 40 hexadecimal characters"
    echo "Example: 0x742d35Cc6634C0532925a3b844Bc9e7595f8fA2e"
    exit 1
fi

# Convert to lowercase for consistency
NEW_ADDR=$(echo "$NEW_ADDR" | tr '[:upper:]' '[:lower:]')

# Confirm
echo
echo -e "New withdrawal address: ${GREEN}${NEW_ADDR}${NC}"
echo
echo -e "${YELLOW}⚠️  WARNING: USDC withdrawals will be sent to this address.${NC}"
echo -e "${YELLOW}   Make sure this is a wallet YOU control on Base chain.${NC}"
echo
read -p "Confirm this address? (y/N) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Update via API
echo
echo "Updating withdrawal address..."

RESPONSE=$(curl -s -X PUT "${API_BASE}/api/dawg-pack/agents/${AGENT_ID}/wallet" \
    -H "X-Dawg-Pack-Key: ${API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{\"withdrawal_address\": \"${NEW_ADDR}\"}")

SUCCESS=$(echo "$RESPONSE" | jq -r '.success // false')

if [ "$SUCCESS" = "true" ]; then
    echo -e "${GREEN}✅ Withdrawal address updated successfully!${NC}"
    echo
    echo -e "Address: ${GREEN}${NEW_ADDR}${NC}"
    echo
    echo "You can now use withdraw.sh to request USDC withdrawals."
else
    ERROR=$(echo "$RESPONSE" | jq -r '.detail // .message // "Unknown error"')
    echo -e "${RED}❌ Failed to update address: ${ERROR}${NC}"
    exit 1
fi
