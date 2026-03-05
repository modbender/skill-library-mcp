#!/usr/bin/env bash
# proxybase-poll.sh — Poll a ProxyBase order until terminal state
# Usage: bash proxybase-poll.sh <order_id> [--once] [--quiet] [--max-attempts N]
#
# Modes:
#   Default:   Poll every 30s until proxy_active/expired/failed (max 100 attempts = ~50 min)
#   --once:    Single status check (for cron jobs or manual checks)
#   --quiet:   Only output on state changes (for cron: reply NO_REPLY if pending)
#   --max-attempts N:  Override the default 100 attempts (e.g. 200 for BTC)
#
# Exit codes:
#   0 — proxy_active (credentials in stdout)
#   1 — error (network, auth, bad order)
#   2 — expired or failed
#   3 — still pending (with --once)

set -euo pipefail

# Source shared library
source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

# Parse args
ORDER_ID=""
ONCE=false
QUIET=false
MAX_ATTEMPTS=100  # 100 * 30s = ~50 minutes

for arg in "$@"; do
    case "$arg" in
        --once) ONCE=true ;;
        --quiet) QUIET=true ;;
        --max-attempts)
            # next arg is the value — handled below
            ;;
        --max-attempts=*)
            MAX_ATTEMPTS="${arg#*=}"
            ;;
        -*)
            echo "Unknown flag: $arg"; exit 1
            ;;
        *)
            # Could be the value for --max-attempts or the order_id
            ORDER_ID="$arg"
            ;;
    esac
done

# Handle --max-attempts N (positional value after flag)
ARGS=("$@")
for i in "${!ARGS[@]}"; do
    if [[ "${ARGS[$i]}" == "--max-attempts" ]] && [[ -n "${ARGS[$((i+1))]:-}" ]]; then
        MAX_ATTEMPTS="${ARGS[$((i+1))]}"
        # If the "order_id" we captured was actually the max-attempts value, re-find order_id
        if [[ "$ORDER_ID" == "$MAX_ATTEMPTS" ]]; then
            ORDER_ID=""
            for a in "$@"; do
                case "$a" in
                    --*) continue ;;
                    "$MAX_ATTEMPTS") continue ;;
                    *) ORDER_ID="$a"; break ;;
                esac
            done
        fi
    fi
done

if [[ -z "$ORDER_ID" ]]; then
    echo "ERROR: order_id is required"
    echo "Usage: bash proxybase-poll.sh <order_id> [--once] [--quiet] [--max-attempts N]"
    exit 1
fi

load_credentials --required || exit 1
init_orders_file

# Function: check status once
check_status() {
    local RC=0
    api_call GET "/orders/$ORDER_ID/status" || RC=$?

    if [[ $RC -ne 0 ]]; then
        if ! validate_json "$API_RESPONSE"; then
            echo "ERROR: API returned non-JSON (HTTP $API_HTTP_CODE) for order $ORDER_ID"
            return 1
        fi
        # HTTP error but valid JSON — check if it's a real error
        local ERR_MSG
        ERR_MSG=$(echo "$API_RESPONSE" | jq -r '.message // .error // "unknown error"')
        echo "ERROR: API error (HTTP $API_HTTP_CODE): $ERR_MSG"
        return 1
    fi

    # Extract status
    local STATUS
    STATUS=$(echo "$API_RESPONSE" | jq -r '.status // empty')

    if [[ -z "$STATUS" ]]; then
        echo "ERROR: No status field in API response"
        echo "$API_RESPONSE" | jq . 2>/dev/null
        return 1
    fi

    # Update orders.json with current status — under lock
    acquire_lock
    if jq -e ".orders[] | select(.order_id == \"$ORDER_ID\")" "$ORDERS_FILE" > /dev/null 2>&1; then
        local UPDATED
        UPDATED=$(jq --arg oid "$ORDER_ID" --arg s "$STATUS" \
            '(.orders[] | select(.order_id == $oid)).status = $s' "$ORDERS_FILE")
        if validate_json "$UPDATED"; then
            echo "$UPDATED" > "$ORDERS_FILE"
        fi
    fi
    release_lock

    case "$STATUS" in
        proxy_active)
            # Extract proxy credentials
            local HOST PORT USERNAME PASSWORD BW_USED BW_TOTAL
            HOST=$(echo "$API_RESPONSE" | jq -r '.proxy.host // "api.proxybase.xyz"')
            PORT=$(echo "$API_RESPONSE" | jq -r '.proxy.port // 1080')
            USERNAME=$(echo "$API_RESPONSE" | jq -r '.proxy.username // empty')
            PASSWORD=$(echo "$API_RESPONSE" | jq -r '.proxy.password // empty')
            BW_USED=$(echo "$API_RESPONSE" | jq -r '.bandwidth_used // .used_bytes // 0')
            BW_TOTAL=$(echo "$API_RESPONSE" | jq -r '.bandwidth_total // .bandwidth_bytes // 0')

            # Update orders.json with proxy info — under lock
            local PROXY_URL="socks5://${USERNAME}:${PASSWORD}@${HOST}:${PORT}"
            acquire_lock
            local PROXY_UPDATED
            PROXY_UPDATED=$(jq --arg oid "$ORDER_ID" --arg proxy "$PROXY_URL" \
                '(.orders[] | select(.order_id == $oid)).proxy = $proxy' "$ORDERS_FILE")
            if validate_json "$PROXY_UPDATED"; then
                echo "$PROXY_UPDATED" > "$ORDERS_FILE"
            fi
            release_lock

            # Write per-order proxy env file (safe for multi-proxy)
            local ORDER_PROXY_ENV="${STATE_DIR}/.proxy-env-${ORDER_ID}"
            cat > "$ORDER_PROXY_ENV" << ENVEOF
# ProxyBase SOCKS5 proxy — Order $ORDER_ID
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

            # Format bandwidth
            local BW_USED_MB BW_TOTAL_MB BW_PCT
            BW_USED_MB=$(echo "scale=1; $BW_USED / 1048576" | bc 2>/dev/null || echo "0")
            BW_TOTAL_MB=$(echo "scale=1; $BW_TOTAL / 1048576" | bc 2>/dev/null || echo "0")
            if [[ "$BW_TOTAL" -gt 0 ]] 2>/dev/null; then
                BW_PCT=$(echo "scale=1; $BW_USED * 100 / $BW_TOTAL" | bc 2>/dev/null || echo "0")
            else
                BW_PCT="0"
            fi

            echo ""
            echo "✅ PROXY ACTIVE — Order $ORDER_ID"
            echo ""
            echo "SOCKS5: $PROXY_URL"
            echo ""
            echo "Usage with curl:"
            echo "  curl --proxy $PROXY_URL https://example.com"
            echo ""
            echo "Or set ENV (auto-routes all traffic):"
            echo "  source $ORDER_PROXY_ENV"
            echo "  # or: source $PROXY_ENV_FILE  (always points to most recent)"
            echo ""
            echo "Bandwidth: ${BW_USED_MB}MB / ${BW_TOTAL_MB}MB (${BW_PCT}%)"

            return 0
            ;;

        payment_pending|confirming|paid)
            if [[ "$QUIET" == true ]]; then
                echo "NO_REPLY"
            else
                echo "Order $ORDER_ID: $STATUS"
                if [[ "$STATUS" == "confirming" ]]; then
                    echo "  Payment detected — waiting for blockchain confirmation..."
                elif [[ "$STATUS" == "paid" ]]; then
                    echo "  Payment confirmed — proxy being provisioned..."
                else
                    echo "  Waiting for payment..."
                fi
            fi
            return 3
            ;;

        expired)
            echo ""
            echo "⚠️ Order $ORDER_ID has EXPIRED"
            echo "No payment was received within the payment window."
            echo "Create a new order to try again."
            return 2
            ;;

        failed)
            echo ""
            echo "❌ Order $ORDER_ID has FAILED"
            echo "Payment processing encountered an error."
            echo "Create a new order to try again."
            return 2
            ;;

        bandwidth_exhausted)
            echo ""
            echo "📊 Order $ORDER_ID — BANDWIDTH EXHAUSTED"
            echo "All bandwidth has been consumed."
            echo "Top up to reactivate (same credentials):"
            echo "  bash $SCRIPT_DIR/proxybase-topup.sh $ORDER_ID us_residential_1gb"
            return 2
            ;;

        partially_paid)
            # ALWAYS print — this is actionable even in --quiet mode
            local PAID_AMT EXPECTED_AMT
            PAID_AMT=$(echo "$API_RESPONSE" | jq -r '.actually_paid // "unknown"')
            EXPECTED_AMT=$(echo "$API_RESPONSE" | jq -r '.pay_amount // "unknown"')
            echo ""
            echo "⚠️ Order $ORDER_ID — PARTIALLY PAID"
            echo "  Received: $PAID_AMT"
            echo "  Expected: $EXPECTED_AMT"
            echo "  Send the remaining amount to complete the payment."
            return 3
            ;;

        *)
            echo "Order $ORDER_ID: Unknown status '$STATUS'"
            echo "$API_RESPONSE" | jq . 2>/dev/null
            return 1
            ;;
    esac
}

# Single check mode
if [[ "$ONCE" == true ]]; then
    EXIT_CODE=0
    check_status || EXIT_CODE=$?
    exit $EXIT_CODE
fi

# Polling loop
ATTEMPT=0

echo "ProxyBase: Polling order $ORDER_ID every 30s (max ${MAX_ATTEMPTS} attempts)..."

while [[ $ATTEMPT -lt $MAX_ATTEMPTS ]]; do
    ATTEMPT=$((ATTEMPT + 1))

    if ! $QUIET; then
        echo "[$(date +%H:%M:%S)] Poll attempt $ATTEMPT/$MAX_ATTEMPTS..."
    fi

    EXIT_CODE=0
    check_status || EXIT_CODE=$?

    case $EXIT_CODE in
        0) exit 0 ;;  # proxy_active
        2) exit 2 ;;  # expired/failed/exhausted
        3) ;;         # still pending — continue polling
        *) ;;         # error — continue polling (transient)
    esac

    if [[ $ATTEMPT -lt $MAX_ATTEMPTS ]]; then
        sleep 30
    fi
done

# Timed out — record timed_out state so status.sh can flag it
acquire_lock
if jq -e ".orders[] | select(.order_id == \"$ORDER_ID\")" "$ORDERS_FILE" > /dev/null 2>&1; then
    UPDATED=$(jq --arg oid "$ORDER_ID" \
        '(.orders[] | select(.order_id == $oid)).status = "timed_out"' "$ORDERS_FILE")
    if validate_json "$UPDATED"; then
        echo "$UPDATED" > "$ORDERS_FILE"
    fi
fi
release_lock

echo ""
echo "⏰ TIMEOUT — Order $ORDER_ID"
echo "Polling stopped after $MAX_ATTEMPTS attempts (~$((MAX_ATTEMPTS * 30 / 60)) minutes)."
echo "The order may still be pending on the blockchain."
echo ""
echo "Resume polling (e.g. for slow BTC confirmations):"
echo "  bash $SCRIPT_DIR/proxybase-poll.sh $ORDER_ID --max-attempts 200"
echo ""
echo "Or check once:"
echo "  bash $SCRIPT_DIR/proxybase-poll.sh $ORDER_ID --once"
exit 3
