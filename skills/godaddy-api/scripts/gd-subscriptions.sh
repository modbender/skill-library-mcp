#!/usr/bin/env bash
#
# gd-subscriptions.sh - GoDaddy subscription operations
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/gd-api.sh"

confirm() {
  local msg="$1"
  read -r -p "${msg} [y/N] " reply
  [[ "$reply" =~ ^[Yy]$ ]]
}

usage() {
  cat <<EOF
Usage:
  $0 list
  $0 get <subscriptionId>
  $0 cancel <subscriptionId> [payload.json]
EOF
  exit 1
}

cmd="${1:-}"
shift || true

case "$cmd" in
  list)
    gd_api GET "/v1/subscriptions" | jq .
    ;;

  get)
    subscription_id="${1:?subscriptionId required}"
    gd_api GET "/v1/subscriptions/${subscription_id}" | jq .
    ;;

  cancel)
    subscription_id="${1:?subscriptionId required}"
    file="${2:-}"
    echo "⚠️  WARNING: This will cancel subscription ${subscription_id}." >&2
    confirm "Continue?" || { echo "Aborted." >&2; exit 1; }
    if [[ -n "$file" ]]; then
      [[ -f "$file" ]] || { echo "Error: File not found: $file" >&2; exit 1; }
      gd_api POST "/v1/subscriptions/${subscription_id}/cancel" "$(cat "$file")" | jq .
    else
      gd_api POST "/v1/subscriptions/${subscription_id}/cancel" "{}" | jq .
    fi
    ;;

  *)
    usage
    ;;
esac
