#!/usr/bin/env bash
#
# gd-aftermarket.sh - GoDaddy aftermarket listings operations
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/gd-api.sh"

usage() {
  cat <<EOF
Usage:
  $0 list [queryString]
  $0 get <listingId>

Example queryString:
  status=ACTIVE&pageSize=50&pageNumber=1
EOF
  exit 1
}

cmd="${1:-}"
shift || true

case "$cmd" in
  list)
    query="${1:-}"
    if [[ -n "$query" ]]; then
      gd_api GET "/v1/aftermarket/listings?${query}" | jq .
    else
      gd_api GET "/v1/aftermarket/listings" | jq .
    fi
    ;;

  get)
    listing_id="${1:?listingId required}"
    gd_api GET "/v1/aftermarket/listings/${listing_id}" | jq .
    ;;

  *)
    usage
    ;;
esac
