#!/bin/bash
# uf2.sh - CLI wrapper for uf2.net URL shortener API

set -euo pipefail

API_BASE="https://uf2.net/api/v1"
API_KEY="${UF2_API_KEY:-}"

usage() {
  cat <<EOF
Usage: uf2.sh <command> [options]

Commands:
  create <url> [slug] [title]  Create a short link
  list [limit] [offset]        List your links (default: 50)
  get <code>                   Get link metadata & click count
  delete <code>                Delete a link
  account                      Show account info

Environment:
  UF2_API_KEY                  API key (required for most commands)

Examples:
  uf2.sh create https://example.com/long/path my-slug "My Link"
  uf2.sh list 10
  uf2.sh get abc123
  uf2.sh delete abc123
  uf2.sh account
EOF
  exit 1
}

require_auth() {
  if [[ -z "$API_KEY" ]]; then
    echo "Error: UF2_API_KEY environment variable not set" >&2
    exit 1
  fi
}

cmd_create() {
  require_auth
  local url="${1:-}"
  local slug="${2:-}"
  local title="${3:-}"
  
  if [[ -z "$url" ]]; then
    echo "Error: URL required" >&2
    exit 1
  fi
  
  local body="{\"url\":\"$url\""
  [[ -n "$slug" ]] && body="$body,\"slug\":\"$slug\""
  [[ -n "$title" ]] && body="$body,\"title\":\"$title\""
  body="$body}"
  
  curl -s -X POST "$API_BASE/links" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "$body"
}

cmd_list() {
  require_auth
  local limit="${1:-50}"
  local offset="${2:-0}"
  
  curl -s -X GET "$API_BASE/links?limit=$limit&offset=$offset" \
    -H "X-API-Key: $API_KEY"
}

cmd_get() {
  local code="${1:-}"
  
  if [[ -z "$code" ]]; then
    echo "Error: Code required" >&2
    exit 1
  fi
  
  curl -s -X GET "$API_BASE/links/$code"
}

cmd_delete() {
  require_auth
  local code="${1:-}"
  
  if [[ -z "$code" ]]; then
    echo "Error: Code required" >&2
    exit 1
  fi
  
  curl -s -X DELETE "$API_BASE/links/$code" \
    -H "X-API-Key: $API_KEY"
}

cmd_account() {
  require_auth
  curl -s -X GET "$API_BASE/accounts/me" \
    -H "X-API-Key: $API_KEY"
}

[[ $# -eq 0 ]] && usage

case "$1" in
  create)  cmd_create "${@:2}" ;;
  list)    cmd_list "${@:2}" ;;
  get)     cmd_get "${@:2}" ;;
  delete)  cmd_delete "${@:2}" ;;
  account) cmd_account ;;
  *)       usage ;;
esac
