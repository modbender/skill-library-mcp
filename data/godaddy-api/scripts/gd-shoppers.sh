#!/usr/bin/env bash
#
# gd-shoppers.sh - GoDaddy shopper operations
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/gd-api.sh"

confirm() {
  local msg="$1"
  read -r -p "${msg} [y/N] " reply
  [[ "$reply" =~ ^[Yy]$ ]]
}

require_file() {
  local file="$1"
  [[ -f "$file" ]] || { echo "Error: File not found: $file" >&2; exit 1; }
}

usage() {
  cat <<EOF
Usage:
  $0 get <shopperId>
  $0 update <shopperId> <payload.json>
  $0 delete <shopperId>
EOF
  exit 1
}

cmd="${1:-}"
shift || true

case "$cmd" in
  get)
    shopper_id="${1:?shopperId required}"
    gd_api GET "/v1/shoppers/${shopper_id}" | jq .
    ;;

  update)
    shopper_id="${1:?shopperId required}"
    file="${2:?JSON payload file required}"
    require_file "$file"
    gd_api PATCH "/v1/shoppers/${shopper_id}" "$(cat "$file")" | jq .
    ;;

  delete)
    shopper_id="${1:?shopperId required}"
    echo "⚠️  WARNING: This will delete shopper ${shopper_id}." >&2
    confirm "Continue?" || { echo "Aborted." >&2; exit 1; }
    gd_api DELETE "/v1/shoppers/${shopper_id}" | jq .
    ;;

  *)
    usage
    ;;
esac
