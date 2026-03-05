#!/usr/bin/env bash
# proxybase-status.sh — Show status of all tracked ProxyBase orders
# Usage: bash proxybase-status.sh [order_id] [--cleanup]
#
# With no arguments: shows all tracked orders + refreshes from API
# With order_id:     shows detailed status for that specific order
# With --cleanup:    removes expired/failed orders from orders.json

set -euo pipefail

# Source shared library
source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

# Load credentials (not required — offline status still works)
load_credentials

# Parse args
SPECIFIC_ORDER=""
CLEANUP=false

for arg in "$@"; do
    case "$arg" in
        --cleanup) CLEANUP=true ;;
        -*) echo "Unknown flag: $arg"; exit 1 ;;
        *) SPECIFIC_ORDER="$arg" ;;
    esac
done

if [[ ! -f "$ORDERS_FILE" ]]; then
    echo "No tracked orders. Create one with:"
    echo "  bash $SCRIPT_DIR/proxybase-order.sh us_residential_1gb"
    exit 0
fi

ORDER_COUNT=$(jq '.orders | length' "$ORDERS_FILE")

if [[ "$ORDER_COUNT" -eq 0 ]]; then
    echo "No tracked orders. Create one with:"
    echo "  bash $SCRIPT_DIR/proxybase-order.sh us_residential_1gb"
    exit 0
fi

# ─── Cleanup mode ────────────────────────────────────────────────────
if [[ "$CLEANUP" == true ]]; then
    TERMINAL_STATES='["expired", "failed"]'
    BEFORE_COUNT=$ORDER_COUNT

    acquire_lock

    REMOVED=$(jq -r --argjson ts "$TERMINAL_STATES" \
        '[.orders[] | select(.status as $s | $ts | index($s) != null)] | length' "$ORDERS_FILE")

    CLEANED=$(jq --argjson ts "$TERMINAL_STATES" \
        '.orders |= [.[] | select(.status as $s | $ts | index($s) == null)]' "$ORDERS_FILE")

    if validate_json "$CLEANED"; then
        echo "$CLEANED" > "$ORDERS_FILE"
        AFTER_COUNT=$(echo "$CLEANED" | jq '.orders | length')
        echo "Cleanup: removed $REMOVED terminal order(s) (expired/failed)"
        echo "Orders: $BEFORE_COUNT → $AFTER_COUNT"
    else
        echo "ERROR: Cleanup failed — state file may be corrupt" >&2
    fi

    release_lock
    exit 0
fi

# ─── Specific order detail ───────────────────────────────────────────
if [[ -n "$SPECIFIC_ORDER" ]]; then
    if [[ -z "${PROXYBASE_API_KEY:-}" ]]; then
        echo "ERROR: PROXYBASE_API_KEY is not set — cannot fetch live status"
        echo "Run: source $SCRIPT_DIR/proxybase-register.sh"
        exit 1
    fi

    # Fetch fresh status from API with JSON validation
    STATUS_RC=0
    api_call GET "/orders/$SPECIFIC_ORDER/status" || STATUS_RC=$?
    if [[ $STATUS_RC -ne 0 ]]; then
        echo "ERROR: Failed to fetch order $SPECIFIC_ORDER (HTTP $API_HTTP_CODE)"
        if validate_json "$API_RESPONSE"; then
            echo "$API_RESPONSE" | jq .
        else
            echo "Non-JSON response from API"
        fi
        exit 1
    fi

    echo "Order: $SPECIFIC_ORDER"
    echo "$API_RESPONSE" | jq .
    exit 0
fi

# ─── All orders — show summary table ─────────────────────────────────
echo "========================================"
echo "  PROXYBASE ORDERS"
echo "========================================"
echo ""

jq -r '.orders[] | "  \(.order_id)  \(.status | if length > 18 then .[:18] else . + " " * (18 - length) end)  \(.package_id // "unknown")  \(.proxy // "—")"' "$ORDERS_FILE" 2>/dev/null

echo ""
echo "Total: $ORDER_COUNT order(s)"

# Flag timed-out orders
TIMED_OUT=$(jq '[.orders[] | select(.status == "timed_out")] | length' "$ORDERS_FILE")
if [[ "$TIMED_OUT" -gt 0 ]]; then
    echo ""
    echo "⚠️  $TIMED_OUT order(s) timed out during polling. Resume with:"
    jq -r '.orders[] | select(.status == "timed_out") | "  bash '"$SCRIPT_DIR"'/proxybase-poll.sh \(.order_id) --max-attempts 200"' "$ORDERS_FILE"
fi

echo ""

# Refresh all statuses from API if we have credentials
if [[ -n "${PROXYBASE_API_KEY:-}" ]]; then
    echo "Refreshing live status..."

    acquire_lock

    jq -r '.orders[].order_id' "$ORDERS_FILE" | while read -r OID; do
        REFRESH_RC=0
        api_call GET "/orders/$OID/status" || REFRESH_RC=$?
        if [[ $REFRESH_RC -ne 0 ]]; then
            echo "  $OID: refresh failed (HTTP $API_HTTP_CODE)" >&2
            continue
        fi

        LIVE_STATUS=$(echo "$API_RESPONSE" | jq -r '.status // empty')
        if [[ -z "$LIVE_STATUS" ]]; then
            continue
        fi

        UPDATED=$(jq --arg oid "$OID" --arg s "$LIVE_STATUS" \
            '(.orders[] | select(.order_id == $oid)).status = $s' "$ORDERS_FILE")
        if validate_json "$UPDATED"; then
            echo "$UPDATED" > "$ORDERS_FILE"
        fi

        # If proxy_active, update proxy URL
        if [[ "$LIVE_STATUS" == "proxy_active" ]]; then
            HOST=$(echo "$API_RESPONSE" | jq -r '.proxy.host // "api.proxybase.xyz"')
            PORT=$(echo "$API_RESPONSE" | jq -r '.proxy.port // 1080')
            USER=$(echo "$API_RESPONSE" | jq -r '.proxy.username // empty')
            PASS=$(echo "$API_RESPONSE" | jq -r '.proxy.password // empty')
            if [[ -n "$USER" && -n "$PASS" ]]; then
                PROXY_URL="socks5://${USER}:${PASS}@${HOST}:${PORT}"
                UPDATED=$(jq --arg oid "$OID" --arg p "$PROXY_URL" \
                    '(.orders[] | select(.order_id == $oid)).proxy = $p' "$ORDERS_FILE")
                if validate_json "$UPDATED"; then
                    echo "$UPDATED" > "$ORDERS_FILE"
                fi
            fi
        fi
    done

    release_lock

    echo ""
    echo "Updated status:"
    echo ""
    jq -r '.orders[] | "  \(.order_id)  \(.status)  \(.proxy // "—")"' "$ORDERS_FILE"
    echo ""
fi

# Show active proxies
ACTIVE_COUNT=$(jq '[.orders[] | select(.status == "proxy_active")] | length' "$ORDERS_FILE")
if [[ "$ACTIVE_COUNT" -gt 0 ]]; then
    echo "Active proxies ($ACTIVE_COUNT):"
    jq -r '.orders[] | select(.status == "proxy_active") | "  \(.order_id): \(.proxy)"' "$ORDERS_FILE"
    echo ""
    echo "Use proxy:"
    echo "  source $PROXY_ENV_FILE"
    echo "  curl https://httpbin.org/ip"
fi
