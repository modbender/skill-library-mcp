#!/usr/bin/env bash
# proxybase.sh — Unified ProxyBase skill CLI
# All-in-one script: register, order, poll, status, topup, rotate, inject-gateway
#
# Usage:
#   bash proxybase.sh <command> [args...]
#   source proxybase.sh register          (must source for register to export vars)
#
# Commands:
#   register                          Register agent + store API key
#   order <pkg> [currency] [cb_url]   Create a proxy order
#   poll <order_id> [--once] [--quiet] [--max-attempts N]
#   status [order_id] [--cleanup]     Show order status
#   topup <order_id> <pkg> [currency] Top up bandwidth
#   rotate <order_id>                 Rotate proxy credentials
#   inject-gateway <order_id>         Inject proxy into OpenClaw systemd service
#   help                              Show this help

set -euo pipefail

# ═════════════════════════════════════════════════════════════════════
# COMMON LIBRARY
# ═════════════════════════════════════════════════════════════════════

# ─── Path setup ──────────────────────────────────────────────────────
if [[ -z "${_PROXYBASE_COMMON_LOADED:-}" ]]; then
    _PROXYBASE_COMMON_LOADED=1

    # Resolve SKILL_DIR from where this script lives
    if [[ -n "${BASH_SOURCE[0]:-}" ]]; then
        SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    else
        SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
    fi
    SCRIPT_DIR="$SKILL_DIR"
    STATE_DIR="$SKILL_DIR/state"
    ORDERS_FILE="$STATE_DIR/orders.json"
    CREDS_FILE="$STATE_DIR/credentials.env"
    PROXY_ENV_FILE="$STATE_DIR/.proxy-env"
    LOCK_FILE="$STATE_DIR/orders.lock"

    PROXYBASE_API_URL="${PROXYBASE_API_URL:-https://api.proxybase.xyz/v1}"

    mkdir -p "$STATE_DIR"
fi

# ─── Input validation & sanitization ─────────────────────────────────
# Validates values from API responses contain only safe characters,
# preventing shell injection if the upstream API is compromised.
validate_safe_string() {
    local VALUE="$1"
    local CONTEXT="$2"  # username, password, host, port, order_id, api_key, package_id, proxy_url

    if [[ -z "$VALUE" ]]; then
        return 1
    fi

    case "$CONTEXT" in
        username)
            [[ "$VALUE" =~ ^[a-zA-Z0-9._-]+$ ]] || { echo "SECURITY: Invalid characters in proxy username — rejecting" >&2; return 1; }
            ;;
        password)
            [[ "$VALUE" =~ ^[a-zA-Z0-9._!*+-]+$ ]] || { echo "SECURITY: Invalid characters in proxy password — rejecting" >&2; return 1; }
            ;;
        host)
            [[ "$VALUE" =~ ^[a-zA-Z0-9.-]+$ ]] || { echo "SECURITY: Invalid characters in proxy host — rejecting" >&2; return 1; }
            ;;
        port)
            [[ "$VALUE" =~ ^[0-9]+$ ]] && [[ "$VALUE" -ge 1 && "$VALUE" -le 65535 ]] || { echo "SECURITY: Invalid proxy port — rejecting" >&2; return 1; }
            ;;
        order_id)
            [[ "$VALUE" =~ ^[a-zA-Z0-9_-]+$ ]] || { echo "SECURITY: Invalid characters in order_id — rejecting" >&2; return 1; }
            ;;
        api_key)
            [[ "$VALUE" =~ ^[a-zA-Z0-9_-]+$ ]] || { echo "SECURITY: Invalid characters in API key — rejecting" >&2; return 1; }
            ;;
        package_id)
            [[ "$VALUE" =~ ^[a-zA-Z0-9_-]+$ ]] || { echo "SECURITY: Invalid characters in package_id — rejecting" >&2; return 1; }
            ;;
        proxy_url)
            [[ "$VALUE" =~ ^socks5://[a-zA-Z0-9._-]+:[a-zA-Z0-9._!*+-]+@[a-zA-Z0-9.-]+:[0-9]+$ ]] || { echo "SECURITY: Invalid proxy URL format — rejecting" >&2; return 1; }
            ;;
        *)
            if [[ "$VALUE" =~ [\$\`\"\'\'\;\&\|\>\<\(\)\{\}\\] ]]; then
                echo "SECURITY: Unsafe characters detected in $CONTEXT — rejecting" >&2
                return 1
            fi
            ;;
    esac
    return 0
}

build_safe_proxy_url() {
    local _HOST="$1" _PORT="$2" _USER="$3" _PASS="$4"
    validate_safe_string "$_HOST" "host" || return 1
    validate_safe_string "$_PORT" "port" || return 1
    validate_safe_string "$_USER" "username" || return 1
    validate_safe_string "$_PASS" "password" || return 1
    PROXY_URL="socks5://${_USER}:${_PASS}@${_HOST}:${_PORT}"
    return 0
}

write_proxy_env_file() {
    local _FILE="$1" _OID="$2" _URL="$3" _LABEL="${4:-}"
    validate_safe_string "$_URL" "proxy_url" || return 1
    {
        printf '# ProxyBase SOCKS5 proxy — Order %s%s\n' "$_OID" "${_LABEL:+ ($_LABEL)}"
        printf '# Generated %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
        printf "export ALL_PROXY='%s'\n" "$_URL"
        printf "export HTTPS_PROXY='%s'\n" "$_URL"
        printf "export HTTP_PROXY='%s'\n" "$_URL"
        printf "export NO_PROXY='localhost,127.0.0.1,api.proxybase.xyz'\n"
        printf "export PROXYBASE_SOCKS5='%s'\n" "$_URL"
    } > "$_FILE"
    chmod 600 "$_FILE"
}

write_credentials_file() {
    local _FILE="$1" _KEY="$2" _URL="$3" _AGENT_ID="${4:-unknown}"
    validate_safe_string "$_KEY" "api_key" || return 1
    {
        printf '# ProxyBase credentials — generated %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
        printf '# Agent ID: %s\n' "$_AGENT_ID"
        printf "export PROXYBASE_API_KEY='%s'\n" "$_KEY"
        printf "export PROXYBASE_API_URL='%s'\n" "$_URL"
    } > "$_FILE"
    chmod 600 "$_FILE"
}

# ─── File locking ────────────────────────────────────────────────────
_LOCK_FD=""
_LOCK_METHOD=""

acquire_lock() {
    if command -v flock &>/dev/null; then
        _LOCK_METHOD="flock"
        exec 9>"$LOCK_FILE"
        if ! flock -n 9 2>/dev/null; then
            echo "ProxyBase: Waiting for state lock..." >&2
            flock 9
        fi
        _LOCK_FD=9
    else
        _LOCK_METHOD="mkdir"
        local LOCK_DIR="${LOCK_FILE}.d"
        local ATTEMPTS=0
        while ! mkdir "$LOCK_DIR" 2>/dev/null; do
            if [[ -d "$LOCK_DIR" ]]; then
                local LOCK_AGE=0
                if command -v stat &>/dev/null; then
                    if stat -f%m "$LOCK_DIR" &>/dev/null; then
                        LOCK_AGE=$(( $(date +%s) - $(stat -f%m "$LOCK_DIR") ))
                    elif stat -c%Y "$LOCK_DIR" &>/dev/null; then
                        LOCK_AGE=$(( $(date +%s) - $(stat -c%Y "$LOCK_DIR") ))
                    fi
                fi
                if [[ $LOCK_AGE -gt 120 ]]; then
                    echo "ProxyBase: Removing stale lock (age=${LOCK_AGE}s)" >&2
                    rm -rf "$LOCK_DIR" 2>/dev/null
                    continue
                fi
            fi

            ATTEMPTS=$((ATTEMPTS + 1))
            if [[ $ATTEMPTS -ge 60 ]]; then
                echo "ERROR: Could not acquire state lock after 30s — stale lock?" >&2
                echo "  Remove manually: rm -rf $LOCK_DIR" >&2
                return 1
            fi
            if [[ $ATTEMPTS -eq 1 ]]; then
                echo "ProxyBase: Waiting for state lock..." >&2
            fi
            sleep 0.5
        done
    fi
}

release_lock() {
    if [[ "$_LOCK_METHOD" == "flock" && -n "$_LOCK_FD" ]]; then
        flock -u 9 2>/dev/null || true
        exec 9>&- 2>/dev/null || true
        rm -f "$LOCK_FILE" 2>/dev/null
    elif [[ "$_LOCK_METHOD" == "mkdir" ]]; then
        rm -rf "${LOCK_FILE}.d" 2>/dev/null
    fi
    _LOCK_FD=""
    _LOCK_METHOD=""
}

trap 'release_lock' EXIT

# ─── JSON validation ─────────────────────────────────────────────────
validate_json() {
    local data="$1"
    if [[ -z "$data" ]]; then
        return 1
    fi
    echo "$data" | jq empty >/dev/null 2>&1
}

# ─── Safe API call ───────────────────────────────────────────────────
api_call() {
    local METHOD="$1"
    shift
    local PATH_="$1"
    shift

    local TMPFILE
    TMPFILE=$(mktemp)

    local _PREV_TRAP
    _PREV_TRAP=$(trap -p EXIT | sed "s/^trap -- '//;s/' EXIT$//")
    trap "rm -f '$TMPFILE'; ${_PREV_TRAP:-release_lock}" EXIT

    API_HTTP_CODE=$(curl -s -o "$TMPFILE" -w "%{http_code}" \
        -X "$METHOD" \
        "${PROXYBASE_API_URL}${PATH_}" \
        -H "X-API-Key: ${PROXYBASE_API_KEY:-}" \
        --connect-timeout 10 \
        --max-time 20 \
        "$@" 2>/dev/null) || {
        rm -f "$TMPFILE"
        trap "${_PREV_TRAP:-release_lock}" EXIT
        API_RESPONSE='{"error":"network_error","message":"curl failed"}'
        API_HTTP_CODE="000"
        return 1
    }

    API_RESPONSE=$(cat "$TMPFILE")
    rm -f "$TMPFILE"

    trap "${_PREV_TRAP:-release_lock}" EXIT

    if ! validate_json "$API_RESPONSE"; then
        local SNIPPET="${API_RESPONSE:0:200}"
        API_RESPONSE=$(jq -n --arg code "$API_HTTP_CODE" --arg body "$SNIPPET" \
            '{"error":"invalid_json","message":"API returned non-JSON response","http_code":$code,"body_preview":$body}')
        return 1
    fi

    case "$API_HTTP_CODE" in
        2*) return 0 ;;
        429) return 2 ;;
        *) return 2 ;;
    esac
}

# ─── Retry wrapper ───────────────────────────────────────────────────
api_call_with_retry() {
    local DELAYS=(2 5 10)
    local ATTEMPT=0

    while [[ $ATTEMPT -le 3 ]]; do
        local RC=0
        api_call "$@" || RC=$?

        if [[ $RC -eq 0 ]]; then
            return 0
        fi

        if [[ "$API_HTTP_CODE" =~ ^4[0-9][0-9]$ && "$API_HTTP_CODE" != "429" ]]; then
            return $RC
        fi

        if [[ $ATTEMPT -ge 3 ]]; then
            return $RC
        fi

        local WAIT=${DELAYS[$ATTEMPT]:-10}
        if [[ "$API_HTTP_CODE" == "429" ]]; then
            local RA
            RA=$(echo "$API_RESPONSE" | jq -r '.retry_after // empty' 2>/dev/null)
            if [[ -n "$RA" && "$RA" =~ ^[0-9]+$ ]]; then
                WAIT=$RA
            fi
        fi

        echo "ProxyBase: Request failed (HTTP $API_HTTP_CODE), retrying in ${WAIT}s... (attempt $((ATTEMPT+1))/3)" >&2
        sleep "$WAIT"
        ATTEMPT=$((ATTEMPT + 1))
    done

    return 1
}

# ─── Credentials loading ─────────────────────────────────────────────
load_credentials() {
    local REQUIRED=false
    [[ "${1:-}" == "--required" ]] && REQUIRED=true

    if [[ -z "${PROXYBASE_API_KEY:-}" ]]; then
        if [[ -f "$CREDS_FILE" ]]; then
            source "$CREDS_FILE"
        fi
    fi

    if [[ "$REQUIRED" == true && -z "${PROXYBASE_API_KEY:-}" ]]; then
        echo "ProxyBase: No API key found. Attempting auto-registration..." >&2
        cmd_register || {
            echo "ERROR: Auto-registration failed." >&2
            return 1
        }
        if [[ -z "${PROXYBASE_API_KEY:-}" ]]; then
            echo "ERROR: Auto-registration completed but PROXYBASE_API_KEY is still not set." >&2
            return 1
        fi
    fi
}

# ─── Orders file helpers ─────────────────────────────────────────────
init_orders_file() {
    if [[ ! -f "$ORDERS_FILE" ]]; then
        echo '{"orders":[]}' > "$ORDERS_FILE"
    fi
}

update_order_field() {
    local OID="$1" FIELD="$2" VALUE="$3"

    if [[ ! -f "$ORDERS_FILE" ]]; then
        return 1
    fi

    local UPDATED
    UPDATED=$(jq --arg oid "$OID" --arg f "$FIELD" --arg v "$VALUE" \
        '(.orders[] | select(.order_id == $oid))[$f] = $v' "$ORDERS_FILE" 2>/dev/null)

    if [[ -n "$UPDATED" ]] && validate_json "$UPDATED"; then
        echo "$UPDATED" > "$ORDERS_FILE"
    else
        echo "WARN: Failed to update order $OID field $FIELD — state file may be corrupt" >&2
    fi
}


# ═════════════════════════════════════════════════════════════════════
# COMMANDS
# ═════════════════════════════════════════════════════════════════════

# ─── register ─────────────────────────────────────────────────────────
cmd_register() {
    # Check if we already have credentials
    if [[ -f "$CREDS_FILE" ]]; then
        source "$CREDS_FILE"
        if [[ -n "${PROXYBASE_API_KEY:-}" ]]; then
            local_rc=0
            api_call_with_retry GET "/packages" || local_rc=$?
            if [[ $local_rc -eq 0 ]]; then
                echo "ProxyBase: Credentials loaded (key: ${PROXYBASE_API_KEY:0:8}...)"
                export PROXYBASE_API_KEY
                export PROXYBASE_API_URL
                return 0
            else
                if [[ "$API_HTTP_CODE" == "401" || "$API_HTTP_CODE" == "403" ]]; then
                    echo "ProxyBase: Stored key is invalid (HTTP $API_HTTP_CODE) — re-registering..."
                    unset PROXYBASE_API_KEY
                else
                    echo "ProxyBase: API unreachable (HTTP $API_HTTP_CODE) — keeping existing key."
                    echo "ProxyBase: The API may be temporarily down. Retry later." >&2
                    export PROXYBASE_API_KEY
                    export PROXYBASE_API_URL
                    return 0
                fi
            fi
        fi
    fi

    echo "ProxyBase: Registering new agent..."

    local_rc=0
    api_call_with_retry POST "/agents" -H "Content-Type: application/json" || local_rc=$?
    if [[ $local_rc -ne 0 ]]; then
        echo "ProxyBase: ERROR — Registration failed (HTTP $API_HTTP_CODE)"
        if validate_json "$API_RESPONSE"; then
            echo "$API_RESPONSE" | jq .
        else
            echo "$API_RESPONSE"
        fi
        return 1
    fi

    if ! echo "$API_RESPONSE" | jq -e '.api_key' > /dev/null 2>&1; then
        echo "ProxyBase: ERROR — No api_key in registration response:"
        echo "$API_RESPONSE" | jq .
        return 1
    fi

    local API_KEY AGENT_ID
    API_KEY=$(echo "$API_RESPONSE" | jq -r '.api_key')
    AGENT_ID=$(echo "$API_RESPONSE" | jq -r '.agent_id // .id // "unknown"')

    if [[ -z "$API_KEY" || "$API_KEY" == "null" ]]; then
        echo "ProxyBase: ERROR — api_key field is empty/null"
        echo "$API_RESPONSE" | jq .
        return 1
    fi

    # Validate API key contains only safe characters (prevent injection via credentials.env)
    if ! validate_safe_string "$API_KEY" "api_key"; then
        echo "ProxyBase: ERROR — API key contains invalid characters (possible API compromise)"
        return 1
    fi

    write_credentials_file "$CREDS_FILE" "$API_KEY" "$PROXYBASE_API_URL" "$AGENT_ID"

    export PROXYBASE_API_KEY="$API_KEY"
    export PROXYBASE_API_URL

    echo "ProxyBase: Registered successfully"
    echo "  Agent ID: $AGENT_ID"
    echo "  API Key:  ${API_KEY:0:8}..."
    echo "  Stored:   $CREDS_FILE"
}

# ─── order ────────────────────────────────────────────────────────────
cmd_order() {
    local PACKAGE_ID="${1:-}"
    local PAY_CURRENCY="${2:-usdcsol}"
    local CALLBACK_URL="${3:-}"

    if [[ -z "$PACKAGE_ID" ]]; then
        echo "ERROR: package_id is required"
        echo "Usage: bash proxybase.sh order <package_id> [pay_currency] [callback_url]"
        echo ""
        echo "Available packages: us_residential_1gb, us_residential_5gb, us_residential_10gb"
        exit 1
    fi

    # Validate input to prevent injection
    validate_safe_string "$PACKAGE_ID" "package_id" || { echo "ERROR: package_id contains invalid characters"; exit 1; }

    load_credentials --required || exit 1
    init_orders_file

    local REQUEST_BODY
    REQUEST_BODY=$(jq -n \
        --arg pkg "$PACKAGE_ID" \
        --arg cur "$PAY_CURRENCY" \
        --arg cb "$CALLBACK_URL" \
        '{package_id: $pkg, pay_currency: $cur} + (if $cb != "" then {callback_url: $cb} else {} end)')

    echo "ProxyBase: Creating order (package=$PACKAGE_ID, currency=$PAY_CURRENCY)..."

    local ORDER_RC=0
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

    local ORDER_ID
    ORDER_ID=$(echo "$API_RESPONSE" | jq -r '.order_id // empty')

    if [[ -z "$ORDER_ID" || "$ORDER_ID" == "null" ]]; then
        echo "ERROR: No order_id in API response"
        echo "$API_RESPONSE" | jq .
        exit 1
    fi

    # Validate order_id from API response
    validate_safe_string "$ORDER_ID" "order_id" || { echo "ERROR: API returned order_id with invalid characters"; exit 1; }

    local PAY_ADDRESS PAY_AMOUNT RESP_CURRENCY PRICE_USD EXPIRATION STATUS
    PAY_ADDRESS=$(echo "$API_RESPONSE" | jq -r '.pay_address // "unknown"')
    PAY_AMOUNT=$(echo "$API_RESPONSE" | jq -r '.pay_amount // "unknown"')
    RESP_CURRENCY=$(echo "$API_RESPONSE" | jq -r '.pay_currency // "unknown"')
    PRICE_USD=$(echo "$API_RESPONSE" | jq -r '.price_usd // "unknown"')
    EXPIRATION=$(echo "$API_RESPONSE" | jq -r '.expiration_estimate_date // "~24 hours"')
    STATUS=$(echo "$API_RESPONSE" | jq -r '.status // "payment_pending"')

    local TIMESTAMP
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    acquire_lock

    local UPDATED_ORDERS
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
    echo "To poll status: bash $SKILL_DIR/proxybase.sh poll $ORDER_ID"
    echo ""

    echo "RAW_JSON:"
    echo "$API_RESPONSE" | jq .

    echo ""
    echo "PROXYBASE_ORDER_ID=$ORDER_ID"
}

# ─── poll ─────────────────────────────────────────────────────────────
cmd_poll() {
    local ORDER_ID=""
    local ONCE=false
    local QUIET=false
    local MAX_ATTEMPTS=100

    for arg in "$@"; do
        case "$arg" in
            --once) ONCE=true ;;
            --quiet) QUIET=true ;;
            --max-attempts) ;;
            --max-attempts=*) MAX_ATTEMPTS="${arg#*=}" ;;
            -*) echo "Unknown flag: $arg"; exit 1 ;;
            *) ORDER_ID="$arg" ;;
        esac
    done

    local ARGS=("$@")
    for i in "${!ARGS[@]}"; do
        if [[ "${ARGS[$i]}" == "--max-attempts" ]] && [[ -n "${ARGS[$((i+1))]:-}" ]]; then
            MAX_ATTEMPTS="${ARGS[$((i+1))]}"
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
        echo "Usage: bash proxybase.sh poll <order_id> [--once] [--quiet] [--max-attempts N]"
        exit 1
    fi

    # Validate order_id to prevent injection
    validate_safe_string "$ORDER_ID" "order_id" || { echo "ERROR: order_id contains invalid characters"; exit 1; }

    load_credentials --required || exit 1
    init_orders_file

    # Function: check status once
    _poll_check_status() {
        local RC=0
        api_call GET "/orders/$ORDER_ID/status" || RC=$?

        if [[ $RC -ne 0 ]]; then
            if ! validate_json "$API_RESPONSE"; then
                echo "ERROR: API returned non-JSON (HTTP $API_HTTP_CODE) for order $ORDER_ID"
                return 1
            fi
            local ERR_MSG
            ERR_MSG=$(echo "$API_RESPONSE" | jq -r '.message // .error // "unknown error"')
            echo "ERROR: API error (HTTP $API_HTTP_CODE): $ERR_MSG"
            return 1
        fi

        local STATUS
        STATUS=$(echo "$API_RESPONSE" | jq -r '.status // empty')

        if [[ -z "$STATUS" ]]; then
            echo "ERROR: No status field in API response"
            echo "$API_RESPONSE" | jq . 2>/dev/null
            return 1
        fi

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
                local HOST PORT USERNAME PASSWORD BW_USED BW_TOTAL
                HOST=$(echo "$API_RESPONSE" | jq -r '.proxy.host // "api.proxybase.xyz"')
                PORT=$(echo "$API_RESPONSE" | jq -r '.proxy.port // 1080')
                USERNAME=$(echo "$API_RESPONSE" | jq -r '.proxy.username // empty')
                PASSWORD=$(echo "$API_RESPONSE" | jq -r '.proxy.password // empty')
                BW_USED=$(echo "$API_RESPONSE" | jq -r '.bandwidth_used // .used_bytes // 0')
                BW_TOTAL=$(echo "$API_RESPONSE" | jq -r '.bandwidth_total // .bandwidth_bytes // 0')

                # Validate proxy credentials from API response (prevents shell injection)
                if ! build_safe_proxy_url "$HOST" "$PORT" "$USERNAME" "$PASSWORD"; then
                    echo "ERROR: API returned proxy credentials with invalid characters (possible compromise)" >&2
                    return 1
                fi
                # PROXY_URL is now set by build_safe_proxy_url
                acquire_lock
                local PROXY_UPDATED
                PROXY_UPDATED=$(jq --arg oid "$ORDER_ID" --arg proxy "$PROXY_URL" \
                    '(.orders[] | select(.order_id == $oid)).proxy = $proxy' "$ORDERS_FILE")
                if validate_json "$PROXY_UPDATED"; then
                    echo "$PROXY_UPDATED" > "$ORDERS_FILE"
                fi
                release_lock

                local ORDER_PROXY_ENV="${STATE_DIR}/.proxy-env-${ORDER_ID}"
                write_proxy_env_file "$ORDER_PROXY_ENV" "$ORDER_ID" "$PROXY_URL" || {
                    echo "ERROR: Failed to write proxy env file" >&2
                    return 1
                }
                cp -f "$ORDER_PROXY_ENV" "$PROXY_ENV_FILE"

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
                echo "  bash $SKILL_DIR/proxybase.sh topup $ORDER_ID us_residential_1gb"
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
        local EXIT_CODE=0
        _poll_check_status || EXIT_CODE=$?
        exit $EXIT_CODE
    fi

    # Polling loop
    local ATTEMPT=0

    echo "ProxyBase: Polling order $ORDER_ID every 30s (max ${MAX_ATTEMPTS} attempts)..."

    while [[ $ATTEMPT -lt $MAX_ATTEMPTS ]]; do
        ATTEMPT=$((ATTEMPT + 1))

        if ! $QUIET; then
            echo "[$(date +%H:%M:%S)] Poll attempt $ATTEMPT/$MAX_ATTEMPTS..."
        fi

        local EXIT_CODE=0
        _poll_check_status || EXIT_CODE=$?

        case $EXIT_CODE in
            0) exit 0 ;;
            2) exit 2 ;;
            3) ;;
            *) ;;
        esac

        if [[ $ATTEMPT -lt $MAX_ATTEMPTS ]]; then
            sleep 30
        fi
    done

    # Timed out
    acquire_lock
    if jq -e ".orders[] | select(.order_id == \"$ORDER_ID\")" "$ORDERS_FILE" > /dev/null 2>&1; then
        local UPDATED
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
    echo "  bash $SKILL_DIR/proxybase.sh poll $ORDER_ID --max-attempts 200"
    echo ""
    echo "Or check once:"
    echo "  bash $SKILL_DIR/proxybase.sh poll $ORDER_ID --once"
    exit 3
}

# ─── status ───────────────────────────────────────────────────────────
cmd_status() {
    load_credentials

    local SPECIFIC_ORDER=""
    local CLEANUP=false

    for arg in "$@"; do
        case "$arg" in
            --cleanup) CLEANUP=true ;;
            -*) echo "Unknown flag: $arg"; exit 1 ;;
            *) SPECIFIC_ORDER="$arg" ;;
        esac
    done

    # Validate order_id early (before file operations)
    if [[ -n "$SPECIFIC_ORDER" ]]; then
        validate_safe_string "$SPECIFIC_ORDER" "order_id" || { echo "ERROR: order_id contains invalid characters"; exit 1; }
    fi

    if [[ ! -f "$ORDERS_FILE" ]]; then
        echo "No tracked orders. Create one with:"
        echo "  bash $SKILL_DIR/proxybase.sh order us_residential_1gb"
        exit 0
    fi

    local ORDER_COUNT
    ORDER_COUNT=$(jq '.orders | length' "$ORDERS_FILE")

    if [[ "$ORDER_COUNT" -eq 0 ]]; then
        echo "No tracked orders. Create one with:"
        echo "  bash $SKILL_DIR/proxybase.sh order us_residential_1gb"
        exit 0
    fi

    # Cleanup mode
    if [[ "$CLEANUP" == true ]]; then
        local TERMINAL_STATES='["expired", "failed"]'
        local BEFORE_COUNT=$ORDER_COUNT

        acquire_lock

        local REMOVED
        REMOVED=$(jq -r --argjson ts "$TERMINAL_STATES" \
            '[.orders[] | select(.status as $s | $ts | index($s) != null)] | length' "$ORDERS_FILE")

        local CLEANED
        CLEANED=$(jq --argjson ts "$TERMINAL_STATES" \
            '.orders |= [.[] | select(.status as $s | $ts | index($s) == null)]' "$ORDERS_FILE")

        if validate_json "$CLEANED"; then
            echo "$CLEANED" > "$ORDERS_FILE"
            local AFTER_COUNT
            AFTER_COUNT=$(echo "$CLEANED" | jq '.orders | length')
            echo "Cleanup: removed $REMOVED terminal order(s) (expired/failed)"
            echo "Orders: $BEFORE_COUNT → $AFTER_COUNT"
        else
            echo "ERROR: Cleanup failed — state file may be corrupt" >&2
        fi

        release_lock
        exit 0
    fi

    # Specific order detail
    if [[ -n "$SPECIFIC_ORDER" ]]; then
        if [[ -z "${PROXYBASE_API_KEY:-}" ]]; then
            echo "ERROR: PROXYBASE_API_KEY is not set — cannot fetch live status"
            echo "Run: bash $SKILL_DIR/proxybase.sh register"
            exit 1
        fi

        local STATUS_RC=0
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

    # All orders — show summary table
    echo "========================================"
    echo "  PROXYBASE ORDERS"
    echo "========================================"
    echo ""

    jq -r '.orders[] | "  \(.order_id)  \(.status | if length > 18 then .[:18] else . + " " * (18 - length) end)  \(.package_id // "unknown")  \(.proxy // "—")"' "$ORDERS_FILE" 2>/dev/null

    echo ""
    echo "Total: $ORDER_COUNT order(s)"

    local TIMED_OUT
    TIMED_OUT=$(jq '[.orders[] | select(.status == "timed_out")] | length' "$ORDERS_FILE")
    if [[ "$TIMED_OUT" -gt 0 ]]; then
        echo ""
        echo "⚠️  $TIMED_OUT order(s) timed out during polling. Resume with:"
        jq -r '.orders[] | select(.status == "timed_out") | "  bash '"$SKILL_DIR"'/proxybase.sh poll \(.order_id) --max-attempts 200"' "$ORDERS_FILE"
    fi

    echo ""

    # Refresh all statuses from API if we have credentials
    if [[ -n "${PROXYBASE_API_KEY:-}" ]]; then
        echo "Refreshing live status..."

        acquire_lock

        jq -r '.orders[].order_id' "$ORDERS_FILE" | while read -r OID; do
            local REFRESH_RC=0
            api_call GET "/orders/$OID/status" || REFRESH_RC=$?
            if [[ $REFRESH_RC -ne 0 ]]; then
                echo "  $OID: refresh failed (HTTP $API_HTTP_CODE)" >&2
                continue
            fi

            local LIVE_STATUS
            LIVE_STATUS=$(echo "$API_RESPONSE" | jq -r '.status // empty')
            if [[ -z "$LIVE_STATUS" ]]; then
                continue
            fi

            local UPDATED
            UPDATED=$(jq --arg oid "$OID" --arg s "$LIVE_STATUS" \
                '(.orders[] | select(.order_id == $oid)).status = $s' "$ORDERS_FILE")
            if validate_json "$UPDATED"; then
                echo "$UPDATED" > "$ORDERS_FILE"
            fi

            if [[ "$LIVE_STATUS" == "proxy_active" ]]; then
                local HOST PORT USER PASS
                HOST=$(echo "$API_RESPONSE" | jq -r '.proxy.host // "api.proxybase.xyz"')
                PORT=$(echo "$API_RESPONSE" | jq -r '.proxy.port // 1080')
                USER=$(echo "$API_RESPONSE" | jq -r '.proxy.username // empty')
                PASS=$(echo "$API_RESPONSE" | jq -r '.proxy.password // empty')
                if [[ -n "$USER" && -n "$PASS" ]]; then
                    # Validate proxy credentials before storing
                    if build_safe_proxy_url "$HOST" "$PORT" "$USER" "$PASS"; then
                        UPDATED=$(jq --arg oid "$OID" --arg p "$PROXY_URL" \
                            '(.orders[] | select(.order_id == $oid)).proxy = $p' "$ORDERS_FILE")
                        if validate_json "$UPDATED"; then
                            echo "$UPDATED" > "$ORDERS_FILE"
                        fi
                    else
                        echo "  $OID: SECURITY WARNING — proxy credentials contain invalid characters" >&2
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

    local ACTIVE_COUNT
    ACTIVE_COUNT=$(jq '[.orders[] | select(.status == "proxy_active")] | length' "$ORDERS_FILE")
    if [[ "$ACTIVE_COUNT" -gt 0 ]]; then
        echo "Active proxies ($ACTIVE_COUNT):"
        jq -r '.orders[] | select(.status == "proxy_active") | "  \(.order_id): \(.proxy)"' "$ORDERS_FILE"
        echo ""
        echo "Use proxy:"
        echo "  source $PROXY_ENV_FILE"
        echo "  curl https://lemontv.xyz/api/ip"
    fi
}

# ─── topup ────────────────────────────────────────────────────────────
cmd_topup() {
    local ORDER_ID="${1:-}"
    local PACKAGE_ID="${2:-}"
    local PAY_CURRENCY="${3:-usdcsol}"

    if [[ -z "$ORDER_ID" || -z "$PACKAGE_ID" ]]; then
        echo "ERROR: order_id and package_id are required"
        echo "Usage: bash proxybase.sh topup <order_id> <package_id> [pay_currency]"
        echo ""
        echo "Available packages: us_residential_1gb, us_residential_5gb, us_residential_10gb"
        exit 1
    fi

    # Validate inputs to prevent injection
    validate_safe_string "$ORDER_ID" "order_id" || { echo "ERROR: order_id contains invalid characters"; exit 1; }
    validate_safe_string "$PACKAGE_ID" "package_id" || { echo "ERROR: package_id contains invalid characters"; exit 1; }

    load_credentials --required || exit 1
    init_orders_file

    local REQUEST_BODY
    REQUEST_BODY=$(jq -n \
        --arg pkg "$PACKAGE_ID" \
        --arg cur "$PAY_CURRENCY" \
        '{package_id: $pkg, pay_currency: $cur}')

    echo "ProxyBase: Creating top-up for order $ORDER_ID (package=$PACKAGE_ID, currency=$PAY_CURRENCY)..."

    local TOPUP_RC=0
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

    local TOPUP_PAY_ADDRESS TOPUP_PAY_AMOUNT TOPUP_CURRENCY TOPUP_STATUS TOPUP_EXPIRY
    TOPUP_PAY_ADDRESS=$(echo "$API_RESPONSE" | jq -r '.pay_address // "unknown"')
    TOPUP_PAY_AMOUNT=$(echo "$API_RESPONSE" | jq -r '.pay_amount // "unknown"')
    TOPUP_CURRENCY=$(echo "$API_RESPONSE" | jq -r '.pay_currency // "unknown"')
    TOPUP_STATUS=$(echo "$API_RESPONSE" | jq -r '.status // "payment_pending"')
    TOPUP_EXPIRY=$(echo "$API_RESPONSE" | jq -r '.expiration_estimate_date // "~24 hours"')

    acquire_lock

    if jq -e ".orders[] | select(.order_id == \"$ORDER_ID\")" "$ORDERS_FILE" > /dev/null 2>&1; then
        local TIMESTAMP
        TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        local UPDATED
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
    echo "  bash $SKILL_DIR/proxybase.sh poll $ORDER_ID"
}

# ─── rotate ───────────────────────────────────────────────────────────
cmd_rotate() {
    local ORDER_ID="${1:-}"

    if [[ -z "$ORDER_ID" ]]; then
        echo "ERROR: order_id is required"
        echo "Usage: bash proxybase.sh rotate <order_id>"
        exit 1
    fi

    # Validate order_id to prevent injection
    validate_safe_string "$ORDER_ID" "order_id" || { echo "ERROR: order_id contains invalid characters"; exit 1; }

    load_credentials --required || exit 1
    init_orders_file

    echo "ProxyBase: Rotating proxy credentials for order $ORDER_ID..."

    local ROTATE_RC=0
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

    local HOST PORT USERNAME PASSWORD
    HOST=$(echo "$API_RESPONSE" | jq -r '.proxy.host // "api.proxybase.xyz"')
    PORT=$(echo "$API_RESPONSE" | jq -r '.proxy.port // 1080')
    USERNAME=$(echo "$API_RESPONSE" | jq -r '.proxy.username // empty')
    PASSWORD=$(echo "$API_RESPONSE" | jq -r '.proxy.password // empty')

    if [[ -z "$USERNAME" || -z "$PASSWORD" ]]; then
        echo "ERROR: No proxy credentials in rotation response"
        echo "$API_RESPONSE" | jq .
        exit 1
    fi

    # Validate proxy credentials from API response (prevents shell injection)
    if ! build_safe_proxy_url "$HOST" "$PORT" "$USERNAME" "$PASSWORD"; then
        echo "ERROR: API returned proxy credentials with invalid characters (possible compromise)" >&2
        exit 1
    fi
    # PROXY_URL is now set by build_safe_proxy_url

    acquire_lock

    if jq -e ".orders[] | select(.order_id == \"$ORDER_ID\")" "$ORDERS_FILE" > /dev/null 2>&1; then
        local TIMESTAMP
        TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        local UPDATED
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

    local ORDER_PROXY_ENV="${STATE_DIR}/.proxy-env-${ORDER_ID}"
    write_proxy_env_file "$ORDER_PROXY_ENV" "$ORDER_ID" "$PROXY_URL" "rotated" || {
        echo "ERROR: Failed to write proxy env file" >&2
        exit 1
    }
    cp -f "$ORDER_PROXY_ENV" "$PROXY_ENV_FILE"

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
}

# ─── inject-gateway ──────────────────────────────────────────────────
cmd_inject_gateway() {
    local ORDER_ID="${1:-}"
    local DRY_RUN=false

    for arg in "$@"; do
        case "$arg" in
            --dry-run) DRY_RUN=true ;;
            -*) ;;
            *) ORDER_ID="$arg" ;;
        esac
    done

    if [[ -z "$ORDER_ID" ]]; then
        echo "ERROR: order_id is required"
        echo "Usage: bash proxybase.sh inject-gateway <order_id> [--dry-run]"
        exit 1
    fi

    # Validate order_id to prevent injection
    validate_safe_string "$ORDER_ID" "order_id" || { echo "ERROR: order_id contains invalid characters"; exit 1; }

    init_orders_file

    acquire_lock
    local PROXY_URL
    PROXY_URL=$(jq -r --arg oid "$ORDER_ID" '.orders[] | select(.order_id == $oid) | .proxy // empty' "$ORDERS_FILE" 2>/dev/null)
    release_lock

    if [[ -z "$PROXY_URL" ]]; then
        echo "ERROR: Could not find an active proxy URL for order $ORDER_ID"
        exit 1
    fi

    # Validate the proxy URL before injecting into systemd service
    if ! validate_safe_string "$PROXY_URL" "proxy_url"; then
        echo "ERROR: Proxy URL contains invalid characters — refusing to inject into systemd service"
        echo "This may indicate a compromised API response or corrupted state file." >&2
        exit 1
    fi

    local SERVICE_FILE="$HOME/.config/systemd/user/openclaw-gateway.service"

    if [[ ! -f "$SERVICE_FILE" ]]; then
        echo "ERROR: Systemd service file not found at $SERVICE_FILE"
        echo "Cannot inject proxy configuration."
        exit 1
    fi

    if ! grep -q '\[Service\]' "$SERVICE_FILE"; then
        echo "ERROR: No [Service] section found in $SERVICE_FILE"
        echo "Cannot inject proxy environment variables."
        exit 1
    fi

    # Verify this is actually an OpenClaw gateway service file
    if ! grep -qE 'openclaw|OpenClaw' "$SERVICE_FILE"; then
        echo "ERROR: $SERVICE_FILE does not appear to be an OpenClaw gateway service"
        echo "Refusing to modify unrecognized service file."
        exit 1
    fi

    # Dry-run: show what would be changed without modifying anything
    if [[ "$DRY_RUN" == true ]]; then
        echo "ProxyBase: DRY RUN — would inject into $SERVICE_FILE:"
        echo "  Environment=HTTP_PROXY=$PROXY_URL"
        echo "  Environment=HTTPS_PROXY=$PROXY_URL"
        echo "  Environment=NODE_USE_ENV_PROXY=1"
        echo ""
        echo "No changes were made. Remove --dry-run to apply."
        exit 0
    fi

    echo "ProxyBase: Injecting proxy into $SERVICE_FILE..."

    cp "$SERVICE_FILE" "${SERVICE_FILE}.bak"

    if sed --version 2>/dev/null | grep -q 'GNU'; then
        sed -i '/^Environment=HTTP_PROXY=/d;/^Environment=HTTPS_PROXY=/d;/^Environment=NODE_USE_ENV_PROXY=/d' "$SERVICE_FILE"
    else
        sed -i '' '/^Environment=HTTP_PROXY=/d;/^Environment=HTTPS_PROXY=/d;/^Environment=NODE_USE_ENV_PROXY=/d' "$SERVICE_FILE"
    fi

    awk -v proxy="$PROXY_URL" '
/^\[Service\]/ {
    print $0
    print "Environment=HTTP_PROXY=" proxy
    print "Environment=HTTPS_PROXY=" proxy
    print "Environment=NODE_USE_ENV_PROXY=1"
    next
}
{ print $0 }
' "$SERVICE_FILE" > "${SERVICE_FILE}.new"

    if [[ ! -s "${SERVICE_FILE}.new" ]]; then
        echo "ERROR: awk produced an empty output — aborting. Original file restored from .bak" >&2
        cp "${SERVICE_FILE}.bak" "$SERVICE_FILE"
        rm -f "${SERVICE_FILE}.new"
        exit 1
    fi

    if ! grep -q 'Environment=HTTP_PROXY=' "${SERVICE_FILE}.new"; then
        echo "ERROR: Proxy environment lines not found in rewritten file — aborting." >&2
        cp "${SERVICE_FILE}.bak" "$SERVICE_FILE"
        rm -f "${SERVICE_FILE}.new"
        exit 1
    fi

    mv "${SERVICE_FILE}.new" "$SERVICE_FILE"

    echo "ProxyBase: Configuration updated successfully."
    echo "  HTTP_PROXY=$PROXY_URL"
    echo "  HTTPS_PROXY=$PROXY_URL"
    echo "  NODE_USE_ENV_PROXY=1"
    echo ""

    echo "ProxyBase: Reloading systemd daemon..."
    if command -v systemctl >/dev/null 2>&1; then
        systemctl --user daemon-reload || {
            echo "WARN: systemctl --user daemon-reload failed."
        }
    else
        echo "WARN: systemctl not found."
    fi

    echo "ProxyBase: Restarting OpenClaw Gateway..."
    if command -v openclaw >/dev/null 2>&1; then
        openclaw gateway restart || {
            echo "ERROR: Failed to run 'openclaw gateway restart'."
            exit 1
        }
    else
        echo "ERROR: 'openclaw' command not found. Cannot restart the gateway."
        exit 1
    fi

    echo "✅ Success! OpenClaw Gateway is now routing traffic through proxy $ORDER_ID."
    exit 0
}

# ─── help ─────────────────────────────────────────────────────────────
cmd_help() {
    echo "ProxyBase — SOCKS5 Proxy Purchasing & Management"
    echo ""
    echo "Usage: bash proxybase.sh <command> [args...]"
    echo ""
    echo "Commands:"
    echo "  register                            Register agent + store API key"
    echo "  order <pkg> [currency] [cb_url]     Create a proxy order"
    echo "  poll <order_id> [options]            Poll order until terminal state"
    echo "  status [order_id] [--cleanup]        Show order status"
    echo "  topup <order_id> <pkg> [currency]    Top up bandwidth"
    echo "  rotate <order_id>                    Rotate proxy credentials"
    echo "  inject-gateway <order_id> [--dry-run] Inject proxy into OpenClaw gateway"
    echo "  help                                 Show this help"
    echo ""
    echo "Poll options:"
    echo "  --once               Single status check"
    echo "  --quiet              Only output on state changes"
    echo "  --max-attempts N     Override max poll attempts (default: 100)"
    echo ""
    echo "Packages: us_residential_1gb (\$10), us_residential_5gb (\$50), us_residential_10gb (\$100)"
    echo "Default currency: usdcsol"
}

# ═════════════════════════════════════════════════════════════════════
# MAIN DISPATCH
# ═════════════════════════════════════════════════════════════════════

COMMAND="${1:-help}"
shift 2>/dev/null || true

case "$COMMAND" in
    register)        cmd_register "$@" ;;
    order)           cmd_order "$@" ;;
    poll)            cmd_poll "$@" ;;
    status)          cmd_status "$@" ;;
    topup)           cmd_topup "$@" ;;
    rotate)          cmd_rotate "$@" ;;
    inject-gateway)  cmd_inject_gateway "$@" ;;
    help|--help|-h)  cmd_help ;;
    *)
        echo "Unknown command: $COMMAND"
        echo "Run: bash proxybase.sh help"
        exit 1
        ;;
esac
