#!/bin/bash
# port-check.sh — Check if services are responding on given host:port pairs
# Usage: port-check.sh host:port [host:port ...] [--timeout N] [--http]
# Example: port-check.sh localhost:8080 localhost:5432 192.168.1.1:80 --http

set -euo pipefail

TIMEOUT=3
HTTP=false
TARGETS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --timeout) TIMEOUT="$2"; shift 2 ;;
    --http) HTTP=true; shift ;;
    --help|-h)
      echo "Usage: port-check.sh host:port [...] [--timeout N] [--http]"
      echo "  --timeout N  Connection timeout in seconds (default: 3)"
      echo "  --http       Also check HTTP status code for web services"
      exit 0 ;;
    *) TARGETS+=("$1"); shift ;;
  esac
done

if [[ ${#TARGETS[@]} -eq 0 ]]; then
  echo "Error: No targets specified" >&2
  echo "Usage: port-check.sh host:port [host:port ...]" >&2
  exit 1
fi

OK=0
FAIL=0

for target in "${TARGETS[@]}"; do
  host="${target%%:*}"
  port="${target##*:}"
  
  if [[ "$host" == "$port" ]]; then
    echo "  ❌ $target — invalid format (use host:port)" >&2
    ((FAIL++))
    continue
  fi
  
  # TCP check
  if nc -z -w "$TIMEOUT" "$host" "$port" 2>/dev/null; then
    if $HTTP; then
      # HTTP status check
      STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout "$TIMEOUT" "http://${host}:${port}/" 2>/dev/null || echo "000")
      if [[ "$STATUS" =~ ^[23] ]]; then
        echo "  ✅ $target — open (HTTP $STATUS)"
      else
        echo "  ⚠️  $target — open but HTTP $STATUS"
      fi
    else
      echo "  ✅ $target — open"
    fi
    ((OK++))
  else
    echo "  ❌ $target — closed/timeout"
    ((FAIL++))
  fi
done

echo ""
echo "Results: $OK up, $FAIL down (of $((OK+FAIL)) checked)"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
