#!/usr/bin/env bash
# common.sh — Shared utility functions for ProxyBase skill scripts
# Source this at the top of every script:
#   source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

# ─── Path setup ──────────────────────────────────────────────────────
# Resolve paths relative to the script that sources us.
# If LIB_DIR is already set (by an earlier source), skip re-computation.
if [[ -z "${_PROXYBASE_COMMON_LOADED:-}" ]]; then
    _PROXYBASE_COMMON_LOADED=1

    LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    SKILL_DIR="$(dirname "$LIB_DIR")"
    SCRIPT_DIR="$SKILL_DIR/scripts"
    STATE_DIR="$SKILL_DIR/state"
    ORDERS_FILE="$STATE_DIR/orders.json"
    CREDS_FILE="$STATE_DIR/credentials.env"
    PROXY_ENV_FILE="$STATE_DIR/.proxy-env"
    LOCK_FILE="$STATE_DIR/orders.lock"

    PROXYBASE_API_URL="${PROXYBASE_API_URL:-https://api.proxybase.xyz/v1}"

    # Ensure state dir exists
    mkdir -p "$STATE_DIR"
fi

# ─── File locking ────────────────────────────────────────────────────
# Usage:
#   acquire_lock          # blocks until lock acquired
#   release_lock          # release the lock (also automatic on exit)
#
# Uses flock(1) when available, falls back to a mkdir-based spinlock.

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
        # Fallback: mkdir-based lock (atomic on all POSIX systems)
        _LOCK_METHOD="mkdir"
        local LOCK_DIR="${LOCK_FILE}.d"
        local ATTEMPTS=0
        while ! mkdir "$LOCK_DIR" 2>/dev/null; do
            # Staleness detection: if lock dir is older than 120s, assume the
            # holder was killed (SIGKILL / crash) and force-remove.
            if [[ -d "$LOCK_DIR" ]]; then
                local LOCK_AGE=0
                if command -v stat &>/dev/null; then
                    # macOS stat vs GNU stat
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

# Auto-release lock on script exit
trap 'release_lock' EXIT

# ─── JSON validation ─────────────────────────────────────────────────
# validate_json <string>
#   Returns 0 if the string is valid JSON, 1 otherwise.
validate_json() {
    local data="$1"
    if [[ -z "$data" ]]; then
        return 1
    fi
    echo "$data" | jq empty >/dev/null 2>&1
}

# ─── Safe API call ───────────────────────────────────────────────────
# api_call <method> <path> [curl_extra_args...]
#   Makes a curl call and validates the response is JSON.
#   Sets two global vars:  API_RESPONSE  API_HTTP_CODE
#   Returns 0 on success, 1 on network/parse error, 2 on HTTP error.
#
# Tmpfile lifecycle: cleaned up via a trap stack that restores the
# previous EXIT trap after the function returns, ensuring no /tmp leaks
# even on SIGINT/SIGTERM mid-curl.
api_call() {
    local METHOD="$1"
    shift
    local PATH_="$1"
    shift

    local TMPFILE
    TMPFILE=$(mktemp)

    # Push a local cleanup trap (restores the outer trap on return)
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

    # Restore previous EXIT trap
    trap "${_PREV_TRAP:-release_lock}" EXIT

    # Check for HTML error pages / non-JSON responses
    if ! validate_json "$API_RESPONSE"; then
        local SNIPPET="${API_RESPONSE:0:200}"
        API_RESPONSE=$(jq -n --arg code "$API_HTTP_CODE" --arg body "$SNIPPET" \
            '{"error":"invalid_json","message":"API returned non-JSON response","http_code":$code,"body_preview":$body}')
        return 1
    fi

    # Check HTTP status codes
    case "$API_HTTP_CODE" in
        2*) return 0 ;;          # 2xx — success
        429)
            # Rate limited — extract Retry-After if present
            return 2
            ;;
        *)
            return 2
            ;;
    esac
}

# ─── Retry wrapper ───────────────────────────────────────────────────
# api_call_with_retry <method> <path> [curl_extra_args...]
#   Calls api_call with up to 3 retries for network/429 errors.
#   Waits 2s, 5s, 10s between retries. On 429, respects Retry-After if present.
api_call_with_retry() {
    local DELAYS=(2 5 10)
    local ATTEMPT=0

    while [[ $ATTEMPT -le 3 ]]; do
        local RC=0
        api_call "$@" || RC=$?

        if [[ $RC -eq 0 ]]; then
            return 0
        fi

        # Don't retry 4xx errors (except 429) — they are client errors
        if [[ "$API_HTTP_CODE" =~ ^4[0-9][0-9]$ && "$API_HTTP_CODE" != "429" ]]; then
            return $RC
        fi

        if [[ $ATTEMPT -ge 3 ]]; then
            return $RC
        fi

        # On 429, check Retry-After
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
# load_credentials [--required]
#   Loads PROXYBASE_API_KEY from state/credentials.env if not already set.
#   With --required: exits 1 if no key is available.
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
        
        # Source the registration script to fetch and export a new key inline
        if [[ -f "$SCRIPT_DIR/proxybase-register.sh" ]]; then
            # Use `source` so the ENV vars bleed up into our current shell context
            source "$SCRIPT_DIR/proxybase-register.sh" || {
                echo "ERROR: Auto-registration failed." >&2
                return 1
            }
        else
            echo "ERROR: proxybase-register.sh not found at $SCRIPT_DIR/proxybase-register.sh. Cannot auto-register." >&2
            return 1
        fi
        
        # If it's still missing after auto-register, fail out
        if [[ -z "${PROXYBASE_API_KEY:-}" ]]; then
            echo "ERROR: Auto-registration completed but PROXYBASE_API_KEY is still not set." >&2
            return 1
        fi
    fi
}

# ─── Orders file helpers ─────────────────────────────────────────────
# init_orders_file
#   Creates orders.json if it doesn't exist yet.
init_orders_file() {
    if [[ ! -f "$ORDERS_FILE" ]]; then
        echo '{"orders":[]}' > "$ORDERS_FILE"
    fi
}

# update_order_field <order_id> <field> <value>
#   Updates a single field on an order in orders.json (under lock).
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
