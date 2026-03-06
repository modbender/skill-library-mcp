#!/usr/bin/env bash
set -euo pipefail

BASE_URL="https://api.nasdaq.com/api/screener/stocks"
USER_AGENT="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
ACCEPT="application/json, text/plain, */*"
REFERER="https://www.nasdaq.com/market-activity/stocks/screener"

limit="25"
offset="0"
exchange=""
tableonly="true"
download="true"
format="raw"
print_url="false"
timeout_sec="30"

usage() {
  cat <<USAGE
Usage: $(basename "$0") [options]

Query Nasdaq public stock screener endpoint.

Options:
  --limit N           Page size (default: 25)
  --offset N          Page offset (default: 0)
  --exchange EX       Exchange filter: NASDAQ|NYSE|AMEX
  --tableonly BOOL    true|false (default: true)
  --download BOOL     true|false (default: true)
  --format FMT        raw|rows|symbols (default: raw)
  --timeout SEC       Curl timeout seconds (default: 30)
  --print-url         Print resolved request URL and exit
  -h, --help          Show this help

Examples:
  $(basename "$0") --exchange NASDAQ --limit 100 --offset 0 --format symbols
  $(basename "$0") --exchange NYSE --limit 50 --offset 100 --format rows
USAGE
}

die() {
  echo "error: $*" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "required command not found: $1"
}

is_bool() {
  [[ "$1" == "true" || "$1" == "false" ]]
}

is_uint() {
  [[ "$1" =~ ^[0-9]+$ ]]
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --limit)
      shift
      [[ $# -gt 0 ]] || die "--limit requires a value"
      limit="$1"
      ;;
    --offset)
      shift
      [[ $# -gt 0 ]] || die "--offset requires a value"
      offset="$1"
      ;;
    --exchange)
      shift
      [[ $# -gt 0 ]] || die "--exchange requires a value"
      exchange="${1^^}"
      ;;
    --tableonly)
      shift
      [[ $# -gt 0 ]] || die "--tableonly requires a value"
      tableonly="$1"
      ;;
    --download)
      shift
      [[ $# -gt 0 ]] || die "--download requires a value"
      download="$1"
      ;;
    --format)
      shift
      [[ $# -gt 0 ]] || die "--format requires a value"
      format="$1"
      ;;
    --timeout)
      shift
      [[ $# -gt 0 ]] || die "--timeout requires a value"
      timeout_sec="$1"
      ;;
    --print-url)
      print_url="true"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "unknown option: $1"
      ;;
  esac
  shift
done

is_uint "$limit" || die "--limit must be a non-negative integer"
is_uint "$offset" || die "--offset must be a non-negative integer"
is_uint "$timeout_sec" || die "--timeout must be a non-negative integer"
is_bool "$tableonly" || die "--tableonly must be true or false"
is_bool "$download" || die "--download must be true or false"

if [[ -n "$exchange" ]]; then
  case "$exchange" in
    NASDAQ|NYSE|AMEX) ;;
    *) die "--exchange must be NASDAQ, NYSE, or AMEX" ;;
  esac
fi

case "$format" in
  raw|rows|symbols) ;;
  *) die "--format must be raw, rows, or symbols" ;;
esac

need_cmd curl

query="tableonly=${tableonly}&limit=${limit}&offset=${offset}&download=${download}"
if [[ -n "$exchange" ]]; then
  query+="&exchange=${exchange}"
fi
url="${BASE_URL}?${query}"

if [[ "$print_url" == "true" ]]; then
  echo "$url"
  exit 0
fi

response="$({
  curl --silent --show-error --fail \
    --connect-timeout 10 \
    --max-time "$timeout_sec" \
    -H "Accept: ${ACCEPT}" \
    -H "User-Agent: ${USER_AGENT}" \
    -H "Referer: ${REFERER}" \
    "$url"
} )"

if [[ "$format" == "raw" ]]; then
  printf '%s\n' "$response"
  exit 0
fi

need_cmd jq

if [[ "$format" == "rows" ]]; then
  printf '%s\n' "$response" | jq -c '.data.rows // []'
  exit 0
fi

printf '%s\n' "$response" | jq -r '.data.rows[]?.symbol // empty'
