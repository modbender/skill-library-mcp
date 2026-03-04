#!/usr/bin/env bash
#
# gd-domains.sh - GoDaddy domain operations
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
  $0 list
  $0 get <domain>
  $0 available <domain> [FAST|FULL] [forTransfer=true|false]
  $0 available-bulk <file.json> [FAST|FULL]
  $0 validate-purchase <payload.json>
  $0 purchase <payload.json>
  $0 renew <domain> <periodYears>
  $0 transfer <domain> <payload.json>
  $0 update <domain> <payload.json>
  $0 update-contacts <domain> <contacts.json>
  $0 delete <domain>
  $0 privacy-enable <domain>
  $0 privacy-disable <domain>
  $0 agreements-get [queryString]
  $0 agreements-accept <payload.json>

Notes:
  - agreements-get queryString example: tlds=com,net&privacy=true&forTransfer=false
  - update / update-contacts payloads are sent as-is (see references/request-bodies.md)
EOF
  exit 1
}

cmd="${1:-}"
shift || true

case "$cmd" in
  list)
    gd_api GET "/v1/domains" | jq .
    ;;

  get)
    domain="${1:?Domain required}"
    gd_api GET "/v1/domains/${domain}" | jq .
    ;;

  available)
    domain="${1:?Domain required}"
    check_type="${2:-FAST}"
    for_transfer="${3:-false}"
    gd_api GET "/v1/domains/available?domain=${domain}&checkType=${check_type}&forTransfer=${for_transfer}" | jq .
    ;;

  available-bulk)
    file="${1:?JSON file required}"
    check_type="${2:-FAST}"
    require_file "$file"
    gd_api POST "/v1/domains/available?checkType=${check_type}" "$(cat "$file")" | jq .
    ;;

  validate-purchase)
    file="${1:?JSON payload file required}"
    require_file "$file"
    gd_api POST "/v1/domains/purchase/validate" "$(cat "$file")" | jq .
    ;;

  purchase)
    file="${1:?JSON payload file required}"
    require_file "$file"
    echo "⚠️  WARNING: This will purchase a domain and charge your account." >&2
    echo "Payload: $(jq -c . "$file")" >&2
    confirm "Continue?" || { echo "Aborted." >&2; exit 1; }
    gd_api POST "/v1/domains/purchase" "$(cat "$file")" | jq .
    ;;

  renew)
    domain="${1:?Domain required}"
    period="${2:?Period (years) required}"
    echo "⚠️  WARNING: This will renew ${domain} for ${period} year(s) and charge your account." >&2
    confirm "Continue?" || { echo "Aborted." >&2; exit 1; }
    gd_api POST "/v1/domains/${domain}/renew" "{\"period\": ${period}}" | jq .
    ;;

  transfer)
    domain="${1:?Domain required}"
    file="${2:?JSON payload file required}"
    require_file "$file"
    echo "⚠️  WARNING: This may initiate a paid transfer for ${domain}." >&2
    confirm "Continue?" || { echo "Aborted." >&2; exit 1; }
    gd_api POST "/v1/domains/${domain}/transfer" "$(cat "$file")" | jq .
    ;;

  update)
    domain="${1:?Domain required}"
    file="${2:?JSON payload file required}"
    require_file "$file"
    gd_api PATCH "/v1/domains/${domain}" "$(cat "$file")" | jq .
    ;;

  update-contacts)
    domain="${1:?Domain required}"
    file="${2:?JSON contacts payload file required}"
    require_file "$file"
    gd_api PATCH "/v1/domains/${domain}/contacts" "$(cat "$file")" | jq .
    ;;

  delete)
    domain="${1:?Domain required}"
    echo "⚠️  WARNING: This will cancel/delete ${domain}. This may be irreversible." >&2
    confirm "Continue?" || { echo "Aborted." >&2; exit 1; }
    gd_api DELETE "/v1/domains/${domain}" | jq .
    ;;

  privacy-enable)
    domain="${1:?Domain required}"
    echo "⚠️  WARNING: This may incur privacy-protection charges for ${domain}." >&2
    confirm "Continue?" || { echo "Aborted." >&2; exit 1; }
    gd_api PUT "/v1/domains/${domain}/privacy" "{}" | jq .
    ;;

  privacy-disable)
    domain="${1:?Domain required}"
    echo "⚠️  WARNING: This will disable privacy protection for ${domain}." >&2
    confirm "Continue?" || { echo "Aborted." >&2; exit 1; }
    gd_api DELETE "/v1/domains/${domain}/privacy" | jq .
    ;;

  agreements-get)
    query="${1:-}"
    if [[ -n "$query" ]]; then
      gd_api GET "/v1/domains/agreements?${query}" | jq .
    else
      gd_api GET "/v1/domains/agreements" | jq .
    fi
    ;;

  agreements-accept)
    file="${1:?JSON payload file required}"
    require_file "$file"
    echo "⚠️  WARNING: This records legal agreement acceptance." >&2
    confirm "Continue?" || { echo "Aborted." >&2; exit 1; }
    gd_api POST "/v1/domains/agreements" "$(cat "$file")" | jq .
    ;;

  *)
    usage
    ;;
esac
