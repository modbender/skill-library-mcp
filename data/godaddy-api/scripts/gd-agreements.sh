#!/usr/bin/env bash
#
# gd-agreements.sh - GoDaddy legal agreements operations
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/gd-api.sh"

usage() {
  cat <<EOF
Usage:
  $0 list [queryString]

Example queryString:
  product=domain&marketId=en-US
EOF
  exit 1
}

cmd="${1:-}"
shift || true

case "$cmd" in
  list)
    query="${1:-}"
    if [[ -n "$query" ]]; then
      gd_api GET "/v1/agreements?${query}" | jq .
    else
      gd_api GET "/v1/agreements" | jq .
    fi
    ;;

  *)
    usage
    ;;
esac
