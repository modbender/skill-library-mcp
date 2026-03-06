#!/bin/bash
#
# Check if Gateway is running via Hummingbot API.
#
# Usage:
#   # Source in another script to get check_gateway function
#   source "$(dirname "$0")/check_gateway.sh"
#   check_gateway || exit 1
#
#   # Or run directly for status output
#   bash scripts/check_gateway.sh
#   bash scripts/check_gateway.sh --json
#
# Requires: Hummingbot API running (sources check_api.sh)
#
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load .env if present
for f in hummingbot-api/.env ~/.hummingbot/.env .env; do
    if [ -f "$f" ]; then
        set -a; source "$f"; set +a
        break
    fi
done

API_URL="${HUMMINGBOT_API_URL:-http://localhost:8000}"
API_USER="${API_USER:-admin}"
API_PASS="${API_PASS:-admin}"

check_gateway() {
    local auth status running
    auth=$(echo -n "$API_USER:$API_PASS" | base64)
    status=$(curl -s -H "Authorization: Basic $auth" -H "Content-Type: application/json" "$API_URL/gateway/status" 2>/dev/null || echo '{}')
    running=$(echo "$status" | python3 -c "import sys,json; print(json.load(sys.stdin).get('running', False))" 2>/dev/null || echo "False")
    [ "$running" = "True" ]
}

# Only produce output when run directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # First check API is running
    source "$SCRIPT_DIR/check_api.sh"
    if ! check_api; then
        JSON=false
        [[ "${1:-}" == "--json" ]] && JSON=true
        if [ "$JSON" = "true" ]; then
            echo '{"running": false, "message": "Hummingbot API is not running", "next": "Run: /lp-agent deploy-hummingbot-api"}'
        else
            echo "Hummingbot API is not running at $API_URL"
            echo "Run: /lp-agent deploy-hummingbot-api"
        fi
        exit 1
    fi

    JSON=false
    [[ "${1:-}" == "--json" ]] && JSON=true

    if check_gateway; then
        if [ "$JSON" = "true" ]; then
            echo '{"running": true, "message": "Gateway is running"}'
        else
            echo "Gateway is running"
        fi
        exit 0
    else
        if [ "$JSON" = "true" ]; then
            echo '{"running": false, "message": "Gateway is not running", "next": "Run: /lp-agent setup-gateway"}'
        else
            echo "Gateway is not running"
            echo "Run: /lp-agent setup-gateway"
        fi
        exit 1
    fi
fi
