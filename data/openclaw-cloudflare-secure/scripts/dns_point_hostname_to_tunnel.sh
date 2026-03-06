#!/usr/bin/env bash
set -euo pipefail

# Depends on the bundled Cloudflare DNS helper script in this skill.

CFPY="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/cf_dns.py"

ZONE=""
HOSTNAME=""
TUNNEL_UUID=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --zone) ZONE="$2"; shift 2;;
    --hostname) HOSTNAME="$2"; shift 2;;
    --tunnel-uuid) TUNNEL_UUID="$2"; shift 2;;
    -h|--help)
      echo "Usage: $0 --zone avmil.xyz --hostname lobster.avmil.xyz --tunnel-uuid <uuid>";
      exit 0;;
    *)
      echo "Unknown arg: $1" >&2; exit 2;;
  esac
done

if [[ -z "$ZONE" || -z "$HOSTNAME" || -z "$TUNNEL_UUID" ]]; then
  echo "Missing required args." >&2
  exit 2
fi

if [[ ! -x "$CFPY" ]]; then
  echo "Missing cf_dns.py at $CFPY" >&2
  exit 1
fi

# Delete existing A/AAAA/CNAME records for the hostname
existing_json=$("$CFPY" dns list --zone "$ZONE" --name "$HOSTNAME")

# Extract record ids (best-effort; keeps script dependency-free)
record_ids=$(python3 - <<'PY'
import json,sys
recs=json.load(sys.stdin)
for r in recs:
  if r.get('type') in ('A','AAAA','CNAME') and r.get('id'):
    print(r['id'])
PY
<<<"$existing_json")

if [[ -n "$record_ids" ]]; then
  while read -r rid; do
    [[ -z "$rid" ]] && continue
    echo "Deleting existing DNS record id=$rid for $HOSTNAME"
    "$CFPY" dns delete --zone "$ZONE" --record-id "$rid"
  done <<<"$record_ids"
fi

TARGET="${TUNNEL_UUID}.cfargotunnel.com"
echo "Upserting CNAME $HOSTNAME -> $TARGET (proxied)"
"$CFPY" dns upsert --zone "$ZONE" --type CNAME --name "$HOSTNAME" --content "$TARGET" --proxied true
