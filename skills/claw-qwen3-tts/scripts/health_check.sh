#!/usr/bin/env bash
# health_check.sh — Check if the Qwen3-TTS server is alive
set -euo pipefail

PORT="${TTS_PORT:-8880}"
HOST="${TTS_HOST:-127.0.0.1}"
URL="http://${HOST}:${PORT}/health"

response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "$URL" 2>/dev/null || echo "000")

case "$response" in
    200)
        echo "[OK] Server is healthy at $URL"
        exit 0
        ;;
    000)
        echo "[ERROR] Server is not reachable at $URL"
        exit 1
        ;;
    *)
        echo "[ERROR] Server returned HTTP $response at $URL"
        exit 1
        ;;
esac
