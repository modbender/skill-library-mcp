#!/bin/bash
# withdraw.sh - Request USDC withdrawal from your Fuku Sportsbook agent
# Paid tier only - sends USDC to your configured withdrawal address

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
echo -e "${BLUE}  🦊 Request Withdrawal - ${AGENT_NAME}${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo

# Get wallet info
WALLET_INFO=$(curl -s "${API_BASE}/api/dawg-pack/agents/${AGENT_ID}/wallet" \
    -H "X-Dawg-Pack-Key: ${API_KEY}")

# Parse response
TRANCHE=$(echo "$WALLET_INFO" | jq -r '.tranche // "free"')
BALANCE=$(echo "$WALLET_INFO" | jq -r '.balance // 0')
AVAILABLE=$(echo "$WALLET_INFO" | jq -r '.available_for_withdrawal // 0')
WITHDRAWAL_ADDR=$(echo "$WALLET_INFO" | jq -r '.withdrawal_address // empty')
PENDING_PAYOUT=$(echo "$WALLET_INFO" | jq -r '.pending_usdc_payout // 0')

# Check tier
if [ "$TRANCHE" = "free" ]; then
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}  FREE TIER - Withdrawals Not Available${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    echo "Free tier agents earn USDC payouts based on virtual performance."
    echo "Payouts are processed weekly from the Fuku treasury."
    echo
    echo -e "Your pending USDC payout: ${GREEN}\$${PENDING_PAYOUT}${NC}"
    echo -e "(Earned from virtual profit at \$50 per \$500)"
    echo
    echo "To withdraw directly, upgrade to paid tier by depositing USDC."
    exit 0
fi

# Check withdrawal address
if [ -z "$WITHDRAWAL_ADDR" ] || [ "$WITHDRAWAL_ADDR" = "null" ]; then
    echo -e "${RED}❌ No withdrawal address set${NC}"
    echo
    echo "You must set a withdrawal address before you can withdraw."
    echo "Run: ./set_wallet.sh"
    exit 1
fi

echo -e "Tier: ${BLUE}${TRANCHE}${NC}"
echo -e "Balance: ${GREEN}\$${BALANCE}${NC}"
echo -e "Available for withdrawal: ${GREEN}\$${AVAILABLE}${NC}"
echo -e "Withdrawal address: ${CYAN}${WITHDRAWAL_ADDR}${NC}"
echo

# Check if balance available
if (( $(echo "$AVAILABLE < 10" | bc -l) )); then
    echo -e "${RED}❌ Insufficient balance for withdrawal${NC}"
    echo "Minimum withdrawal: \$10 USDC"
    echo "Your available balance: \$${AVAILABLE}"
    exit 1
fi

# Get amount from arg or prompt
if [ -n "$1" ]; then
    AMOUNT="$1"
else
    echo -e "${YELLOW}Enter amount to withdraw (or 'all'):${NC}"
    read -r AMOUNT
fi

# Validate amount
if [ "$AMOUNT" != "all" ]; then
    if ! [[ "$AMOUNT" =~ ^[0-9]+\.?[0-9]*$ ]]; then
        echo -e "${RED}Error: Invalid amount. Enter a number or 'all'.${NC}"
        exit 1
    fi
    
    if (( $(echo "$AMOUNT < 10" | bc -l) )); then
        echo -e "${RED}Error: Minimum withdrawal is \$10 USDC${NC}"
        exit 1
    fi
    
    if (( $(echo "$AMOUNT > $AVAILABLE" | bc -l) )); then
        echo -e "${RED}Error: Amount exceeds available balance (\$${AVAILABLE})${NC}"
        exit 1
    fi
fi

# Confirm
echo
if [ "$AMOUNT" = "all" ]; then
    echo -e "Withdraw: ${GREEN}ALL (\$${AVAILABLE})${NC}"
else
    echo -e "Withdraw: ${GREEN}\$${AMOUNT}${NC}"
fi
echo -e "To: ${CYAN}${WITHDRAWAL_ADDR}${NC}"
echo
echo -e "${YELLOW}⚠️  This will send real USDC to the address above.${NC}"
echo
read -p "Confirm withdrawal? (y/N) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Submit withdrawal request
echo
echo "Submitting withdrawal request..."

RESPONSE=$(curl -s -X POST "${API_BASE}/api/dawg-pack/agents/${AGENT_ID}/withdraw" \
    -H "X-Dawg-Pack-Key: ${API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{\"amount\": \"${AMOUNT}\"}")

SUCCESS=$(echo "$RESPONSE" | jq -r '.success // false')

if [ "$SUCCESS" = "true" ]; then
    WITHDRAW_ID=$(echo "$RESPONSE" | jq -r '.withdrawal_id')
    FINAL_AMOUNT=$(echo "$RESPONSE" | jq -r '.amount')
    EST_TIME=$(echo "$RESPONSE" | jq -r '.estimated_time')
    
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}  ✅ WITHDRAWAL REQUESTED${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    echo -e "  ID: ${CYAN}${WITHDRAW_ID}${NC}"
    echo -e "  Amount: ${GREEN}\$${FINAL_AMOUNT} USDC${NC}"
    echo -e "  To: ${CYAN}${WITHDRAWAL_ADDR}${NC}"
    echo -e "  Estimated time: ${YELLOW}${EST_TIME}${NC}"
    echo
    echo "Your USDC will be sent to your wallet within the estimated time."
    echo "Check status with: ./balance.sh"
else
    ERROR=$(echo "$RESPONSE" | jq -r '.detail // .message // "Unknown error"')
    echo -e "${RED}❌ Withdrawal failed: ${ERROR}${NC}"
    exit 1
fi
