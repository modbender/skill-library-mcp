#!/bin/bash
# balance.sh - Check balance and transaction history for your Fuku Sportsbook agent
# Shows current bankroll, deposits, withdrawals, and recent transactions

set -e

CONFIG_FILE="${HOME}/.fuku/agent.json"
API_BASE="https://cbb-predictions-api-nzpk.onrender.com"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Parse arguments
JSON_OUTPUT=false
LIMIT=20

while [[ $# -gt 0 ]]; do
    case $1 in
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --limit)
            LIMIT="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: balance.sh [OPTIONS]"
            echo
            echo "Options:"
            echo "  --json      Output in JSON format"
            echo "  --limit N   Number of transactions to show (default: 20)"
            echo "  --help      Show this help"
            exit 0
            ;;
        *)
            shift
            ;;
    esac
done

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

# Fetch wallet info and transactions
WALLET_INFO=$(curl -s "${API_BASE}/api/dawg-pack/agents/${AGENT_ID}/wallet" \
    -H "X-Dawg-Pack-Key: ${API_KEY}")

TRANSACTIONS=$(curl -s "${API_BASE}/api/dawg-pack/agents/${AGENT_ID}/transactions?limit=${LIMIT}" \
    -H "X-Dawg-Pack-Key: ${API_KEY}")

# JSON output mode
if [ "$JSON_OUTPUT" = true ]; then
    echo "{\"wallet\": ${WALLET_INFO}, \"transactions\": ${TRANSACTIONS}}"
    exit 0
fi

# Parse wallet info
TRANCHE=$(echo "$WALLET_INFO" | jq -r '.tranche // "free"')
DEPOSIT_ADDR=$(echo "$WALLET_INFO" | jq -r '.deposit_address // "Not set"')
WITHDRAWAL_ADDR=$(echo "$WALLET_INFO" | jq -r '.withdrawal_address // "Not set"')
TOTAL_DEPOSITED=$(echo "$WALLET_INFO" | jq -r '.total_deposited // 0')
TOTAL_WITHDRAWN=$(echo "$WALLET_INFO" | jq -r '.total_withdrawn // 0')

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🦊 Balance & History - ${AGENT_NAME}${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo

# Display based on tier
if [ "$TRANCHE" = "free" ]; then
    VIRTUAL=$(echo "$WALLET_INFO" | jq -r '.virtual_bankroll // 3000')
    STARTING=$(echo "$WALLET_INFO" | jq -r '.starting_bankroll // 3000')
    PROFIT=$(echo "$WALLET_INFO" | jq -r '.virtual_profit // 0')
    PENDING_PAYOUT=$(echo "$WALLET_INFO" | jq -r '.pending_usdc_payout // 0')
    
    echo -e "${CYAN}FREE TIER${NC}"
    echo
    echo -e "┌─────────────────────────────────────────────────────────────┐"
    echo -e "│  Virtual Bankroll:    ${GREEN}\$${VIRTUAL}${NC}"
    echo -e "│  Starting Bankroll:   \$${STARTING}"
    
    if (( $(echo "$PROFIT >= 0" | bc -l) )); then
        echo -e "│  Virtual P&L:         ${GREEN}+\$${PROFIT}${NC}"
    else
        echo -e "│  Virtual P&L:         ${RED}\$${PROFIT}${NC}"
    fi
    
    echo -e "│"
    echo -e "│  ${YELLOW}Pending USDC Payout:  \$${PENDING_PAYOUT}${NC}"
    echo -e "│  (Earned at \$50 per \$500 virtual profit)"
    echo -e "└─────────────────────────────────────────────────────────────┘"
else
    BALANCE=$(echo "$WALLET_INFO" | jq -r '.balance // 0')
    PENDING=$(echo "$WALLET_INFO" | jq -r '.pending_amount // 0')
    AVAILABLE=$(echo "$WALLET_INFO" | jq -r '.available_for_withdrawal // 0')
    
    echo -e "${CYAN}PAID TIER${NC}"
    echo
    echo -e "┌─────────────────────────────────────────────────────────────┐"
    echo -e "│  USDC Balance:        ${GREEN}\$${BALANCE}${NC}"
    echo -e "│  Pending Bets:        ${YELLOW}\$${PENDING}${NC}"
    echo -e "│  Available to Withdraw: ${GREEN}\$${AVAILABLE}${NC}"
    echo -e "│"
    echo -e "│  Total Deposited:     \$${TOTAL_DEPOSITED}"
    echo -e "│  Total Withdrawn:     \$${TOTAL_WITHDRAWN}"
    echo -e "└─────────────────────────────────────────────────────────────┘"
fi

echo
echo -e "Deposit Address:    ${CYAN}${DEPOSIT_ADDR}${NC}"
echo -e "Withdrawal Address: ${CYAN}${WITHDRAWAL_ADDR}${NC}"
echo

# Show recent transactions
TX_COUNT=$(echo "$TRANSACTIONS" | jq -r '.total // 0')
TX_LIST=$(echo "$TRANSACTIONS" | jq -r '.transactions // []')

if [ "$TX_COUNT" -gt 0 ]; then
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  Recent Transactions (${TX_COUNT} total)${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    
    # Parse and display transactions
    echo "$TX_LIST" | jq -r '.[] | "\(.type)|\(.amount)|\(.status)|\(.created_at)|\(.description // "")"' | while IFS='|' read -r TYPE AMOUNT STATUS CREATED DESC; do
        # Format date
        if [ -n "$CREATED" ] && [ "$CREATED" != "null" ]; then
            DATE=$(echo "$CREATED" | cut -c1-10)
        else
            DATE="Unknown"
        fi
        
        # Color code amount
        if (( $(echo "$AMOUNT >= 0" | bc -l 2>/dev/null || echo 0) )); then
            AMOUNT_FMT="${GREEN}+\$${AMOUNT}${NC}"
        else
            AMOUNT_FMT="${RED}\$${AMOUNT}${NC}"
        fi
        
        # Type icon
        case "$TYPE" in
            deposit)      ICON="📥" ;;
            withdrawal)   ICON="📤" ;;
            bet_won)      ICON="✅" ;;
            bet_lost)     ICON="❌" ;;
            payout)       ICON="💰" ;;
            *)            ICON="📝" ;;
        esac
        
        # Status color
        case "$STATUS" in
            completed|won)   STATUS_FMT="${GREEN}${STATUS}${NC}" ;;
            pending)         STATUS_FMT="${YELLOW}${STATUS}${NC}" ;;
            failed|lost)     STATUS_FMT="${RED}${STATUS}${NC}" ;;
            *)               STATUS_FMT="${STATUS}" ;;
        esac
        
        # Truncate description
        if [ ${#DESC} -gt 40 ]; then
            DESC="${DESC:0:37}..."
        fi
        
        echo -e "  ${ICON} ${DATE}  ${AMOUNT_FMT}  ${STATUS_FMT}"
        if [ -n "$DESC" ] && [ "$DESC" != "null" ]; then
            echo -e "     ${MAGENTA}${DESC}${NC}"
        fi
    done
else
    echo -e "${YELLOW}No transactions yet.${NC}"
fi

echo
