#!/usr/bin/env bash
set -euo pipefail

# Patch OpenClaw config to use local whisper.cpp wrapper for inbound audio STT.
# Uses `openclaw config set` (works with the current CLI).

WRAPPER_PATH="${WRAPPER_PATH:-$HOME/.local/bin/openclaw-whisper-stt}"

if [ ! -x "$WRAPPER_PATH" ]; then
  echo "Wrapper not found or not executable: $WRAPPER_PATH" >&2
  exit 2
fi

if ! command -v openclaw >/dev/null 2>&1; then
  echo "openclaw CLI not found on PATH" >&2
  exit 3
fi

echo "==> Setting tools.media.audio to use local whisper.cpp wrapper"

openclaw config set tools.media.audio.enabled true
openclaw config set tools.media.audio.maxBytes 20971520
openclaw config set --strict-json tools.media.audio.models "[
  {
    \"type\": \"cli\",
    \"command\": \"$WRAPPER_PATH\",
    \"args\": [\"{{MediaPath}}\"],
    \"timeoutSeconds\": 120
  }
]"

echo "==> Restarting gateway to apply config"
openclaw gateway restart >/dev/null

echo "[OK] Patched + restarted. Send a voice note to test."
