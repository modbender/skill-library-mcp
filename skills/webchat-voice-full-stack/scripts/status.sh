#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
SKILLS_DIR="${SKILLS_DIR:-$WORKSPACE/skills}"

BACKEND_STATUS="$SKILLS_DIR/faster-whisper-local-service/scripts/status.sh"
PROXY_STATUS="$SKILLS_DIR/webchat-voice-proxy/scripts/status.sh"

echo "=== [full-stack] Backend status ==="
if [[ -f "$BACKEND_STATUS" ]]; then
  bash "$BACKEND_STATUS"
else
  echo "  faster-whisper-local-service not installed."
fi

echo ""
echo "=== [full-stack] Proxy status ==="
if [[ -f "$PROXY_STATUS" ]]; then
  bash "$PROXY_STATUS"
else
  echo "  webchat-voice-proxy not installed."
fi

echo ""
echo "=== [full-stack] status:done ==="
