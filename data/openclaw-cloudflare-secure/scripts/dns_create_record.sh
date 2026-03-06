#!/usr/bin/env bash
set -euo pipefail

# Convenience wrapper around cf_dns.py for creating/updating DNS records.
# Requires:
#   export CLOUDFLARE_API_TOKEN='...'

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CFPY="$DIR/cf_dns.py"

ZONE=""
NAME=""
TYPE=""
CONTENT=""
PROXIED="true"
TTL=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --zone) ZONE="$2"; shift 2;;
    --name) NAME="$2"; shift 2;;
    --type) TYPE="$2"; shift 2;;
    --content) CONTENT="$2"; shift 2;;
    --proxied) PROXIED="$2"; shift 2;;
    --ttl) TTL="$2"; shift 2;;
    -h|--help)
      cat <<EOF
Usage:
  $0 --zone example.com --type A --name openclaw --content 1.2.3.4 --proxied true
  $0 --zone example.com --type CNAME --name openclaw --content target.example.net --proxied true

Notes:
- --name can be relative (openclaw) or FQDN (openclaw.example.com)
- --proxied defaults to true (orange cloud)
- Requires CLOUDFLARE_API_TOKEN
EOF
      exit 0;;
    *) echo "Unknown arg: $1" >&2; exit 2;;
  esac
done

if [[ -z "$ZONE" || -z "$NAME" || -z "$TYPE" || -z "$CONTENT" ]]; then
  echo "Missing required args. Use --help." >&2
  exit 2
fi

args=(dns upsert --zone "$ZONE" --type "$TYPE" --name "$NAME" --content "$CONTENT" --proxied "$PROXIED")
if [[ -n "$TTL" ]]; then
  args+=(--ttl "$TTL")
fi

exec "$CFPY" "${args[@]}"
