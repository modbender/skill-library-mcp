#!/usr/bin/env bash
set -euo pipefail

UI_DIR="${OPENCLAW_UI_DIR:-$(npm -g root 2>/dev/null)/openclaw/dist/control-ui}"
VOICE_HTTPS_PORT="${VOICE_HTTPS_PORT:-8443}"

systemctl --user is-active openclaw-transcribe.service openclaw-voice-https.service
grep -q 'voice-input.js' "$UI_DIR/index.html" && echo 'inject:ok' || echo 'inject:missing'
curl -sk "https://127.0.0.1:${VOICE_HTTPS_PORT}/chat?session=main" -o /dev/null -w 'https:%{http_code}\n'
echo 'status:done'
