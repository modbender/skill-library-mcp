#!/usr/bin/env bash
set -euo pipefail

URL="${WHISPER_HEALTHCHECK_URL:-http://localhost:9000/healthz}"

echo "Checking the privacy-first ASR health endpoint at $URL"
resp="$(curl -fsS "$URL")"
echo "$resp"

echo "$resp" | grep -q '"status":"ok"\|"status": "ok"'
echo "Healthcheck OK - Secure, offline local Whisper service is ready."
