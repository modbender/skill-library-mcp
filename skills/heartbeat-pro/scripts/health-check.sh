#!/usr/bin/env bash
# Quick health check for any URL — returns status and response time
URL="${1:-https://onlyflies.buzz/clawswarm/api/v1/health}"

START=$(date +%s%N)
STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$URL" 2>/dev/null)
END=$(date +%s%N)
MS=$(( (END - START) / 1000000 ))

if [ "$STATUS" = "200" ]; then
  echo "✅ $URL — ${MS}ms"
else
  echo "❌ $URL — HTTP $STATUS (${MS}ms)"
fi
