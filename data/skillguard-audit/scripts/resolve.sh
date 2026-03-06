#!/bin/bash
# Resolve SkillGuard API URL
# The canonical identity is skillguard.base.eth
# This script checks known endpoints for availability

ENDPOINTS=(
  "https://studio-designed-normal-atomic.trycloudflare.com"
)

for url in "${ENDPOINTS[@]}"; do
  if curl -s --max-time 5 "$url/health" | grep -q '"status":"ok"'; then
    echo "$url"
    exit 0
  fi
done

echo "ERROR: SkillGuard API not reachable. The tunnel URL may have changed." >&2
echo "Check skillguard.base.eth for the latest endpoint." >&2
exit 1
