#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
SKILLS_DIR="${SKILLS_DIR:-$WORKSPACE/skills}"

BACKEND="$SKILLS_DIR/faster-whisper-local-service/scripts/deploy.sh"
PROXY="$SKILLS_DIR/webchat-voice-proxy/scripts/deploy.sh"

if [[ ! -f "$BACKEND" ]]; then
  echo "ERROR: faster-whisper-local-service not found at: $SKILLS_DIR/faster-whisper-local-service" >&2
  echo "Install it first: clawdhub install faster-whisper-local-service" >&2
  exit 2
fi

if [[ ! -f "$PROXY" ]]; then
  echo "ERROR: webchat-voice-proxy not found at: $SKILLS_DIR/webchat-voice-proxy" >&2
  echo "Install it first: clawdhub install webchat-voice-proxy" >&2
  exit 2
fi

echo "=== [full-stack] Step 1/2: Deploy backend (faster-whisper-local-service) ==="
bash "$BACKEND"

echo ""
echo "=== [full-stack] Step 2/2: Deploy proxy (webchat-voice-proxy) ==="
bash "$PROXY"

echo ""
echo "=== [full-stack] Deploy complete ==="
echo ""
echo "Next steps:"
echo "  1. Open https://<your-host>:${VOICE_HTTPS_PORT:-8443}/chat?session=main"
echo "  2. Accept the self-signed certificate"
echo "  3. Approve the pending device if prompted (openclaw devices approve ...)"
echo "  4. Click the mic button and speak"
