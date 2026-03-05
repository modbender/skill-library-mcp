#!/usr/bin/env bash
#
# auto-fund.sh - Automatically fund Grove account when balance is low
#
# Usage:
#   ./auto-fund.sh [options]
#
# Options:
#   --min-balance <amount>     Auto-fund when balance < this (default: 0.10)
#   --fund-amount <amount>     Amount to fund (default: 1.00)
#   --max-balance <amount>     Don't fund if balance > this (default: 10.00)
#   --network <network>        Network to use (default: base)
#   --dry-run                  Check only, don't fund
#   --help                     Show this help message
#
# Safety features:
#   - Won't fund if balance is above --max-balance
#   - Requires confirmation unless --yes is passed
#   - Validates wallet has sufficient USDC + ETH
#
# Requires a wallet (keyfile.txt) with USDC + ETH on Base. See: grove setup
# Full documentation: https://grove.city/docs/skills
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
MIN_BALANCE="0.10"
FUND_AMOUNT="1.00"
MAX_BALANCE="10.00"
NETWORK="${DEFAULT_NETWORK:-base}"
DRY_RUN=false
SKIP_CONFIRM=false

# Usage function
usage() {
    cat << EOF
Usage: $0 [options]

Automatically fund Grove account when balance is low.

Options:
    --min-balance <amount>     Fund when balance < this (default: 0.10)
    --fund-amount <amount>     Amount to fund (default: 1.00)
    --max-balance <amount>     Don't fund if balance > this (default: 10.00)
    --network <network>        Network to use (default: base)
    --dry-run                  Check only, don't fund
    --yes                      Skip confirmation prompt
    --help                     Show this help message

Safety Features:
    - Won't fund if balance > max-balance (prevents over-funding)
    - Checks wallet has sufficient USDC + ETH before funding
    - Requires confirmation unless --yes is passed

Examples:
    $0                                              # Use defaults
    $0 --min-balance 0.50 --fund-amount 5.00        # Custom thresholds
    $0 --max-balance 20.00                          # Higher max
    $0 --network base-sepolia                       # Testnet
    $0 --dry-run                                    # Check without funding
    $0 --yes                                        # Auto-confirm

Typical cron usage:
    */15 * * * * /path/to/auto-fund.sh --yes >> /var/log/grove-auto-fund.log 2>&1

EOF
    exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --min-balance)
            MIN_BALANCE="$2"
            shift 2
            ;;
        --fund-amount)
            FUND_AMOUNT="$2"
            shift 2
            ;;
        --max-balance)
            MAX_BALANCE="$2"
            shift 2
            ;;
        --network)
            NETWORK="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --yes)
            SKIP_CONFIRM=true
            shift
            ;;
        --help)
            usage
            ;;
        *)
            echo -e "${RED}Error: Unknown argument: $1${NC}" >&2
            usage
            ;;
    esac
done

# Check if grove CLI is available
if ! command -v grove &> /dev/null; then
    echo -e "${RED}Error: grove CLI not found${NC}" >&2
    echo "Install with: curl -fsSL https://grove.city/install-cli.sh | bash" >&2
    exit 1
fi

# Check if bc is available
if ! command -v bc &> /dev/null; then
    echo -e "${YELLOW}Warning: 'bc' not found, using integer comparison${NC}" >&2
fi

# Compare floating point numbers
compare_balance() {
    local balance="$1"
    local threshold="$2"

    if command -v bc &> /dev/null; then
        if (( $(echo "$balance < $threshold" | bc -l) )); then
            return 0  # balance < threshold
        else
            return 1  # balance >= threshold
        fi
    else
        balance_cents=$(echo "$balance * 100" | awk '{print int($1)}')
        threshold_cents=$(echo "$threshold * 100" | awk '{print int($1)}')

        if [[ $balance_cents -lt $threshold_cents ]]; then
            return 0
        else
            return 1
        fi
    fi
}

# Main logic
echo -e "${BLUE}🤖 Grove Auto-Fund${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Min balance:    $MIN_BALANCE USDC"
echo "Fund amount:    $FUND_AMOUNT USDC"
echo "Max balance:    $MAX_BALANCE USDC"
echo "Network:        $NETWORK"
if [[ "$DRY_RUN" == "true" ]]; then
    echo -e "Mode:           ${YELLOW}DRY RUN${NC}"
fi
echo ""

# Check current balance
echo -e "${BLUE}💰 Checking current balance...${NC}"

balance_json=$(grove balance --json 2>&1)
if [[ $? -ne 0 ]]; then
    echo -e "${RED}✗ Failed to check balance${NC}" >&2
    echo "$balance_json" >&2
    exit 1
fi

current_balance=$(echo "$balance_json" | jq -r '.total_balance' 2>/dev/null)
if [[ -z "$current_balance" ]] || [[ "$current_balance" == "null" ]]; then
    echo -e "${RED}✗ Failed to parse balance${NC}" >&2
    exit 1
fi

echo "  Current balance: $current_balance USDC"
echo ""

# Check if balance is above max (safety check)
if ! compare_balance "$current_balance" "$MAX_BALANCE"; then
    echo -e "${GREEN}✓ Balance is above maximum threshold ($MAX_BALANCE USDC)${NC}"
    echo "  No funding needed."
    exit 0
fi

# Check if balance is below minimum
if ! compare_balance "$current_balance" "$MIN_BALANCE"; then
    echo -e "${GREEN}✓ Balance is above minimum threshold ($MIN_BALANCE USDC)${NC}"
    echo "  No funding needed."
    exit 0
fi

# Balance is low - need to fund
echo -e "${YELLOW}⚠️  Balance is below minimum threshold${NC}"
echo "  Current: $current_balance USDC"
echo "  Minimum: $MIN_BALANCE USDC"
echo ""

# Calculate new balance after funding
new_balance=$(echo "$current_balance + $FUND_AMOUNT" | bc -l)
echo "  Will fund: $FUND_AMOUNT USDC"
echo "  New balance: $new_balance USDC"
echo ""

# Check if new balance would exceed maximum
if ! compare_balance "$new_balance" "$MAX_BALANCE"; then
    echo -e "${YELLOW}⚠️  Warning: New balance ($new_balance USDC) would exceed maximum ($MAX_BALANCE USDC)${NC}"
    echo "  Consider reducing --fund-amount or increasing --max-balance"
    echo ""
fi

# Dry run - stop here
if [[ "$DRY_RUN" == "true" ]]; then
    echo -e "${YELLOW}🚫 Dry run mode - would fund $FUND_AMOUNT USDC${NC}"
    exit 0
fi

# Confirm funding
if [[ "$SKIP_CONFIRM" == "false" ]]; then
    echo -e "${YELLOW}⚠️  About to fund $FUND_AMOUNT USDC${NC}"
    read -p "Continue? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
    echo ""
fi

# Check if wallet exists and has sufficient funds
echo -e "${BLUE}🔍 Checking wallet...${NC}"

if [[ ! -f ~/.grove/keyfile.txt ]]; then
    echo -e "${RED}✗ Wallet not found${NC}" >&2
    echo "  Run: grove keygen --save" >&2
    exit 1
fi

echo "  Wallet: OK"
echo ""

# Execute funding
echo -e "${BLUE}💸 Funding account...${NC}"

fund_result=$(grove fund "$FUND_AMOUNT" --network "$NETWORK" --json 2>&1)
if [[ $? -ne 0 ]]; then
    echo -e "${RED}✗ Funding failed${NC}" >&2
    echo "$fund_result" >&2
    exit 1
fi

# Parse result
funded_amount=$(echo "$fund_result" | jq -r '.funded_amount' 2>/dev/null)
new_balance_actual=$(echo "$fund_result" | jq -r '.new_balance' 2>/dev/null)
tx_hash=$(echo "$fund_result" | jq -r '.tx_hash' 2>/dev/null)

if [[ -z "$funded_amount" ]] || [[ "$funded_amount" == "null" ]]; then
    echo -e "${RED}✗ Failed to parse funding result${NC}" >&2
    exit 1
fi

echo -e "${GREEN}✓ Funding successful!${NC}"
echo ""
echo "  Funded:      $funded_amount USDC"
echo "  New balance: $new_balance_actual USDC"
if [[ -n "$tx_hash" ]] && [[ "$tx_hash" != "null" ]]; then
    echo "  TX:          $tx_hash"
fi
echo ""

echo -e "${GREEN}✓ Done!${NC}"
exit 0
