#!/usr/bin/env bash
set -euo pipefail

URL="${PARAKEET_URL:-http://localhost:9001/health}"

echo "Checking $URL"
resp="$(curl -fsS "$URL")"
echo "$resp"

echo "$resp" | grep -q '"status":"healthy"\|"status": "healthy"'
echo "Healthcheck OK"
