#!/bin/bash
# CEORater API Helper Script
# Usage: ceorater.sh <command> [args]
#
# Commands:
#   get <ticker>       Get CEO data by ticker
#   search <query>     Search by CEO name, company, ticker, sector, or industry
#   list [limit]       List CEOs (default limit: 20)
#
# Requires: CEORATER_API_KEY environment variable
# Get your key at: https://www.ceorater.com/api-docs.html

set -euo pipefail

BASE_URL="https://api.ceorater.com"

# Check for API key
check_auth() {
    if [ -z "$CEORATER_API_KEY" ]; then
        echo "Error: CEORATER_API_KEY environment variable not set"
        echo "Get your API key at: https://www.ceorater.com/api-docs.html"
        exit 1
    fi
}

# Sanitize input: strip any characters that could enable shell injection.
# Allows only alphanumeric chars, spaces, hyphens, underscores, periods, and ampersands.
sanitize() {
    printf '%s' "$1" | tr -cd 'A-Za-z0-9 _.&-'
}

# URL-encode a string using only printf and sed (no command substitution on user input)
urlencode() {
    printf '%s' "$1" | sed \
        -e 's/%/%25/g' \
        -e 's/ /%20/g' \
        -e 's/&/%26/g' \
        -e 's/+/%2B/g' \
        -e 's/#/%23/g'
}

# GET request with auth
api_get() {
    curl -sS --fail-with-body -H "Authorization: Bearer $CEORATER_API_KEY" \
         -H "Content-Type: application/json" \
         "$1"
}

case "${1:-help}" in
    get)
        if [ -z "$2" ]; then
            echo "Usage: ceorater.sh get <ticker>"
            echo "Example: ceorater.sh get AAPL"
            exit 1
        fi
        check_auth
        # Validate: tickers must be 1-5 alphanumeric characters only
        TICKER=$(sanitize "$2")
        if ! printf '%s' "$TICKER" | grep -qE '^[A-Za-z0-9]{1,5}$'; then
            echo "Error: Invalid ticker. Use 1-5 alphanumeric characters (e.g., AAPL)."
            exit 1
        fi
        TICKER=$(printf '%s' "$TICKER" | tr '[:lower:]' '[:upper:]')
        api_get "$BASE_URL/v1/ceo/$TICKER?format=raw"
        ;;

    search)
        if [ -z "$2" ]; then
            echo "Usage: ceorater.sh search <query>"
            echo "Example: ceorater.sh search technology"
            exit 1
        fi
        check_auth
        # Sanitize then URL-encode — no raw user input reaches the shell
        QUERY=$(sanitize "$2")
        QUERY=$(urlencode "$QUERY")
        api_get "$BASE_URL/v1/search?q=$QUERY&format=raw"
        ;;

    list)
        check_auth
        LIMIT="${2:-20}"
        # Validate: limit must be a positive integer <= 2000
        if ! printf '%s' "$LIMIT" | grep -qE '^[0-9]+$'; then
            echo "Error: Limit must be a positive integer."
            exit 1
        fi
        if [ "$LIMIT" -lt 1 ] || [ "$LIMIT" -gt 2000 ]; then
            echo "Error: Limit must be between 1 and 2000."
            exit 1
        fi
        api_get "$BASE_URL/v1/ceos?limit=$LIMIT&format=raw"
        ;;

    meta)
        check_auth
        api_get "$BASE_URL/v1/meta"
        ;;

    help|--help|-h|*)
        echo "CEORater API Helper"
        echo ""
        echo "Usage: ceorater.sh <command> [args]"
        echo ""
        echo "Commands:"
        echo "  get <ticker>     Get CEO data by ticker (e.g., get AAPL)"
        echo "  search <query>   Search by CEO name, company, ticker, sector, or industry"
        echo "  list [limit]     List CEOs (default: 20)"
        echo "  meta             Get live record count and last refresh timestamp"
        echo ""
        echo "Environment:"
        echo "  CEORATER_API_KEY  Your API key (required for get/search/list)"
        echo ""
        echo "Get your API key: https://www.ceorater.com/api-docs.html"
        ;;
esac
