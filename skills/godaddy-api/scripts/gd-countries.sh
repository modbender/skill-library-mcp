#!/usr/bin/env bash
#
# gd-countries.sh - GoDaddy country metadata operations
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/gd-api.sh"

usage() {
  cat <<EOF
Usage:
  $0 list
EOF
  exit 1
}

cmd="${1:-}"
shift || true

case "$cmd" in
  list)
    gd_api GET "/v1/countries" | jq .
    ;;

  *)
    usage
    ;;
esac
