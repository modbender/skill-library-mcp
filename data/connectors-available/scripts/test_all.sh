#!/bin/bash
# Test multiple connectors for availability and save trading rules
# Usage: ./test_all.sh [--connectors "conn1,conn2"] [--timeout 10] [--output file.json]

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
TIMEOUT=10
CONNECTORS=""
OUTPUT_FILE="$SCRIPT_DIR/../data/trading_rules.json"

while [[ $# -gt 0 ]]; do
    case $1 in
        --connectors) CONNECTORS="$2"; shift 2 ;;
        --timeout) TIMEOUT="$2"; shift 2 ;;
        --output) OUTPUT_FILE="$2"; shift 2 ;;
        *) shift ;;
    esac
done

AUTH="-u $API_USER:$API_PASS"

# Create data directory
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Get all connectors if not specified
if [[ -z "$CONNECTORS" ]]; then
    CONNECTORS=$(curl -s $AUTH "$API_URL/connectors/" | python3 -c "import sys,json; print(','.join(json.load(sys.stdin)))")
fi

echo ""
echo "| Connector | Status | Details |"
echo "|-----------|--------|---------|"

# Initialize JSON output
echo "{" > "$OUTPUT_FILE"
first=true

IFS=',' read -ra CONN_ARRAY <<< "$CONNECTORS"

for connector in "${CONN_ARRAY[@]}"; do
    connector=$(echo "$connector" | tr -d ' "[]')
    [[ -z "$connector" ]] && continue

    # Fetch trading rules
    result=$(curl -s $AUTH --max-time "$TIMEOUT" \
        "$API_URL/connectors/$connector/trading-rules" 2>&1)

    # Check for error
    if echo "$result" | grep -q '"detail"'; then
        details=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('detail','Error')[:50])" 2>/dev/null)
        echo "| $connector | ✗ | $details |"
        continue
    fi

    # Check if valid
    pairs=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d)) if isinstance(d,dict) else print(0)" 2>/dev/null)

    if [[ "$pairs" -gt 0 ]]; then
        echo "| $connector | ✓ | $pairs pairs |"

        # Add to JSON file
        if [[ "$first" == "true" ]]; then
            first=false
        else
            echo "," >> "$OUTPUT_FILE"
        fi
        echo "\"$connector\": $result" >> "$OUTPUT_FILE"
    else
        echo "| $connector | ✗ | No trading pairs |"
    fi
done

echo "}" >> "$OUTPUT_FILE"

echo ""
echo "Trading rules saved to: $OUTPUT_FILE"
