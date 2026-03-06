#!/usr/bin/env bash
set -euo pipefail

DEFAULT_BASE_URL="https://cloud.iexapis.com/stable"
SANDBOX_BASE_URL="https://sandbox.iexapis.com/stable"
DEFAULT_TIMEOUT="20"

show_help() {
  cat <<'USAGE'
IEX Cloud CLI

Usage:
  iex_cloud_cli.sh [global options] <command> [args]

Global options:
  --token TOKEN         API token (default: IEX_TOKEN or IEX_CLOUD_TOKEN)
  --base-url URL        Base URL (default: https://cloud.iexapis.com/stable)
  --sandbox             Use sandbox base URL
  --timeout SECONDS     Curl max-time in seconds (default: 20)
  --compact             Compact JSON output
  --raw-output          Print response without jq formatting
  -h, --help            Show help

Commands:
  quote SYMBOL
  chart SYMBOL RANGE
  company SYMBOL
  stats SYMBOL
  news SYMBOL [LAST]
  movers LIST_TYPE
  batch SYMBOLS TYPES
  raw PATH [key=value ...]

Examples:
  iex_cloud_cli.sh quote AAPL
  iex_cloud_cli.sh chart AAPL 1m
  iex_cloud_cli.sh news MSFT 5
  iex_cloud_cli.sh movers mostactive
  iex_cloud_cli.sh batch AAPL,MSFT quote,stats
  iex_cloud_cli.sh raw stock/AAPL/quote
USAGE
}

die() {
  echo "error: $*" >&2
  exit 1
}

warn() {
  echo "warning: $*" >&2
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"
}

is_valid_list_type() {
  case "$1" in
    mostactive|gainers|losers|iexvolume|iexpercent)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

is_trusted_base_url() {
  local url="$1"
  local host=""

  [[ "$url" =~ ^https://([^/:?#]+) ]] || return 1
  host="${BASH_REMATCH[1],,}"

  case "$host" in
    cloud.iexapis.com|sandbox.iexapis.com)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

validate_raw_path() {
  local path="$1"

  [[ "$path" != *"://"* ]] || die "raw PATH must be a relative API path, not a full URL"
  [[ "$path" != /* ]] || die "raw PATH must not start with '/'"
  [[ "$path" != *".."* ]] || die "raw PATH must not contain '..'"
  [[ "$path" != *"?"* ]] || die "raw PATH must not contain '?'; pass query items as key=value args"
  [[ "$path" != *"#"* ]] || die "raw PATH must not contain '#'"
}

TOKEN="${IEX_TOKEN:-${IEX_CLOUD_TOKEN:-}}"
BASE_URL="${IEX_BASE_URL:-$DEFAULT_BASE_URL}"
TIMEOUT="$DEFAULT_TIMEOUT"
COMPACT=0
RAW_OUTPUT=0
BASE_URL_SOURCE="default"

if [[ -n "${IEX_BASE_URL:-}" ]]; then
  BASE_URL_SOURCE="env"
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --token)
      [[ $# -ge 2 ]] || die "--token requires a value"
      TOKEN="$2"
      shift 2
      ;;
    --base-url)
      [[ $# -ge 2 ]] || die "--base-url requires a value"
      BASE_URL="$2"
      BASE_URL_SOURCE="flag"
      shift 2
      ;;
    --sandbox)
      BASE_URL="$SANDBOX_BASE_URL"
      BASE_URL_SOURCE="sandbox"
      shift
      ;;
    --timeout)
      [[ $# -ge 2 ]] || die "--timeout requires a value"
      TIMEOUT="$2"
      shift 2
      ;;
    --compact)
      COMPACT=1
      shift
      ;;
    --raw-output)
      RAW_OUTPUT=1
      shift
      ;;
    -h|--help)
      show_help
      exit 0
      ;;
    --)
      shift
      break
      ;;
    -* )
      die "Unknown option: $1"
      ;;
    *)
      break
      ;;
  esac
done

[[ $# -ge 1 ]] || {
  show_help
  exit 1
}

need_cmd curl
[[ -n "$TOKEN" ]] || die "Missing token. Set IEX_TOKEN/IEX_CLOUD_TOKEN or pass --token"
is_trusted_base_url "$BASE_URL" || die "Untrusted base URL host. Allowed hosts: cloud.iexapis.com, sandbox.iexapis.com"

if [[ "$BASE_URL" != "$DEFAULT_BASE_URL" && "$BASE_URL" != "$SANDBOX_BASE_URL" ]]; then
  warn "using non-default trusted base URL override: $BASE_URL"
elif [[ "$BASE_URL_SOURCE" == "env" || "$BASE_URL_SOURCE" == "flag" ]]; then
  warn "using explicit base URL configuration: $BASE_URL"
fi

COMMAND="$1"
shift

PATH_PART=""
PARAMS=()

case "$COMMAND" in
  quote)
    [[ $# -eq 1 ]] || die "Usage: quote SYMBOL"
    PATH_PART="stock/$1/quote"
    ;;
  chart)
    [[ $# -eq 2 ]] || die "Usage: chart SYMBOL RANGE"
    PATH_PART="stock/$1/chart/$2"
    ;;
  company)
    [[ $# -eq 1 ]] || die "Usage: company SYMBOL"
    PATH_PART="stock/$1/company"
    ;;
  stats)
    [[ $# -eq 1 ]] || die "Usage: stats SYMBOL"
    PATH_PART="stock/$1/stats"
    ;;
  news)
    [[ $# -ge 1 && $# -le 2 ]] || die "Usage: news SYMBOL [LAST]"
    LAST="${2:-10}"
    PATH_PART="stock/$1/news/last/$LAST"
    ;;
  movers)
    [[ $# -eq 1 ]] || die "Usage: movers LIST_TYPE"
    is_valid_list_type "$1" || die "Invalid LIST_TYPE '$1'"
    PATH_PART="stock/market/list/$1"
    ;;
  batch)
    [[ $# -eq 2 ]] || die "Usage: batch SYMBOLS TYPES"
    PATH_PART="stock/market/batch"
    PARAMS+=("symbols=$1" "types=$2")
    ;;
  raw)
    [[ $# -ge 1 ]] || die "Usage: raw PATH [key=value ...]"
    PATH_PART="$1"
    validate_raw_path "$PATH_PART"
    shift
    while [[ $# -gt 0 ]]; do
      [[ "$1" == *=* ]] || die "Invalid raw param '$1'. Use key=value"
      PARAMS+=("$1")
      shift
    done
    ;;
  *)
    die "Unknown command: $COMMAND"
    ;;
esac

URL="${BASE_URL%/}/${PATH_PART#/}"

curl_args=(
  --silent
  --show-error
  --fail-with-body
  --max-time "$TIMEOUT"
  --get
  "$URL"
  --data-urlencode "token=$TOKEN"
)

for p in "${PARAMS[@]}"; do
  curl_args+=(--data-urlencode "$p")
done

if [[ "$RAW_OUTPUT" -eq 1 ]]; then
  curl "${curl_args[@]}"
  exit 0
fi

if command -v jq >/dev/null 2>&1; then
  if [[ "$COMPACT" -eq 1 ]]; then
    curl "${curl_args[@]}" | jq -c .
  else
    curl "${curl_args[@]}" | jq .
  fi
else
  curl "${curl_args[@]}"
fi
