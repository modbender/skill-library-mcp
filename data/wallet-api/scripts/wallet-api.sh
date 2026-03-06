#!/bin/bash
# Wallet API CLI helper
# Usage: ./wallet-api.sh <command> [options]

set -e

API_BASE="https://rest.budgetbakers.com/wallet"
TOKEN="${WALLET_API_TOKEN:-}"

if [ -z "$TOKEN" ]; then
    echo "Error: WALLET_API_TOKEN environment variable not set"
    echo "Get your token from: https://web.budgetbakers.com/settings/apiTokens"
    exit 1
fi

# Helper function for API calls
api_call() {
    local method="$1"
    local endpoint="$2"
    local params="${3:-}"
    
    local url="${API_BASE}${endpoint}"
    [ -n "$params" ] && url="${url}?${params}"
    
    curl -s \
        -H "Authorization: Bearer ${TOKEN}" \
        -H "Accept: application/json" \
        "$url"
}

# Commands
case "${1:-}" in
    me)
        api_call GET "/me"
        ;;
    accounts)
        api_call GET "/accounts" "${2:-}"
        ;;
    categories)
        api_call GET "/categories" "${2:-}"
        ;;
    records)
        api_call GET "/records" "${2:-}"
        ;;
    budgets)
        api_call GET "/budgets" "${2:-}"
        ;;
    templates)
        api_call GET "/templates" "${2:-}"
        ;;
    *)
        echo "Wallet API CLI"
        echo ""
        echo "Usage: $0 <command> [query-params]"
        echo ""
        echo "Commands:"
        echo "  me          Get current user info"
        echo "  accounts    List accounts [?limit=30&offset=0]"
        echo "  categories  List categories [?limit=30&offset=0]"
        echo "  records     List transactions [?limit=30&offset=0&recordDate=gte.2025-01-01]"
        echo "  budgets     List budgets [?limit=30&offset=0]"
        echo "  templates   List templates [?limit=30&offset=0]"
        echo ""
        echo "Environment:"
        echo "  WALLET_API_TOKEN    Your API token (required)"
        echo ""
        echo "Examples:"
        echo "  $0 me"
        echo "  $0 records 'limit=50&recordDate=gte.2025-02-01'"
        echo "  $0 records 'amount=gte.100&amount=lte.500'"
        exit 1
        ;;
esac
