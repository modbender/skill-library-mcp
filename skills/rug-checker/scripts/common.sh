#!/usr/bin/env bash
# ============================================================================
# common.sh — Anvil AI DeFi Stack Shared Library
# ============================================================================
# Reusable functions for Solana DeFi skills (rug-checker, wallet-xray, etc.)
# Source this file: source "$(dirname "$0")/common.sh"
#
# Dependencies: bash 4+, curl, jq, bc
# No API keys required — all endpoints are free/public.
# ============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Temp file tracking and cleanup
# ---------------------------------------------------------------------------
_CF_TMPFILES=()
cf_mktemp() {
  local f
  f=$(mktemp)
  _CF_TMPFILES+=("$f")
  echo "$f"
}
trap 'rm -f "${_CF_TMPFILES[@]}" 2>/dev/null' EXIT

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
readonly DEXSCREENER_BASE="https://api.dexscreener.com"
readonly RUGCHECK_BASE="https://api.rugcheck.xyz/v1"
readonly SOLANA_RPC="${SOLANA_RPC_URL:-https://api.mainnet-beta.solana.com}"

readonly DEXSCREENER_RATE_LIMIT=300  # req/min for search/tokens/pairs
readonly RUGCHECK_RATE_LIMIT=30      # conservative estimate (undocumented)

readonly USER_AGENT="CacheForge-DeFi-Stack/0.1.2"

# State directory for rate limiting
readonly _CF_STATE_DIR="${XDG_STATE_HOME:-${HOME}/.local/state}/cacheforge"
readonly _CF_RATE_FILE="${_CF_STATE_DIR}/rate_limits"

# ---------------------------------------------------------------------------
# Dependency check
# ---------------------------------------------------------------------------
cf_check_deps() {
  local missing=()
  for cmd in curl jq bc; do
    if ! command -v "$cmd" &>/dev/null; then
      missing+=("$cmd")
    fi
  done
  if [[ ${#missing[@]} -gt 0 ]]; then
    cf_error "Missing required dependencies: ${missing[*]}"
    cf_error "Install with: sudo apt install ${missing[*]}  (or brew install ${missing[*]})"
    cf_error "Note: 'bc' is required for all floating-point risk comparisons."
    return 1
  fi
}

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
cf_info()  { echo "[INFO]  $*" >&2; }
cf_warn()  { echo "[WARN]  $*" >&2; }
cf_error() { echo "[ERROR] $*" >&2; }
cf_debug() {
  if [[ "${CF_DEBUG:-0}" == "1" ]]; then
    echo "[DEBUG] $*" >&2
  fi
}

# ---------------------------------------------------------------------------
# Rate Limiting (token-bucket per domain)
# ---------------------------------------------------------------------------
_cf_rate_init() {
  mkdir -p "$_CF_STATE_DIR"
  touch "$_CF_RATE_FILE"
}

# Sliding-window rate limiter: tracks last N request timestamps per domain.
# Uses flock for advisory locking to prevent concurrent write corruption.
# When at limit, sleeps until the oldest request in the window expires.
# Usage: cf_rate_wait "dexscreener" 300
cf_rate_wait() {
  local domain="$1"
  local max_per_min="${2:-60}"
  _cf_rate_init

  local sleep_needed=0

  (
    # Advisory lock to prevent concurrent read-modify-write corruption
    if command -v flock &>/dev/null; then
      flock -x 200
    fi

    local now
    now=$(date +%s)
    local window_start=$(( now - 60 ))

    # Read existing timestamps for this domain, filter to last 60s window.
    # Also preserve other domains' entries.
    local count=0
    local other_entries=""
    local domain_timestamps=()

    if [[ -f "$_CF_RATE_FILE" ]]; then
      while IFS='|' read -r d ts; do
        [[ -z "$d" ]] && continue
        if [[ "$d" == "$domain" ]]; then
          if [[ "$ts" -ge "$window_start" ]]; then
            domain_timestamps+=("$ts")
            count=$(( count + 1 ))
          fi
          # else: expired, drop it
        else
          other_entries="${other_entries}${d}|${ts}\n"
        fi
      done < "$_CF_RATE_FILE"
    fi

    # If at limit, compute how long until the oldest request expires
    if [[ $count -ge $max_per_min ]]; then
      # Find the oldest timestamp in the window
      local oldest="$now"
      for ts in "${domain_timestamps[@]}"; do
        if [[ "$ts" -lt "$oldest" ]]; then
          oldest="$ts"
        fi
      done
      # Sleep until that oldest entry falls outside the 60s window
      local sleep_time=$(( 60 - (now - oldest) + 1 ))
      if [[ $sleep_time -gt 0 && $sleep_time -le 61 ]]; then
        cf_warn "Rate limit reached for $domain (${count}/${max_per_min} in 60s), waiting ${sleep_time}s..."
        sleep "$sleep_time"
        # After sleeping, re-read now and drop the expired entry
        now=$(date +%s)
        window_start=$(( now - 60 ))
        # Rebuild domain_timestamps excluding expired
        local new_timestamps=()
        for ts in "${domain_timestamps[@]}"; do
          if [[ "$ts" -ge "$window_start" ]]; then
            new_timestamps+=("$ts")
          fi
        done
        domain_timestamps=("${new_timestamps[@]+"${new_timestamps[@]}"}")
      fi
    fi

    # Record this request
    now=$(date +%s)
    domain_timestamps+=("$now")

    # Write back all entries
    {
      printf '%b' "$other_entries"
      for ts in "${domain_timestamps[@]}"; do
        printf '%s|%s\n' "$domain" "$ts"
      done
    } > "$_CF_RATE_FILE"

  ) 200>"${_CF_RATE_FILE}.lock"
}

# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

# Generic GET with retries, timeout, and rate limiting.
# Usage: cf_http_get "https://..." ["domain_for_rate_limit" [max_per_min]]
# Returns: response body on stdout, exit code 0 on success
cf_http_get() {
  local url="$1"
  local domain="${2:-}"
  local rate_limit="${3:-60}"
  local max_retries="${CF_MAX_RETRIES:-2}"
  local timeout="${CF_HTTP_TIMEOUT:-15}"

  if [[ -n "$domain" ]]; then
    cf_rate_wait "$domain" "$rate_limit"
  fi

  local attempt=0
  local response=""
  local http_code=""

  while [[ $attempt -le $max_retries ]]; do
    cf_debug "GET $url (attempt $((attempt + 1)))"

    # Use a temp file for the body so we can capture the HTTP code
    local tmpfile
    tmpfile=$(cf_mktemp)
    http_code=$(curl -s -o "$tmpfile" -w "%{http_code}" \
      --max-time "$timeout" \
      -H "User-Agent: ${USER_AGENT}" \
      "$url" 2>/dev/null) || http_code="000"

    response=$(cat "$tmpfile")
    rm -f "$tmpfile"

    case "$http_code" in
      200) echo "$response"; return 0 ;;
      429)
        cf_warn "Rate limited (429) on $url, backing off..."
        sleep $(( (attempt + 1) * 5 ))
        ;;
      404)
        cf_debug "Not found (404): $url"
        echo "$response"; return 44  # special exit code for not found
        ;;
      000)
        cf_warn "Connection failed for $url (timeout or DNS)"
        sleep $(( (attempt + 1) * 2 ))
        ;;
      *)
        cf_warn "HTTP $http_code from $url"
        sleep $(( (attempt + 1) * 2 ))
        ;;
    esac

    attempt=$(( attempt + 1 ))
  done

  cf_error "Failed after $((max_retries + 1)) attempts: $url (last HTTP $http_code)"
  return 1
}

# Solana RPC JSON-RPC call
# Usage: cf_solana_rpc "methodName" '["param1", {"encoding":"jsonParsed"}]'
# Returns: full JSON-RPC response on stdout
cf_solana_rpc() {
  local method="$1"
  local params="${2:-[]}"
  local timeout="${CF_HTTP_TIMEOUT:-15}"
  local max_retries="${CF_MAX_RETRIES:-2}"

  local payload
  payload=$(jq -n --arg m "$method" --argjson p "$params" \
    '{"jsonrpc":"2.0","id":1,"method":$m,"params":$p}')

  local attempt=0
  while [[ $attempt -le $max_retries ]]; do
    cf_debug "RPC $method (attempt $((attempt + 1)))"

    local tmpfile
    tmpfile=$(cf_mktemp)
    local http_code
    http_code=$(curl -s -o "$tmpfile" -w "%{http_code}" \
      --max-time "$timeout" \
      -X POST \
      -H "Content-Type: application/json" \
      -H "User-Agent: ${USER_AGENT}" \
      -d "$payload" \
      "$SOLANA_RPC" 2>/dev/null) || http_code="000"

    local response
    response=$(cat "$tmpfile")
    rm -f "$tmpfile"

    if [[ "$http_code" == "200" ]]; then
      # Check for JSON-RPC error
      local rpc_error
      rpc_error=$(echo "$response" | jq -r '.error.code // empty' 2>/dev/null)
      if [[ "$rpc_error" == "429" ]]; then
        cf_warn "Solana RPC rate limited for $method, backing off..."
        sleep $(( (attempt + 1) * 5 ))
      elif [[ -n "$rpc_error" ]]; then
        local rpc_msg
        rpc_msg=$(echo "$response" | jq -r '.error.message // "unknown"' 2>/dev/null)
        cf_debug "RPC error $rpc_error: $rpc_msg"
        echo "$response"
        return 1
      else
        echo "$response"
        return 0
      fi
    else
      cf_warn "HTTP $http_code from Solana RPC"
      sleep $(( (attempt + 1) * 2 ))
    fi

    attempt=$(( attempt + 1 ))
  done

  cf_error "Solana RPC failed after $((max_retries + 1)) attempts: $method"
  return 1
}

# ---------------------------------------------------------------------------
# DexScreener API wrappers
# ---------------------------------------------------------------------------

# Search DexScreener by name/symbol
# Returns: array of Solana pairs
dex_search() {
  local query="$1"
  local encoded
  encoded=$(printf '%s' "$query" | jq -sRr @uri)
  local response
  response=$(cf_http_get "${DEXSCREENER_BASE}/latest/dex/search?q=${encoded}" "dexscreener" "$DEXSCREENER_RATE_LIMIT") || return 1
  echo "$response" | jq '[.pairs[] | select(.chainId == "solana")]'
}

# Get token market data by address
# Returns: array of pair objects
dex_token() {
  local address="$1"
  cf_http_get "${DEXSCREENER_BASE}/tokens/v1/solana/${address}" "dexscreener" "$DEXSCREENER_RATE_LIMIT"
}

# Get all trading pairs for a token
dex_token_pairs() {
  local address="$1"
  cf_http_get "${DEXSCREENER_BASE}/token-pairs/v1/solana/${address}" "dexscreener" "$DEXSCREENER_RATE_LIMIT"
}

# ---------------------------------------------------------------------------
# Rugcheck API wrappers
# ---------------------------------------------------------------------------

# Get full rug report for a token mint
# Returns: full report JSON
rugcheck_report() {
  local mint="$1"
  cf_http_get "${RUGCHECK_BASE}/tokens/${mint}/report" "rugcheck" "$RUGCHECK_RATE_LIMIT"
}

# ---------------------------------------------------------------------------
# Solana RPC wrappers
# ---------------------------------------------------------------------------

# Get parsed account info for a mint
# Returns: { decimals, freezeAuthority, mintAuthority, supply, isInitialized }
solana_mint_info() {
  local mint="$1"
  local params
  params=$(jq -n --arg m "$mint" '[$m, {"encoding": "jsonParsed"}]')
  local response
  response=$(cf_solana_rpc "getAccountInfo" "$params") || return 1
  echo "$response" | jq '.result.value.data.parsed.info // empty'
}

# Get token supply
solana_token_supply() {
  local mint="$1"
  local params
  params=$(jq -n --arg m "$mint" '[$m]')
  local response
  response=$(cf_solana_rpc "getTokenSupply" "$params") || return 1
  echo "$response" | jq '.result.value // empty'
}

# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

# Check if string looks like a valid Solana address (base58, 32-44 chars)
is_solana_address() {
  local addr="$1"
  [[ "$addr" =~ ^[1-9A-HJ-NP-Za-km-z]{32,44}$ ]]
}

# Pretty-print large numbers (1234567 → 1,234,567)
format_number() {
  local num="$1"
  printf "%'.0f" "$num" 2>/dev/null || echo "$num"
}

# Format USD amount (human-friendly: $1.2B, $3.4M, $56.7K, $12.34)
format_usd() {
  local val="$1"
  if [[ -z "$val" || "$val" == "0" || "$val" == "null" || "$val" == "N/A" ]]; then
    echo "N/A"
  elif (( $(echo "$val >= 1000000000" | bc -l 2>/dev/null || echo 0) )); then
    printf "\$%.1fB" "$(echo "$val / 1000000000" | bc -l)"
  elif (( $(echo "$val >= 1000000" | bc -l 2>/dev/null || echo 0) )); then
    printf "\$%.1fM" "$(echo "$val / 1000000" | bc -l)"
  elif (( $(echo "$val >= 1000" | bc -l 2>/dev/null || echo 0) )); then
    printf "\$%.1fK" "$(echo "$val / 1000" | bc -l)"
  else
    printf "\$%.2f" "$val"
  fi
}

# Format percentage
format_pct() {
  local pct="$1"
  printf "%.1f%%" "$pct" 2>/dev/null || echo "${pct}%"
}

# Epoch millis to human-readable date
epoch_ms_to_date() {
  local ms="$1"
  local secs=$(( ms / 1000 ))
  date -d "@${secs}" "+%Y-%m-%d %H:%M UTC" 2>/dev/null || \
    date -r "$secs" "+%Y-%m-%d %H:%M UTC" 2>/dev/null || \
    echo "unknown"
}

# Calculate age in human-readable form from epoch millis
epoch_ms_to_age() {
  local ms="$1"
  local now_ms
  now_ms=$(( $(date +%s) * 1000 ))
  local diff_ms=$(( now_ms - ms ))
  local diff_hours=$(( diff_ms / 3600000 ))
  local diff_days=$(( diff_hours / 24 ))

  if [[ $diff_days -gt 365 ]]; then
    echo "$(( diff_days / 365 ))y $(( (diff_days % 365) / 30 ))mo"
  elif [[ $diff_days -gt 30 ]]; then
    echo "$(( diff_days / 30 ))mo $(( diff_days % 30 ))d"
  elif [[ $diff_days -gt 0 ]]; then
    echo "${diff_days}d"
  elif [[ $diff_hours -gt 0 ]]; then
    echo "${diff_hours}h"
  else
    echo "<1h"
  fi
}

# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------

# Safe jq extraction with default
jq_default() {
  local json="$1"
  local path="$2"
  local default="${3:-null}"
  echo "$json" | jq -r "${path} // ${default}" 2>/dev/null || echo "$default"
}

# Check if jq output is null/empty
jq_is_null() {
  local val="$1"
  [[ -z "$val" || "$val" == "null" || "$val" == "" ]]
}

# ---------------------------------------------------------------------------
# Disclaimer
# ---------------------------------------------------------------------------
readonly CF_DISCLAIMER="⚠️ DISCLAIMER: This report is for informational purposes only and does NOT constitute financial advice. Risk scores are algorithmic estimates based on on-chain data. Always do your own research (DYOR) before making investment decisions. CacheForge is not responsible for any financial losses."

# ---------------------------------------------------------------------------
# Init
# ---------------------------------------------------------------------------
cf_check_deps
