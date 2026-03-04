#!/usr/bin/env bash
# proxybase-topup.sh — Top up bandwidth on an existing ProxyBase order
# Usage: bash proxybase-topup.sh <order_id> <package_id> [pay_currency]
#
# Example:
#   bash proxybase-topup.sh gmp6vp2k us_residential_1gb
#   bash proxybase-topup.sh gmp6vp2k us_residential_5gb btc
#
# This extends bandwidth on an active proxy without changing credentials.

set -euo pipefail

# Source shared library
source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

ORDER_ID="${1:-}"
PACKAGE_ID="${2:-}"
PAY_CURRENCY="${3:-usdttrc20}"

if [[ -z "$ORDER_ID" || -z "$PACKAGE_ID" ]]; then
    echo "ERROR: order_id and package_id are required"
    echo "Usage: bash proxybase-topup.sh <order_id> <package_id> [pay_currency]"
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
    '{package_id: $pkg, pay_currency: $cur}')

echo "ProxyBase: Creating top-up for order $ORDER_ID (package=$PACKAGE_ID, currency=$PAY_CURRENCY)..."

TOPUP_RC=0
api_call_with_retry POST "/orders/$ORDER_ID/topup" \
    -H "Content-Type: application/json" \
    -d "$REQUEST_BODY" || TOPUP_RC=$?

if [[ $TOPUP_RC -ne 0 ]]; then
    echo "ERROR: Top-up failed (HTTP $API_HTTP_CODE)"
    if validate_json "$API_RESPONSE"; then
        echo "$API_RESPONSE" | jq .
    else
        echo "$API_RESPONSE"
    fi
    exit 1
fi

# Extract payment details
TOPUP_PAY_ADDRESS=$(echo "$API_RESPONSE" | jq -r '.pay_address // "unknown"')
TOPUP_PAY_AMOUNT=$(echo "$API_RESPONSE" | jq -r '.pay_amount // "unknown"')
TOPUP_CURRENCY=$(echo "$API_RESPONSE" | jq -r '.pay_currency // "unknown"')
TOPUP_STATUS=$(echo "$API_RESPONSE" | jq -r '.status // "payment_pending"')
TOPUP_EXPIRY=$(echo "$API_RESPONSE" | jq -r '.expiration_estimate_date // "~24 hours"')

# Update order in state file — record the top-up
acquire_lock

if jq -e ".orders[] | select(.order_id == \"$ORDER_ID\")" "$ORDERS_FILE" > /dev/null 2>&1; then
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    UPDATED=$(jq --arg oid "$ORDER_ID" --arg ts "$TIMESTAMP" --arg pkg "$PACKAGE_ID" \
        '(.orders[] | select(.order_id == $oid)) |= . + {
            last_topup: $ts,
            topup_package: $pkg,
            status: "topup_pending"
        }' "$ORDERS_FILE")
    if validate_json "$UPDATED"; then
        echo "$UPDATED" > "$ORDERS_FILE"
    fi
else
    echo "WARN: Order $ORDER_ID not found in local state — top-up not tracked locally" >&2
fi

release_lock

# Output
echo ""
echo "========================================"
echo "  TOP-UP CREATED"
echo "========================================"
echo ""
echo "  Order ID:   $ORDER_ID"
echo "  Top-up:     $PACKAGE_ID"
echo ""
echo "  PAYMENT DETAILS:"
echo "  Send exactly: $TOPUP_PAY_AMOUNT $TOPUP_CURRENCY"
echo "  To address:   $TOPUP_PAY_ADDRESS"
echo "  Expires:      $TOPUP_EXPIRY"
echo ""
echo "  Status:       $TOPUP_STATUS"
echo ""
echo "========================================"
echo ""
echo "After payment, poll to confirm:"
echo "  bash $SCRIPT_DIR/proxybase-poll.sh $ORDER_ID"
echo ""

# Raw JSON
echo "RAW_JSON:"
echo "$API_RESPONSE" | jq .
