#!/usr/bin/env bash
set -euo pipefail

REST_BASE="${WEIBO_REST_BASE:-https://api.weibo.com/2}"
OAUTH_BASE="${WEIBO_OAUTH_BASE:-https://api.weibo.com/oauth2}"

usage() {
  cat <<'EOF'
Weibo API CLI

Usage:
  bash scripts/weibo_cli.sh <command> [options]

Commands:
  oauth-authorize-url [--state STATE] [--scope SCOPE] [--display DISPLAY]
  oauth-access-token --code CODE [--redirect-uri URI]
  oauth-token-info [--access-token TOKEN]
  public-timeline [--count N] [--page N] [--access-token TOKEN]
  user-timeline --uid UID [--count N] [--page N] [--access-token TOKEN]
  search-topics --q QUERY [--count N] [--page N] [--access-token TOKEN]
  call --method METHOD --path /2/xxx.json [--param key=value ...] [--access-token TOKEN]

Environment:
  WEIBO_APP_KEY        OAuth client id / app key
  WEIBO_APP_SECRET     OAuth client secret
  WEIBO_REDIRECT_URI   OAuth callback URL
  WEIBO_ACCESS_TOKEN   Default bearer token for API calls

Examples:
  bash scripts/weibo_cli.sh oauth-authorize-url
  bash scripts/weibo_cli.sh oauth-access-token --code "<code>"
  bash scripts/weibo_cli.sh public-timeline --count 20
  bash scripts/weibo_cli.sh call --method GET --path /2/statuses/public_timeline.json --param count=10
EOF
}

urlencode() {
  python3 - "$1" <<'PY'
import sys
from urllib.parse import quote
print(quote(sys.argv[1], safe=""))
PY
}

json_pretty_or_raw() {
  local payload="$1"
  if command -v jq >/dev/null 2>&1; then
    printf '%s\n' "$payload" | jq .
  else
    printf '%s\n' "$payload" | python3 -m json.tool 2>/dev/null || printf '%s\n' "$payload"
  fi
}

require_env() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    echo "error: missing required environment variable: $name" >&2
    exit 1
  fi
}

extract_error() {
  local payload="$1"
  python3 - "$payload" <<'PY'
import json
import sys
raw = sys.argv[1]
try:
    obj = json.loads(raw)
except Exception:
    print("")
    raise SystemExit(0)
msg = obj.get("error") or ""
code = obj.get("error_code")
if msg:
    print(f"{msg} ({code})" if code is not None else msg)
else:
    print("")
PY
}

api_request() {
  local method="$1"
  local url="$2"
  shift 2

  local response_with_status response http_status
  response_with_status="$(curl -sS -X "$method" "$url" "$@" -w $'\n__HTTP_STATUS__:%{http_code}')"
  http_status="${response_with_status##*__HTTP_STATUS__:}"
  response="${response_with_status%$'\n'__HTTP_STATUS__:*}"

  if [[ ! "$http_status" =~ ^[0-9]{3}$ ]]; then
    echo "error: unable to parse HTTP status" >&2
    printf '%s\n' "$response_with_status" >&2
    exit 2
  fi
  if (( http_status >= 400 )); then
    echo "http_error: status ${http_status}" >&2
    json_pretty_or_raw "$response" >&2
    exit 2
  fi

  local err
  err="$(extract_error "$response")"
  if [[ -n "$err" ]]; then
    echo "api_error: $err" >&2
    json_pretty_or_raw "$response" >&2
    exit 2
  fi
  json_pretty_or_raw "$response"
}

cmd_oauth_authorize_url() {
  require_env WEIBO_APP_KEY
  require_env WEIBO_REDIRECT_URI

  local state="" scope="" display=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --state) state="${2:-}"; shift 2 ;;
      --scope) scope="${2:-}"; shift 2 ;;
      --display) display="${2:-}"; shift 2 ;;
      *) echo "error: unknown option: $1" >&2; exit 1 ;;
    esac
  done

  local url="${OAUTH_BASE}/authorize?client_id=$(urlencode "$WEIBO_APP_KEY")&response_type=code&redirect_uri=$(urlencode "$WEIBO_REDIRECT_URI")"
  [[ -n "$state" ]] && url="${url}&state=$(urlencode "$state")"
  [[ -n "$scope" ]] && url="${url}&scope=$(urlencode "$scope")"
  [[ -n "$display" ]] && url="${url}&display=$(urlencode "$display")"
  printf '%s\n' "$url"
}

cmd_oauth_access_token() {
  require_env WEIBO_APP_KEY
  require_env WEIBO_APP_SECRET
  require_env WEIBO_REDIRECT_URI

  local code="" redirect_uri="$WEIBO_REDIRECT_URI"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --code) code="${2:-}"; shift 2 ;;
      --redirect-uri) redirect_uri="${2:-}"; shift 2 ;;
      *) echo "error: unknown option: $1" >&2; exit 1 ;;
    esac
  done
  [[ -z "$code" ]] && { echo "error: --code is required" >&2; exit 1; }

  api_request POST "${OAUTH_BASE}/access_token" \
    --data-urlencode "client_id=${WEIBO_APP_KEY}" \
    --data-urlencode "client_secret=${WEIBO_APP_SECRET}" \
    --data-urlencode "grant_type=authorization_code" \
    --data-urlencode "redirect_uri=${redirect_uri}" \
    --data-urlencode "code=${code}"
}

cmd_oauth_token_info() {
  local token="${WEIBO_ACCESS_TOKEN:-}"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --access-token) token="${2:-}"; shift 2 ;;
      *) echo "error: unknown option: $1" >&2; exit 1 ;;
    esac
  done
  [[ -z "$token" ]] && { echo "error: provide --access-token or WEIBO_ACCESS_TOKEN" >&2; exit 1; }

  api_request POST "${OAUTH_BASE}/get_token_info" \
    --data-urlencode "access_token=${token}"
}

cmd_public_timeline() {
  local token="${WEIBO_ACCESS_TOKEN:-}" count="20" page="1"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --access-token) token="${2:-}"; shift 2 ;;
      --count) count="${2:-}"; shift 2 ;;
      --page) page="${2:-}"; shift 2 ;;
      *) echo "error: unknown option: $1" >&2; exit 1 ;;
    esac
  done
  [[ -z "$token" ]] && { echo "error: provide --access-token or WEIBO_ACCESS_TOKEN" >&2; exit 1; }

  api_request GET "${REST_BASE}/statuses/public_timeline.json" \
    --get \
    --data-urlencode "access_token=${token}" \
    --data-urlencode "count=${count}" \
    --data-urlencode "page=${page}"
}

cmd_user_timeline() {
  local token="${WEIBO_ACCESS_TOKEN:-}" uid="" count="20" page="1"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --access-token) token="${2:-}"; shift 2 ;;
      --uid) uid="${2:-}"; shift 2 ;;
      --count) count="${2:-}"; shift 2 ;;
      --page) page="${2:-}"; shift 2 ;;
      *) echo "error: unknown option: $1" >&2; exit 1 ;;
    esac
  done
  [[ -z "$token" ]] && { echo "error: provide --access-token or WEIBO_ACCESS_TOKEN" >&2; exit 1; }
  [[ -z "$uid" ]] && { echo "error: --uid is required" >&2; exit 1; }

  api_request GET "${REST_BASE}/statuses/user_timeline.json" \
    --get \
    --data-urlencode "access_token=${token}" \
    --data-urlencode "uid=${uid}" \
    --data-urlencode "count=${count}" \
    --data-urlencode "page=${page}"
}

cmd_search_topics() {
  local token="${WEIBO_ACCESS_TOKEN:-}" q="" count="20" page="1"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --access-token) token="${2:-}"; shift 2 ;;
      --q) q="${2:-}"; shift 2 ;;
      --count) count="${2:-}"; shift 2 ;;
      --page) page="${2:-}"; shift 2 ;;
      *) echo "error: unknown option: $1" >&2; exit 1 ;;
    esac
  done
  [[ -z "$token" ]] && { echo "error: provide --access-token or WEIBO_ACCESS_TOKEN" >&2; exit 1; }
  [[ -z "$q" ]] && { echo "error: --q is required" >&2; exit 1; }

  api_request GET "${REST_BASE}/search/topics.json" \
    --get \
    --data-urlencode "access_token=${token}" \
    --data-urlencode "q=${q}" \
    --data-urlencode "count=${count}" \
    --data-urlencode "page=${page}"
}

cmd_call() {
  local method="GET" path="" token="${WEIBO_ACCESS_TOKEN:-}"
  local -a params=()
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --method) method="${2:-}"; shift 2 ;;
      --path) path="${2:-}"; shift 2 ;;
      --param) params+=("${2:-}"); shift 2 ;;
      --access-token) token="${2:-}"; shift 2 ;;
      *) echo "error: unknown option: $1" >&2; exit 1 ;;
    esac
  done
  [[ -z "$path" ]] && { echo "error: --path is required" >&2; exit 1; }

  local url
  if [[ "$path" =~ ^https?:// ]]; then
    url="$path"
  else
    if [[ "$path" == /2/* ]]; then
      url="https://api.weibo.com${path}"
    else
      url="${REST_BASE}/${path#/}"
    fi
  fi

  local -a curl_args=()
  if [[ "$method" == "GET" ]]; then
    curl_args+=(--get)
  fi
  [[ -n "$token" ]] && curl_args+=(--data-urlencode "access_token=${token}")
  for kv in "${params[@]}"; do
    curl_args+=(--data-urlencode "$kv")
  done

  api_request "$method" "$url" "${curl_args[@]}"
}

main() {
  local cmd="${1:-}"
  [[ $# -gt 0 ]] && shift || true
  case "$cmd" in
    oauth-authorize-url) cmd_oauth_authorize_url "$@" ;;
    oauth-access-token) cmd_oauth_access_token "$@" ;;
    oauth-token-info) cmd_oauth_token_info "$@" ;;
    public-timeline) cmd_public_timeline "$@" ;;
    user-timeline) cmd_user_timeline "$@" ;;
    search-topics) cmd_search_topics "$@" ;;
    call) cmd_call "$@" ;;
    -h|--help|"") usage ;;
    *) echo "error: unknown command: $cmd" >&2; usage; exit 1 ;;
  esac
}

main "$@"
