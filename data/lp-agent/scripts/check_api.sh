#!/bin/bash
#
# Check if Hummingbot API is running.
#
# Usage:
#   # Source in another script to get check_api function
#   source "$(dirname "$0")/check_api.sh"
#   check_api || exit 1
#
#   # Or run directly for status output
#   bash scripts/check_api.sh
#   bash scripts/check_api.sh --json
#
set -e

# Load .env if present
for f in hummingbot-api/.env ~/.hummingbot/.env .env; do
    if [ -f "$f" ]; then
        set -a; source "$f"; set +a
        break
    fi
done

API_URL="${HUMMINGBOT_API_URL:-http://localhost:8000}"

check_api() {
    local response
    response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/" 2>/dev/null || echo "000")
    [ "$response" = "200" ]
}

# Only produce output when run directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    JSON=false
    [[ "${1:-}" == "--json" ]] && JSON=true

    if check_api; then
        if [ "$JSON" = "true" ]; then
            echo '{"running": true, "url": "'"$API_URL"'", "message": "Hummingbot API is running"}'
        else
            echo "Hummingbot API is running at $API_URL"
        fi
        exit 0
    else
        if [ "$JSON" = "true" ]; then
            echo '{"running": false, "url": "'"$API_URL"'", "message": "Cannot connect to Hummingbot API", "next": "Run: /lp-agent deploy-hummingbot-api"}'
        else
            echo "Cannot connect to Hummingbot API at $API_URL"
            echo "Run: /lp-agent deploy-hummingbot-api"
        fi
        exit 1
    fi
fi
