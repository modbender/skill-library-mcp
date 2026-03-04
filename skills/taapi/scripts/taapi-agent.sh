#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${TAAPI_BASE_URL:-https://api.taapi.io}"
SECRET="${TAAPI_SECRET:-}"
DEFAULT_RETRIES="${TAAPI_RETRIES:-3}"
DEFAULT_TIMEOUT="${TAAPI_TIMEOUT:-30}"
ALLOW_UNOFFICIAL_BASE_URL="${TAAPI_ALLOW_UNOFFICIAL_BASE_URL:-0}"
OFFICIAL_BASE_URL="https://api.taapi.io"

usage() {
  cat <<'EOF'
taapi-agent.sh - Agent-friendly TAAPI.IO CLI

Usage:
  taapi-agent.sh direct --indicator NAME --symbol PAIR --interval TF [options]
  taapi-agent.sh bulk --payload-file FILE [options]
  taapi-agent.sh multi --symbols CSV --intervals CSV --indicators CSV [options]

Commands:
  direct    GET /{indicator}
  bulk      POST /bulk using a JSON payload file
  multi     Build a multi-construct /bulk payload from CSV lists, then execute

Global options:
  --secret VALUE         Override TAAPI_SECRET
  --base-url URL         Override API base URL (default: https://api.taapi.io)
  --allow-unofficial-base-url
                         Allow sending requests to a non-default base URL
  --retries N            Retry count for transient errors (default: 3)
  --timeout SECONDS      Curl timeout (default: 30)
  --json                 Force JSON output (default)
  --raw                  Raw response passthrough
  -h, --help             Show this help

direct options:
  --indicator NAME       Indicator endpoint (e.g., rsi, macd)
  --exchange NAME        Exchange (required for crypto)
  --symbol PAIR          Symbol like BTC/USDT
  --interval TF          Timeframe like 1h, 15m, 1d
  --type VALUE           crypto|stocks (default: crypto)
  --opt key=value        Additional indicator/query parameter (repeatable)

bulk options:
  --payload-file FILE    JSON payload file for /bulk

multi options:
  --exchange NAME        Exchange for all constructs (default: binance)
  --symbols CSV          Example: BTC/USDT,ETH/USDT
  --intervals CSV        Example: 15m,1h
  --indicators CSV       Example: rsi,macd,supertrend
  --type VALUE           crypto|stocks (default: crypto)
  --opt key=value        Additional indicator params applied to all indicators
EOF
}

die() {
  echo "error: $*" >&2
  exit 1
}

warn() {
  echo "warning: $*" >&2
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

normalize_url() {
  local url="$1"
  while [[ "$url" == */ ]]; do
    url="${url%/}"
  done
  printf '%s' "$url"
}

validate_base_url() {
  BASE_URL="$(normalize_url "$BASE_URL")"
  local official
  official="$(normalize_url "$OFFICIAL_BASE_URL")"

  if [[ "$BASE_URL" == "$official" ]]; then
    return 0
  fi

  if [[ "$ALLOW_UNOFFICIAL_BASE_URL" != "1" ]]; then
    die "refusing unofficial base URL: $BASE_URL (set TAAPI_ALLOW_UNOFFICIAL_BASE_URL=1 or pass --allow-unofficial-base-url to override)"
  fi

  warn "using unofficial TAAPI base URL $BASE_URL; TAAPI secrets and payloads will be sent to that endpoint"
}

urlencode() {
  local raw="$1"
  local out="" i c hex
  for ((i = 0; i < ${#raw}; i++)); do
    c="${raw:i:1}"
    case "$c" in
      [a-zA-Z0-9.~_-]) out+="$c" ;;
      *)
        printf -v hex '%%%02X' "'$c"
        out+="$hex"
        ;;
    esac
  done
  printf '%s' "$out"
}

http_with_retries() {
  local method="$1"
  local url="$2"
  local data="${3:-}"
  local retries="$4"
  local timeout="$5"

  local attempt=0
  local status body tmpfile curl_rc
  tmpfile="$(mktemp)"
  trap 'rm -f "$tmpfile"' RETURN

  while :; do
    attempt=$((attempt + 1))
    if [[ -n "$data" ]]; then
      set +e
      body="$(curl -sS --connect-timeout 10 --max-time "$timeout" \
        -X "$method" \
        -H "Content-Type: application/json" \
        -w $'\n%{http_code}' \
        --data "$data" \
        "$url" 2>"$tmpfile")"
      curl_rc=$?
      set -e
    else
      set +e
      body="$(curl -sS --connect-timeout 10 --max-time "$timeout" \
        -X "$method" \
        -w $'\n%{http_code}' \
        "$url" 2>"$tmpfile")"
      curl_rc=$?
      set -e
    fi

    if [[ $curl_rc -eq 0 ]]; then
      status="${body##*$'\n'}"
      body="${body%$'\n'*}"
      if [[ "$status" =~ ^2[0-9][0-9]$ ]]; then
        printf '%s\n' "$body"
        return 0
      fi
      if [[ "$status" == "429" || "$status" =~ ^5[0-9][0-9]$ ]]; then
        if (( attempt <= retries )); then
          sleep "$attempt"
          continue
        fi
      fi
      echo "$body" >&2
      die "http status $status from $url"
    else
      if (( attempt <= retries )); then
        sleep "$attempt"
        continue
      fi
      cat "$tmpfile" >&2 || true
      die "curl failed for $url"
    fi
  done
}

render_output() {
  local payload="$1"
  local mode="$2"
  if [[ "$mode" == "raw" ]]; then
    printf '%s\n' "$payload"
    return 0
  fi
  if command -v jq >/dev/null 2>&1; then
    printf '%s\n' "$payload" | jq .
  else
    printf '%s\n' "$payload"
  fi
}

build_direct_url() {
  local indicator="$1"
  shift
  local q="secret=$(urlencode "$SECRET")"
  local kv
  for kv in "$@"; do
    local k="${kv%%=*}"
    local v="${kv#*=}"
    q+="&$(urlencode "$k")=$(urlencode "$v")"
  done
  printf '%s/%s?%s' "$BASE_URL" "$indicator" "$q"
}

do_direct() {
  local indicator="" exchange="" symbol="" interval="" type="crypto"
  local output_mode="json" retries="$DEFAULT_RETRIES" timeout="$DEFAULT_TIMEOUT"
  local opts=()

  while (($#)); do
    case "$1" in
      --indicator) indicator="${2:-}"; shift 2 ;;
      --exchange) exchange="${2:-}"; shift 2 ;;
      --symbol) symbol="${2:-}"; shift 2 ;;
      --interval) interval="${2:-}"; shift 2 ;;
      --type) type="${2:-}"; shift 2 ;;
      --opt) opts+=("${2:-}"); shift 2 ;;
      --secret) SECRET="${2:-}"; shift 2 ;;
      --base-url) BASE_URL="${2:-}"; shift 2 ;;
      --allow-unofficial-base-url) ALLOW_UNOFFICIAL_BASE_URL="1"; shift ;;
      --retries) retries="${2:-}"; shift 2 ;;
      --timeout) timeout="${2:-}"; shift 2 ;;
      --json) output_mode="json"; shift ;;
      --raw) output_mode="raw"; shift ;;
      -h|--help) usage; exit 0 ;;
      *) die "unknown direct option: $1" ;;
    esac
  done

  [[ -n "$SECRET" ]] || die "missing secret (set TAAPI_SECRET or use --secret)"
  [[ -n "$indicator" ]] || die "missing --indicator"
  [[ -n "$symbol" ]] || die "missing --symbol"
  [[ -n "$interval" ]] || die "missing --interval"
  [[ -n "$type" ]] || die "missing --type"
  if [[ "$type" == "crypto" ]]; then
    [[ -n "$exchange" ]] || die "--exchange is required for crypto direct requests"
  fi
  validate_base_url

  local query=("symbol=$symbol" "interval=$interval" "type=$type")
  if [[ -n "$exchange" ]]; then
    query+=("exchange=$exchange")
  fi
  local kv
  for kv in "${opts[@]}"; do
    [[ "$kv" == *=* ]] || die "--opt must be key=value, got: $kv"
    query+=("$kv")
  done

  local url body
  url="$(build_direct_url "$indicator" "${query[@]}")"
  body="$(http_with_retries "GET" "$url" "" "$retries" "$timeout")"
  render_output "$body" "$output_mode"
}

do_bulk() {
  local payload_file="" output_mode="json" retries="$DEFAULT_RETRIES" timeout="$DEFAULT_TIMEOUT"
  while (($#)); do
    case "$1" in
      --payload-file) payload_file="${2:-}"; shift 2 ;;
      --secret) SECRET="${2:-}"; shift 2 ;;
      --base-url) BASE_URL="${2:-}"; shift 2 ;;
      --allow-unofficial-base-url) ALLOW_UNOFFICIAL_BASE_URL="1"; shift ;;
      --retries) retries="${2:-}"; shift 2 ;;
      --timeout) timeout="${2:-}"; shift 2 ;;
      --json) output_mode="json"; shift ;;
      --raw) output_mode="raw"; shift ;;
      -h|--help) usage; exit 0 ;;
      *) die "unknown bulk option: $1" ;;
    esac
  done

  [[ -n "$payload_file" ]] || die "missing --payload-file"
  [[ -r "$payload_file" ]] || die "cannot read payload file: $payload_file"
  local payload
  payload="$(cat "$payload_file")"

  # Replace placeholder in payload if present.
  if [[ -n "$SECRET" ]]; then
    payload="${payload//TAAPI_SECRET/$SECRET}"
  elif [[ "$payload" == *"TAAPI_SECRET"* ]]; then
    die "missing secret (set TAAPI_SECRET or use --secret before posting placeholder payloads)"
  fi

  validate_base_url

  local body
  body="$(http_with_retries "POST" "$BASE_URL/bulk" "$payload" "$retries" "$timeout")"
  render_output "$body" "$output_mode"
}

do_multi() {
  need_cmd jq
  local exchange="binance" symbols="" intervals="" indicators="" type="crypto"
  local output_mode="json" retries="$DEFAULT_RETRIES" timeout="$DEFAULT_TIMEOUT"
  local opts=()

  while (($#)); do
    case "$1" in
      --exchange) exchange="${2:-}"; shift 2 ;;
      --symbols) symbols="${2:-}"; shift 2 ;;
      --intervals) intervals="${2:-}"; shift 2 ;;
      --indicators) indicators="${2:-}"; shift 2 ;;
      --type) type="${2:-}"; shift 2 ;;
      --opt) opts+=("${2:-}"); shift 2 ;;
      --secret) SECRET="${2:-}"; shift 2 ;;
      --base-url) BASE_URL="${2:-}"; shift 2 ;;
      --allow-unofficial-base-url) ALLOW_UNOFFICIAL_BASE_URL="1"; shift ;;
      --retries) retries="${2:-}"; shift 2 ;;
      --timeout) timeout="${2:-}"; shift 2 ;;
      --json) output_mode="json"; shift ;;
      --raw) output_mode="raw"; shift ;;
      -h|--help) usage; exit 0 ;;
      *) die "unknown multi option: $1" ;;
    esac
  done

  [[ -n "$SECRET" ]] || die "missing secret (set TAAPI_SECRET or use --secret)"
  [[ -n "$symbols" ]] || die "missing --symbols"
  [[ -n "$intervals" ]] || die "missing --intervals"
  [[ -n "$indicators" ]] || die "missing --indicators"
  validate_base_url

  local indicators_json='[]'
  local indicator
  IFS=',' read -r -a _indicators <<<"$indicators"
  for indicator in "${_indicators[@]}"; do
    local entry
    entry="$(jq -nc --arg ind "$indicator" '{indicator: $ind}')"
    local kv
    for kv in "${opts[@]}"; do
      [[ "$kv" == *=* ]] || die "--opt must be key=value, got: $kv"
      local k="${kv%%=*}"
      local v="${kv#*=}"
      entry="$(jq -nc --argjson obj "$entry" --arg k "$k" --arg v "$v" '$obj + {($k): $v}')"
    done
    indicators_json="$(jq -nc --argjson arr "$indicators_json" --argjson e "$entry" '$arr + [$e]')"
  done

  local constructs='[]'
  local symbol interval
  IFS=',' read -r -a _symbols <<<"$symbols"
  IFS=',' read -r -a _intervals <<<"$intervals"
  for symbol in "${_symbols[@]}"; do
    for interval in "${_intervals[@]}"; do
      local construct
      if [[ "$type" == "stocks" ]]; then
        construct="$(jq -nc \
          --arg type "$type" \
          --arg symbol "$symbol" \
          --arg interval "$interval" \
          --argjson indicators "$indicators_json" \
          '{type: $type, symbol: $symbol, interval: $interval, indicators: $indicators}')"
      else
        construct="$(jq -nc \
          --arg type "$type" \
          --arg exchange "$exchange" \
          --arg symbol "$symbol" \
          --arg interval "$interval" \
          --argjson indicators "$indicators_json" \
          '{type: $type, exchange: $exchange, symbol: $symbol, interval: $interval, indicators: $indicators}')"
      fi
      constructs="$(jq -nc --argjson arr "$constructs" --argjson c "$construct" '$arr + [$c]')"
    done
  done

  local payload body
  payload="$(jq -nc --arg secret "$SECRET" --argjson constructs "$constructs" '{secret: $secret, constructs: $constructs}')"
  body="$(http_with_retries "POST" "$BASE_URL/bulk" "$payload" "$retries" "$timeout")"
  render_output "$body" "$output_mode"
}

main() {
  need_cmd curl
  local cmd="${1:-}"
  if [[ -z "$cmd" || "$cmd" == "-h" || "$cmd" == "--help" ]]; then
    usage
    exit 0
  fi
  shift || true

  case "$cmd" in
    direct) do_direct "$@" ;;
    bulk) do_bulk "$@" ;;
    multi) do_multi "$@" ;;
    *) die "unknown command: $cmd" ;;
  esac
}

main "$@"
