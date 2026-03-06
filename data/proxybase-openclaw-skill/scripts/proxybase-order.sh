#!/usr/bin/env bash
# proxybase-order.sh — Create a ProxyBase order and track it
# Usage: bash proxybase-order.sh <package_id> [pay_currency] [callback_url]
#
# Example:
#   bash proxybase-order.sh us_residential_1gb usdttrc20
#   bash proxybase-order.sh us_residential_5gb btc https://gateway.example.com/hooks/proxybase
#
# Prerequisites:
#   - PROXYBASE_API_KEY and PROXYBASE_API_URL must be set
#   - Run: source scripts/proxybase-register.sh
#
# Output: JSON order details + writes to state/orders.json

set -euo pipefail

# Source shared library
source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

# Validate inputs
PACKAGE_ID="${1:-}"
PAY_CURRENCY="${2:-usdttrc20}"
CALLBACK_URL="${3:-}"

if [[ -z "$PACKAGE_ID" ]]; then
    echo "ERROR: package_id is required"
    echo "Usage: bash proxybase-order.sh <package_id> [pay_currency] [callback_url]"
    echo ""
    echo "Available packages: us_residential_1gb, us_residential_5gb, us_residential_10gb"
    exit 1
fi

load_credentials --required || exit 1
init_orders_file

# Build request body
REQUEST_BODY=$(jq -n \
    --arg pkg "$PACKAGE_ID" \
    --arg cur "$PAY_CURRENCY" \
    --arg cb "$CALLBACK_URL" \
    '{package_id: $pkg, pay_currency: $cur} + (if $cb != "" then {callback_url: $cb} else {} end)')

# Create order (with retry)
echo "ProxyBase: Creating order (package=$PACKAGE_ID, currency=$PAY_CURRENCY)..."

ORDER_RC=0
api_call_with_retry POST "/orders" \
    -H "Content-Type: application/json" \
    -d "$REQUEST_BODY" || ORDER_RC=$?

if [[ $ORDER_RC -ne 0 ]]; then
    echo "ERROR: Order creation failed (HTTP $API_HTTP_CODE)"
    if validate_json "$API_RESPONSE"; then
        echo "$API_RESPONSE" | jq .
    else
        echo "$API_RESPONSE"
    fi
    exit 1
fi

# Extract order_id — validate it's present
ORDER_ID=$(echo "$API_RESPONSE" | jq -r '.order_id // empty')

if [[ -z "$ORDER_ID" || "$ORDER_ID" == "null" ]]; then
    echo "ERROR: No order_id in API response"
    echo "$API_RESPONSE" | jq .
    exit 1
fi

# Extract fields
PAY_ADDRESS=$(echo "$API_RESPONSE" | jq -r '.pay_address // "unknown"')
PAY_AMOUNT=$(echo "$API_RESPONSE" | jq -r '.pay_amount // "unknown"')
RESP_CURRENCY=$(echo "$API_RESPONSE" | jq -r '.pay_currency // "unknown"')
PRICE_USD=$(echo "$API_RESPONSE" | jq -r '.price_usd // "unknown"')
EXPIRATION=$(echo "$API_RESPONSE" | jq -r '.expiration_estimate_date // "~24 hours"')
STATUS=$(echo "$API_RESPONSE" | jq -r '.status // "payment_pending"')

# Track order in orders.json — under lock
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

acquire_lock

UPDATED_ORDERS=$(jq \
    --arg oid "$ORDER_ID" \
    --arg pkg "$PACKAGE_ID" \
    --arg status "$STATUS" \
    --arg ts "$TIMESTAMP" \
    --arg addr "$PAY_ADDRESS" \
    --arg amt "$PAY_AMOUNT" \
    --arg cur "$RESP_CURRENCY" \
    '.orders += [{
        order_id: $oid,
        package_id: $pkg,
        status: $status,
        created_at: $ts,
        pay_address: $addr,
        pay_amount: $amt,
        pay_currency: $cur,
        proxy: null,
        cron_job_id: null
    }]' "$ORDERS_FILE")

if validate_json "$UPDATED_ORDERS"; then
    echo "$UPDATED_ORDERS" > "$ORDERS_FILE"
else
    echo "WARN: Failed to update orders.json — order $ORDER_ID not tracked locally" >&2
fi

release_lock

# Output
echo ""
echo "========================================"
echo "  ORDER CREATED SUCCESSFULLY"
echo "========================================"
echo ""
echo "  Order ID:   $ORDER_ID"
echo "  Package:    $PACKAGE_ID"
echo "  Price:      \$$PRICE_USD USD"
echo ""
echo "  PAYMENT DETAILS:"
echo "  Send exactly: $PAY_AMOUNT $RESP_CURRENCY"
echo "  To address:   $PAY_ADDRESS"
echo "  Expires:      $EXPIRATION"
echo ""
echo "  Status:       $STATUS"
echo ""
echo "========================================"
echo ""
echo "To poll status: bash $SCRIPT_DIR/proxybase-poll.sh $ORDER_ID"
echo ""

# Output raw JSON for programmatic use
echo "RAW_JSON:"
echo "$API_RESPONSE" | jq .

# Machine-parseable marker for pipeline consumption
echo ""
echo "PROXYBASE_ORDER_ID=$ORDER_ID"
