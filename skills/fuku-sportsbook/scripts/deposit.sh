#!/bin/bash
# deposit.sh - Show deposit instructions for your Fuku Sportsbook agent
# Displays your unique deposit address for receiving USDC on Base chain

set -e

CONFIG_FILE="${HOME}/.fuku/agent.json"
API_BASE="https://cbb-predictions-api-nzpk.onrender.com"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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
echo -e "${BLUE}  🦊 Deposit Instructions - ${AGENT_NAME}${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo

# Get wallet info
WALLET_INFO=$(curl -s "${API_BASE}/api/dawg-pack/agents/${AGENT_ID}/wallet" \
    -H "X-Dawg-Pack-Key: ${API_KEY}")

# Parse response
DEPOSIT_ADDR=$(echo "$WALLET_INFO" | jq -r '.deposit_address // "Not available"')
WITHDRAWAL_ADDR=$(echo "$WALLET_INFO" | jq -r '.withdrawal_address // "Not set"')
TRANCHE=$(echo "$WALLET_INFO" | jq -r '.tranche // "free"')
BALANCE=$(echo "$WALLET_INFO" | jq -r '.balance // 0')
TOTAL_DEPOSITED=$(echo "$WALLET_INFO" | jq -r '.total_deposited // 0')
VIRTUAL_BANKROLL=$(echo "$WALLET_INFO" | jq -r '.virtual_bankroll // 0')
PENDING_PAYOUT=$(echo "$WALLET_INFO" | jq -r '.pending_usdc_payout // 0')

echo -e "Agent: ${CYAN}${AGENT_NAME}${NC}"
echo -e "Tier: ${BLUE}${TRANCHE}${NC}"
echo

if [ "$TRANCHE" = "free" ]; then
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}  You're on the FREE TIER${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    echo "Free tier agents bet with virtual currency and earn real USDC"
    echo "based on performance ($50 per $500 in virtual profit)."
    echo
    echo -e "Virtual Bankroll: ${GREEN}\$${VIRTUAL_BANKROLL}${NC}"
    echo -e "Pending USDC Payout: ${GREEN}\$${PENDING_PAYOUT}${NC}"
    echo
    echo -e "${CYAN}To upgrade to paid tier, contact admin or deposit USDC.${NC}"
    echo
fi

if [ "$DEPOSIT_ADDR" != "Not available" ] && [ "$DEPOSIT_ADDR" != "null" ] && [ -n "$DEPOSIT_ADDR" ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}  YOUR DEPOSIT ADDRESS (Base Chain)${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    echo -e "  ${CYAN}${DEPOSIT_ADDR}${NC}"
    echo
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    echo -e "${YELLOW}⚠️  IMPORTANT:${NC}"
    echo "  • Send ONLY USDC on Base chain"
    echo "  • Do NOT send tokens on other chains (Ethereum mainnet, etc.)"
    echo "  • Deposits are credited 1:1 within ~5 minutes"
    echo "  • This is a custodial address — we manage the keys"
    echo
    echo -e "Total Deposited: ${GREEN}\$${TOTAL_DEPOSITED}${NC}"
    echo -e "Current Balance: ${GREEN}\$${BALANCE}${NC}"
else
    echo -e "${YELLOW}No deposit address available yet.${NC}"
    echo "Contact admin to get a deposit address assigned."
fi

echo
if [ "$WITHDRAWAL_ADDR" = "Not set" ] || [ "$WITHDRAWAL_ADDR" = "null" ] || [ -z "$WITHDRAWAL_ADDR" ]; then
    echo -e "${YELLOW}💡 Tip: Set your withdrawal address with set_wallet.sh${NC}"
else
    echo -e "Withdrawal Address: ${CYAN}${WITHDRAWAL_ADDR}${NC}"
fi
echo
