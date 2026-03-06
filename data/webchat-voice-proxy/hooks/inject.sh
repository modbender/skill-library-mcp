#!/usr/bin/env bash
# Inject voice-input.js into OpenClaw Control UI (idempotent, portable)
set -euo pipefail

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
SRC="$WORKSPACE/voice-input/voice-input.js"

# Find Control UI dir
UI_DIR="${OPENCLAW_UI_DIR:-$(npm -g root 2>/dev/null)/openclaw/dist/control-ui}"
ASSET_DIR="$UI_DIR/assets"
INDEX="$UI_DIR/index.html"
MARKER='voice-input.js'

if [[ ! -f "$SRC" ]]; then
  echo "[voice-input-inject] Source not found: $SRC" >&2
  exit 1
fi

if [[ ! -f "$INDEX" ]]; then
  echo "[voice-input-inject] Control UI index not found: $INDEX" >&2
  exit 1
fi

cp -f "$SRC" "$ASSET_DIR/voice-input.js"

if ! grep -q "$MARKER" "$INDEX" 2>/dev/null; then
  # SECURITY: sed uses only hardcoded strings — no variable interpolation.
  sed -i 's|</body>|    <script src="./assets/voice-input.js"></script>\n  </body>|' "$INDEX"
  echo "[voice-input-inject] Injected into $INDEX"
else
  echo "[voice-input-inject] Already present in $INDEX"
fi
