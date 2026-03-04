#!/usr/bin/env bash
set -euo pipefail

# Bitpanda API CLI wrapper
# Read-only portfolio and transaction viewer

API_BASE="https://api.bitpanda.com/v1"

# Load API key: env var > credentials file
CRED_FILE="${HOME}/.openclaw/credentials/bitpanda/config.json"
if [[ -z "${BITPANDA_API_KEY:-}" && -f "$CRED_FILE" ]]; then
    BITPANDA_API_KEY=$(jq -r '.api_key // empty' "$CRED_FILE" 2>/dev/null || true)
fi
API_KEY="${BITPANDA_API_KEY:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Check if API key is set
check_api_key() {
    if [[ -z "$API_KEY" ]]; then
        echo -e "${RED}Error: BITPANDA_API_KEY environment variable not set${NC}" >&2
        echo "Generate your API key at: https://web.bitpanda.com/my-account/apikey" >&2
        exit 1
    fi
}

# Make API request with error handling
api_request() {
    local endpoint="$1"
    local response
    local http_code
    
    # Make request and capture both response and HTTP code
    response=$(curl -s -w "\n%{http_code}" \
        -H "X-Api-Key: $API_KEY" \
        -H "Accept: application/json" \
        "$API_BASE$endpoint")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    # Check HTTP status
    if [[ "$http_code" != "200" ]]; then
        echo -e "${RED}API Error (HTTP $http_code)${NC}" >&2
        if echo "$body" | jq -e '.error' &>/dev/null; then
            echo "$body" | jq -r '.error' >&2
        else
            echo "$body" >&2
        fi
        return 1
    fi
    
    echo "$body"
}

# Format number with proper decimals
format_amount() {
    local amount="$1"
    local decimals="${2:-8}"
    
    # Remove trailing zeros and decimal point if not needed
    printf "%.${decimals}f" "$amount" | sed 's/\.0*$//;s/\(\.[0-9]*[1-9]\)0*$/\1/'
}

# Get all wallets with pagination
get_all_wallets() {
    local page_size=100
    local all_data="[]"
    local next_cursor=""
    local first=true
    
    while true; do
        local endpoint="/wallets?page_size=$page_size"
        [[ -n "$next_cursor" ]] && endpoint="${endpoint}&after=$next_cursor"
        
        local response
        response=$(api_request "$endpoint") || return 1
        
        # Merge data
        if [[ "$first" == "true" ]]; then
            all_data="$response"
            first=false
        else
            all_data=$(echo "$all_data" | jq --argjson new "$response" '.data += $new.data')
        fi
        
        # Check for next page
        next_cursor=$(echo "$response" | jq -r '.meta.next_cursor // empty')
        [[ -z "$next_cursor" ]] && break
    done
    
    echo "$all_data"
}

# Command: list wallets
cmd_wallets() {
    check_api_key
    
    echo -e "${BOLD}Fetching wallets...${NC}"
    local data
    data=$(get_all_wallets) || exit 1
    
    # Fetch fiat wallets
    local fiat_data
    fiat_data=$(api_request "/fiatwallets") || fiat_data='{"data":[]}'
    
    # Merge fiat into data (normalize fields)
    data=$(echo "$data" "$fiat_data" | jq -s '
        { data: (
            .[0].data + 
            [.[1].data[] | .attributes += {"cryptocoin_symbol": .attributes.fiat_symbol, "deleted": false}]
        )}
    ')
    
    # Parse and display
    echo "$data" | jq -r '
        .data[] |
        [
            .attributes.cryptocoin_symbol // .attributes.fiat_symbol // .attributes.commodity_symbol // "???",
            .attributes.name,
            .attributes.balance,
            .attributes.deleted,
            .id
        ] | @tsv
    ' | while IFS=$'\t' read -r symbol name balance deleted wallet_id; do
        # Skip deleted and zero-balance wallets
        [[ "$deleted" == "true" ]] && continue
        (( $(echo "$balance == 0" | bc -l) )) && continue
        
        # Format balance
        local formatted_balance
        formatted_balance=$(format_amount "$balance")
        
        # Color code based on balance
        if (( $(echo "$balance > 0" | bc -l) )); then
            echo -e "${GREEN}●${NC} ${BOLD}$symbol${NC} ($name)"
            echo -e "  Balance: ${GREEN}$formatted_balance${NC}"
            echo -e "  Wallet ID: $wallet_id"
        else
            echo -e "○ $symbol ($name)"
            echo -e "  Balance: $formatted_balance"
            echo -e "  Wallet ID: $wallet_id"
        fi
        echo
    done
}

# Command: portfolio summary
cmd_portfolio() {
    check_api_key
    
    echo -e "${BOLD}Fetching portfolio...${NC}\n"
    local data
    data=$(get_all_wallets) || exit 1
    
    # Fetch fiat wallets separately
    local fiat_data
    fiat_data=$(api_request "/fiatwallets") || fiat_data='{"data":[]}'
    
    # Group by type
    local crypto_wallets
    local fiat_wallets
    local index_wallets
    
    crypto_wallets=$(echo "$data" | jq -r '.data[] | select(.attributes.cryptocoin_symbol != null and .attributes.deleted == false and (.attributes.balance | tonumber) > 0)')
    fiat_wallets=$(echo "$fiat_data" | jq -r '.data[] | select((.attributes.balance | tonumber) > 0)')
    index_wallets=$(echo "$data" | jq -r '.data[] | select(.attributes.is_index == true and .attributes.deleted == false and (.attributes.balance | tonumber) > 0)')
    
    # Display cryptocurrency holdings
    if [[ -n "$crypto_wallets" ]]; then
        echo -e "${BOLD}${BLUE}━━━ CRYPTO ━━━${NC}"
        echo "$crypto_wallets" | jq -rs '.[] | [.attributes.cryptocoin_symbol, .attributes.balance] | @tsv' | \
        while IFS=$'\t' read -r symbol balance; do
            local formatted_balance
            formatted_balance=$(format_amount "$balance")
            echo -e "  ${GREEN}$symbol${NC}: $formatted_balance"
        done
        echo
    fi
    
    # Display fiat holdings
    if [[ -n "$fiat_wallets" ]]; then
        echo -e "${BOLD}${BLUE}━━━ FIAT ━━━${NC}"
        echo "$fiat_wallets" | jq -rs '.[] | [(.attributes.fiat_symbol // .attributes.name), .attributes.balance] | @tsv' | \
        while IFS=$'\t' read -r symbol balance; do
            local formatted_balance
            formatted_balance=$(format_amount "$balance" 2)
            echo -e "  ${YELLOW}$symbol${NC}: $formatted_balance"
        done
        echo
    fi
    
    # Display index holdings
    if [[ -n "$index_wallets" ]]; then
        echo -e "${BOLD}${BLUE}━━━ INDEX ━━━${NC}"
        echo "$index_wallets" | jq -rs '.[] | [.attributes.index_symbol, .attributes.balance, .attributes.name] | @tsv' | \
        while IFS=$'\t' read -r symbol balance name; do
            local formatted_balance
            formatted_balance=$(format_amount "$balance")
            echo -e "  ${GREEN}$symbol${NC} ($name): $formatted_balance"
        done
        echo
    fi
    
    # Count non-zero wallets
    local crypto_count fiat_count total_nonzero
    crypto_count=$(echo "$data" | jq '[.data[] | select(.attributes.deleted == false and (.attributes.balance | tonumber) > 0)] | length')
    fiat_count=$(echo "$fiat_data" | jq '[.data[] | select((.attributes.balance | tonumber) > 0)] | length')
    total_nonzero=$((crypto_count + fiat_count))
    echo -e "${BOLD}Total non-zero wallets: $total_nonzero${NC}"
}

# Command: list transactions
cmd_transactions() {
    check_api_key
    
    local wallet_id=""
    local flow=""
    local from_date=""
    local to_date=""
    local limit=100
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --wallet)
                wallet_id="$2"
                shift 2
                ;;
            --flow)
                flow="$2"
                shift 2
                ;;
            --from)
                from_date="$2"
                shift 2
                ;;
            --to)
                to_date="$2"
                shift 2
                ;;
            --limit)
                limit="$2"
                shift 2
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}" >&2
                exit 1
                ;;
        esac
    done
    
    # Build query params
    local params="page_size=100"
    [[ -n "$flow" ]] && params="${params}&type=$flow"
    
    echo -e "${BOLD}Fetching trades...${NC}"
    
    # Fetch with pagination
    local all_data="[]"
    local next_cursor=""
    local first=true
    local count=0
    
    while [[ $count -lt $limit ]]; do
        local endpoint="/trades?$params"
        [[ -n "$next_cursor" ]] && endpoint="${endpoint}&cursor=$next_cursor&page_size=100"
        
        local response
        response=$(api_request "$endpoint") || exit 1
        
        # Merge data
        if [[ "$first" == "true" ]]; then
            all_data="$response"
            first=false
        else
            all_data=$(echo "$all_data" | jq --argjson new "$response" '.data += $new.data')
        fi
        
        local fetched
        fetched=$(echo "$response" | jq '.data | length')
        count=$((count + fetched))
        
        # Check for next page
        next_cursor=$(echo "$response" | jq -r '.meta.next_cursor // empty')
        [[ -z "$next_cursor" || $count -ge $limit ]] && break
    done
    
    # Limit to requested amount
    all_data=$(echo "$all_data" | jq --argjson limit "$limit" '.data |= .[:$limit]')
    
    # Display trades
    echo "$all_data" | jq -r '
        .data[] |
        [
            .attributes.time.date_iso8601,
            .attributes.type,
            .attributes.cryptocoin_symbol // "???",
            .attributes.amount_cryptocoin,
            .attributes.amount_fiat,
            .attributes.price,
            .attributes.status,
            .id
        ] | @tsv
    ' | while IFS=$'\t' read -r timestamp type symbol amount_crypto amount_fiat price status tx_id; do
        # Format timestamp
        local date
        date=$(date -d "$timestamp" '+%Y-%m-%d %H:%M' 2>/dev/null || echo "$timestamp")
        
        # Color based on type
        local color="$NC"
        [[ "$type" == "buy" ]] && color="$GREEN"
        [[ "$type" == "sell" ]] && color="$RED"
        
        local formatted_crypto formatted_fiat
        formatted_crypto=$(format_amount "$amount_crypto")
        formatted_fiat=$(format_amount "$amount_fiat" 2)
        
        echo -e "${BOLD}$date${NC} | ${color}${type^^}${NC} $symbol"
        echo -e "  Amount: $formatted_crypto $symbol @ €$price"
        echo -e "  Value: €$formatted_fiat | Status: $status"
        echo
    done
    
    local total
    total=$(echo "$all_data" | jq '.data | length')
    echo -e "${BOLD}Showing $total trade(s)${NC}"
}

# Command: get asset info
cmd_asset() {
    check_api_key
    
    local symbol="${1:-}"
    if [[ -z "$symbol" ]]; then
        echo -e "${RED}Error: asset symbol required${NC}" >&2
        echo "Usage: bitpanda asset <SYMBOL>  (e.g. BTC, ETH, DOGE)" >&2
        exit 1
    fi
    
    symbol=$(echo "$symbol" | tr '[:lower:]' '[:upper:]')
    echo -e "${BOLD}Fetching price for: $symbol${NC}\n"
    
    # Ticker is public, no auth needed
    local ticker
    ticker=$(curl -sf "https://api.bitpanda.com/v1/ticker" 2>/dev/null) || {
        echo -e "${RED}Error fetching ticker data${NC}" >&2
        exit 1
    }
    
    local price
    price=$(echo "$ticker" | jq -r --arg s "$symbol" '.[$s].EUR // empty')
    
    if [[ -z "$price" ]]; then
        echo -e "${RED}Asset '$symbol' not found in ticker${NC}" >&2
        exit 1
    fi
    
    echo -e "  ${BOLD}$symbol${NC}"
    echo -e "  Price: ${GREEN}€$price${NC}"
    
    # If we have an API key, also show wallet balance
    if [[ -n "$API_KEY" ]]; then
        local balance
        balance=$(curl -sf -H "X-Api-Key: $API_KEY" "https://api.bitpanda.com/v1/wallets?page_size=100" | \
            jq -r --arg s "$symbol" '.data[] | select(.attributes.cryptocoin_symbol == $s and .attributes.deleted == false) | .attributes.balance' 2>/dev/null)
        if [[ -n "$balance" ]]; then
            local formatted_balance
            formatted_balance=$(format_amount "$balance")
            if (( $(echo "$balance > 0" | bc -l) )); then
                local value
                value=$(echo "$balance * $price" | bc -l 2>/dev/null)
                value=$(format_amount "$value" 2)
                echo -e "  Balance: ${GREEN}$formatted_balance${NC}"
                echo -e "  Value: ${GREEN}€$value${NC}"
            else
                echo -e "  Balance: 0"
            fi
        fi
    fi
}

# Main command dispatcher
main() {
    if [[ $# -eq 0 ]]; then
        echo "Bitpanda API CLI"
        echo
        echo "Usage: bitpanda <command> [options]"
        echo
        echo "Commands:"
        echo "  portfolio              Show portfolio summary (grouped by type)"
        echo "  wallets                List all wallets with balances"
        echo "  transactions [opts]    List trades (buy/sell history)"
        echo "  asset <SYMBOL>         Get current price + balance for an asset"
        echo
        echo "Transaction options:"
        echo "  --flow buy|sell        Filter by trade type"
        echo "  --limit <N>            Limit results (default: 100)"
        echo
        echo "Examples:"
        echo "  bitpanda portfolio"
        echo "  bitpanda wallets"
        echo "  bitpanda transactions --limit 20"
        echo "  bitpanda transactions --flow buy"
        echo "  bitpanda asset BTC"
        exit 0
    fi
    
    local command="$1"
    shift
    
    case "$command" in
        portfolio)
            cmd_portfolio "$@"
            ;;
        wallets)
            cmd_wallets "$@"
            ;;
        transactions)
            cmd_transactions "$@"
            ;;
        asset)
            cmd_asset "$@"
            ;;
        *)
            echo -e "${RED}Unknown command: $command${NC}" >&2
            exit 1
            ;;
    esac
}

main "$@"
