#!/usr/bin/env bash
#
# gd-dns.sh - GoDaddy DNS record operations
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
  $0 get-all <domain>
  $0 get-type <domain> <type>
  $0 get <domain> <type> <name>
  $0 add <domain> <records.json>
  $0 replace-all <domain> <records.json>
  $0 replace-type <domain> <type> <records.json>
  $0 replace-type-name <domain> <type> <name> <records.json>
  $0 delete-type-name <domain> <type> <name>

Types: A, AAAA, CNAME, TXT, MX, SRV, NS, etc.
Name: Use @ for apex, or subdomain name
EOF
  exit 1
}

cmd="${1:-}"
shift || true

case "$cmd" in
  get-all)
    domain="${1:?Domain required}"
    gd_api GET "/v1/domains/${domain}/records" | jq .
    ;;

  get-type)
    domain="${1:?Domain required}"
    type="${2:?Type required}"
    gd_api GET "/v1/domains/${domain}/records/${type}" | jq .
    ;;

  get)
    domain="${1:?Domain required}"
    type="${2:?Type required}"
    name="${3:?Name required}"
    gd_api GET "/v1/domains/${domain}/records/${type}/${name}" | jq .
    ;;

  add)
    domain="${1:?Domain required}"
    file="${2:?JSON file required}"
    require_file "$file"
    gd_api PATCH "/v1/domains/${domain}/records" "$(cat "$file")" | jq .
    ;;

  replace-all)
    domain="${1:?Domain required}"
    file="${2:?JSON file required}"
    require_file "$file"
    echo "⚠️  WARNING: This will REPLACE ALL DNS RECORDS for ${domain}." >&2
    echo "Payload: $(jq -c . "$file")" >&2
    confirm "Continue?" || { echo "Aborted." >&2; exit 1; }
    gd_api PUT "/v1/domains/${domain}/records" "$(cat "$file")" | jq .
    ;;

  replace-type)
    domain="${1:?Domain required}"
    type="${2:?Type required}"
    file="${3:?JSON file required}"
    require_file "$file"
    echo "⚠️  WARNING: This will replace all ${type} records for ${domain}." >&2
    confirm "Continue?" || { echo "Aborted." >&2; exit 1; }
    gd_api PUT "/v1/domains/${domain}/records/${type}" "$(cat "$file")" | jq .
    ;;

  replace-type-name)
    domain="${1:?Domain required}"
    type="${2:?Type required}"
    name="${3:?Name required}"
    file="${4:?JSON file required}"
    require_file "$file"
    gd_api PUT "/v1/domains/${domain}/records/${type}/${name}" "$(cat "$file")" | jq .
    ;;

  delete-type-name)
    domain="${1:?Domain required}"
    type="${2:?Type required}"
    name="${3:?Name required}"
    echo "⚠️  WARNING: This will delete ${type} record '${name}' for ${domain}." >&2
    confirm "Continue?" || { echo "Aborted." >&2; exit 1; }
    gd_api DELETE "/v1/domains/${domain}/records/${type}/${name}" | jq .
    ;;

  *)
    usage
    ;;
esac
