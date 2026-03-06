#!/usr/bin/env bash
# proxybase-rotate.sh — Rotate proxy credentials on an active order
# Usage: bash proxybase-rotate.sh <order_id>
#
# Example:
#   bash proxybase-rotate.sh gmp6vp2k
#
# This rotates the SOCKS5 username/password on an active proxy.
# The new credentials are updated in orders.json and .proxy-env.

set -euo pipefail

# Source shared library
source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

ORDER_ID="${1:-}"

if [[ -z "$ORDER_ID" ]]; then
    echo "ERROR: order_id is required"
    echo "Usage: bash proxybase-rotate.sh <order_id>"
    exit 1
fi

load_credentials --required || exit 1
init_orders_file

echo "ProxyBase: Rotating proxy credentials for order $ORDER_ID..."

ROTATE_RC=0
api_call_with_retry POST "/orders/$ORDER_ID/rotate" \
    -H "Content-Type: application/json" || ROTATE_RC=$?

if [[ $ROTATE_RC -ne 0 ]]; then
    echo "ERROR: Rotation failed (HTTP $API_HTTP_CODE)"
    if validate_json "$API_RESPONSE"; then
        echo "$API_RESPONSE" | jq .
    else
        echo "$API_RESPONSE"
    fi
    exit 1
fi

# Extract new proxy credentials
HOST=$(echo "$API_RESPONSE" | jq -r '.proxy.host // "api.proxybase.xyz"')
PORT=$(echo "$API_RESPONSE" | jq -r '.proxy.port // 1080')
USERNAME=$(echo "$API_RESPONSE" | jq -r '.proxy.username // empty')
PASSWORD=$(echo "$API_RESPONSE" | jq -r '.proxy.password // empty')

if [[ -z "$USERNAME" || -z "$PASSWORD" ]]; then
    echo "ERROR: No proxy credentials in rotation response"
    echo "$API_RESPONSE" | jq .
    exit 1
fi

PROXY_URL="socks5://${USERNAME}:${PASSWORD}@${HOST}:${PORT}"

# Update orders.json — under lock
acquire_lock

if jq -e ".orders[] | select(.order_id == \"$ORDER_ID\")" "$ORDERS_FILE" > /dev/null 2>&1; then
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    UPDATED=$(jq --arg oid "$ORDER_ID" --arg proxy "$PROXY_URL" --arg ts "$TIMESTAMP" \
        '(.orders[] | select(.order_id == $oid)) |= . + {
            proxy: $proxy,
            last_rotated: $ts
        }' "$ORDERS_FILE")
    if validate_json "$UPDATED"; then
        echo "$UPDATED" > "$ORDERS_FILE"
    fi
fi

release_lock

# Write per-order proxy env file (safe for multi-proxy)
ORDER_PROXY_ENV="${STATE_DIR}/.proxy-env-${ORDER_ID}"
cat > "$ORDER_PROXY_ENV" << ENVEOF
# ProxyBase SOCKS5 proxy — Order $ORDER_ID (rotated)
# Generated $(date -u +"%Y-%m-%dT%H:%M:%SZ")
export ALL_PROXY="$PROXY_URL"
export HTTPS_PROXY="$PROXY_URL"
export HTTP_PROXY="$PROXY_URL"
export NO_PROXY="localhost,127.0.0.1,api.proxybase.xyz"
export PROXYBASE_SOCKS5="$PROXY_URL"
ENVEOF
chmod 600 "$ORDER_PROXY_ENV"
# Also update the shared .proxy-env as a convenience default
cp -f "$ORDER_PROXY_ENV" "$PROXY_ENV_FILE"

# Output
echo ""
echo "========================================"
echo "  PROXY CREDENTIALS ROTATED"
echo "========================================"
echo ""
echo "  Order ID:   $ORDER_ID"
echo "  New SOCKS5: $PROXY_URL"
echo ""
echo "  Updated: $ORDER_PROXY_ENV"
echo "           $PROXY_ENV_FILE (shared default)"
echo ""
echo "To apply new credentials:"
echo "  source $ORDER_PROXY_ENV"
echo ""
echo "========================================"
