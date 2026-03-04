#!/usr/bin/env bash
#
# gd-certs.sh - GoDaddy certificate operations
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
  $0 create <payload.json>
  $0 validate <payload.json>
  $0 get <certificateId>
  $0 actions <certificateId>
  $0 download <certificateId>
  $0 renew <certificateId> <payload.json>
  $0 reissue <certificateId> <payload.json>
  $0 revoke <certificateId> <payload.json>
  $0 verify-domain-control <certificateId> <payload.json>
EOF
  exit 1
}

cmd="${1:-}"
shift || true

case "$cmd" in
  create)
    file="${1:?JSON payload file required}"
    require_file "$file"
    echo "⚠️  WARNING: This creates a certificate order and may charge your account." >&2
    confirm "Continue?" || { echo "Aborted." >&2; exit 1; }
    gd_api POST "/v1/certificates" "$(cat "$file")" | jq .
    ;;

  validate)
    file="${1:?JSON payload file required}"
    require_file "$file"
    gd_api POST "/v1/certificates/validate" "$(cat "$file")" | jq .
    ;;

  get)
    certificate_id="${1:?certificateId required}"
    gd_api GET "/v1/certificates/${certificate_id}" | jq .
    ;;

  actions)
    certificate_id="${1:?certificateId required}"
    gd_api GET "/v1/certificates/${certificate_id}/actions" | jq .
    ;;

  download)
    certificate_id="${1:?certificateId required}"
    gd_api GET "/v1/certificates/${certificate_id}/download" | jq .
    ;;

  renew)
    certificate_id="${1:?certificateId required}"
    file="${2:?JSON payload file required}"
    require_file "$file"
    echo "⚠️  WARNING: This may renew certificate ${certificate_id} and charge your account." >&2
    confirm "Continue?" || { echo "Aborted." >&2; exit 1; }
    gd_api POST "/v1/certificates/${certificate_id}/renew" "$(cat "$file")" | jq .
    ;;

  reissue)
    certificate_id="${1:?certificateId required}"
    file="${2:?JSON payload file required}"
    require_file "$file"
    gd_api POST "/v1/certificates/${certificate_id}/reissue" "$(cat "$file")" | jq .
    ;;

  revoke)
    certificate_id="${1:?certificateId required}"
    file="${2:?JSON payload file required}"
    require_file "$file"
    echo "⚠️  WARNING: This will revoke certificate ${certificate_id}." >&2
    confirm "Continue?" || { echo "Aborted." >&2; exit 1; }
    gd_api POST "/v1/certificates/${certificate_id}/revoke" "$(cat "$file")" | jq .
    ;;

  verify-domain-control)
    certificate_id="${1:?certificateId required}"
    file="${2:?JSON payload file required}"
    require_file "$file"
    gd_api POST "/v1/certificates/${certificate_id}/verifyDomainControl" "$(cat "$file")" | jq .
    ;;

  *)
    usage
    ;;
esac
