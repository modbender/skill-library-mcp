#!/usr/bin/env bash
set -euo pipefail

# Export runtime env vars from Vaultwarden item names (secure local use)
# Requires: BW_SESSION set (bw unlock)

ITEM_CLIENT_ID="${VW_ITEM_CLIENT_ID:-oc-bw-clientid}"
ITEM_CLIENT_SECRET="${VW_ITEM_CLIENT_SECRET:-oc-bw-clientsecret}"
ITEM_PASSWORD="${VW_ITEM_PASSWORD:-oc-bw-password}"

if ! command -v bw >/dev/null 2>&1; then
  echo "ERROR: bw CLI not found" >&2
  exit 1
fi

if [ -z "${BW_SESSION:-}" ]; then
  echo "ERROR: BW_SESSION missing. Run 'bw unlock' then export BW_SESSION." >&2
  exit 1
fi

extract_password_by_name() {
  local name="$1"
  local json id value
  json="$(bw list items --search "$name")"
  id="$(printf '%s' "$json" | python3 -c 'import sys,json; a=json.load(sys.stdin); print(a[0]["id"] if a else "")')"
  if [ -z "$id" ]; then
    echo ""
    return
  fi
  value="$(bw get item "$id" | python3 -c 'import sys,json; o=json.load(sys.stdin); print((o.get("login") or {}).get("password") or "")')"
  printf '%s' "$value"
}

CID="$(extract_password_by_name "$ITEM_CLIENT_ID")"
CSEC="$(extract_password_by_name "$ITEM_CLIENT_SECRET")"
CPW="$(extract_password_by_name "$ITEM_PASSWORD")"

if [ -z "$CID" ] || [ -z "$CSEC" ] || [ -z "$CPW" ]; then
  echo "ERROR: One or more required items are missing/empty in Vaultwarden." >&2
  echo "Expected item names: $ITEM_CLIENT_ID, $ITEM_CLIENT_SECRET, $ITEM_PASSWORD" >&2
  exit 1
fi

cat <<EOF
export BW_CLIENTID='$CID'
export BW_CLIENTSECRET='$CSEC'
export BW_PASSWORD='$CPW'
EOF
