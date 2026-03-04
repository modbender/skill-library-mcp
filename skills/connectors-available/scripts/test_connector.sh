#!/bin/bash
# Test if a connector is accessible from current location
# Usage: ./test_connector.sh --connector <name> [--timeout 10]

# Load .env if present
for f in hummingbot-api/.env ~/.hummingbot/.env .env; do
    if [ -f "$f" ]; then
        set -a; source "$f"; set +a
        break
    fi
done

CONNECTOR=""
API_URL="${HUMMINGBOT_API_URL:-http://localhost:8000}"
API_USER="${API_USER:-admin}"
API_PASS="${API_PASS:-admin}"
TIMEOUT=10

while [[ $# -gt 0 ]]; do
    case $1 in
        --connector) CONNECTOR="$2"; shift 2 ;;
        --timeout) TIMEOUT="$2"; shift 2 ;;
        *) shift ;;
    esac
done

if [[ -z "$CONNECTOR" ]]; then
    echo "Error: --connector is required"
    exit 1
fi

# Test by fetching trading rules - if it returns data, connector is available
result=$(curl -s -u "$API_USER:$API_PASS" --max-time "$TIMEOUT" \
    "$API_URL/connectors/$CONNECTOR/trading-rules" 2>&1)

# Check for error responses
if echo "$result" | grep -q '"detail"'; then
    error=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('detail','Unknown error')[:80])" 2>/dev/null)
    echo "FAILED|$error"
    exit 1
fi

# Check if valid trading rules returned
if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if isinstance(d,dict) and len(d)>0 else 1)" 2>/dev/null; then
    pairs=$(echo "$result" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null)
    echo "SUCCESS|$pairs pairs"
    exit 0
else
    echo "FAILED|No trading pairs returned"
    exit 1
fi
