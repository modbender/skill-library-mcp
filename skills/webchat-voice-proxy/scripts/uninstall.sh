#!/usr/bin/env bash
# Uninstall webchat-voice-proxy: removes service, hook, UI injection, gateway origin
set -euo pipefail

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
VOICE_DIR="$WORKSPACE/voice-input"
UI_DIR="${OPENCLAW_UI_DIR:-$(npm -g root 2>/dev/null)/openclaw/dist/control-ui}"
INDEX="$UI_DIR/index.html"
ASSET_DIR="$UI_DIR/assets"
CFG="${OPENCLAW_CONFIG_PATH:-$HOME/.openclaw/openclaw.json}"
VOICE_HTTPS_PORT="${VOICE_HTTPS_PORT:-8443}"
HOOK_DIR="$HOME/.openclaw/hooks/voice-input-inject"

echo "=== Uninstalling webchat-voice-proxy ==="

# 1) Stop and remove systemd service
echo "[1/5] Stopping and removing openclaw-voice-https.service..."
systemctl --user stop openclaw-voice-https.service 2>/dev/null || true
systemctl --user disable openclaw-voice-https.service 2>/dev/null || true
rm -f "$HOME/.config/systemd/user/openclaw-voice-https.service"
systemctl --user daemon-reload 2>/dev/null || true
echo "      done."

# 2) Remove gateway startup hook
echo "[2/5] Removing gateway hook..."
if [[ -d "$HOOK_DIR" ]]; then
  rm -rf "$HOOK_DIR"
  echo "      removed: $HOOK_DIR"
else
  echo "      not found (skipped)."
fi

# 3) Remove voice-input.js from Control UI and undo index.html injection
echo "[3/5] Reverting Control UI..."
if [[ -f "$ASSET_DIR/voice-input.js" ]]; then
  rm -f "$ASSET_DIR/voice-input.js"
  echo "      removed: voice-input.js asset"
fi

if [[ -f "$INDEX" ]] && grep -q 'voice-input.js' "$INDEX"; then
  sed -i '/voice-input\.js/d' "$INDEX"
  echo "      removed script tag from index.html"
else
  echo "      index.html clean (skipped)."
fi

# 4) Remove HTTPS origin from gateway config
echo "[4/5] Cleaning gateway config (allowedOrigins)..."
if [[ -f "$CFG" ]]; then
  python3 - "$CFG" "$VOICE_HTTPS_PORT" << 'PY'
import json, sys
p, port = sys.argv[1], sys.argv[2]
with open(p, 'r', encoding='utf-8') as f:
    c = json.load(f)
g = c.get('gateway', {})
cu = g.get('controlUi', {})
orig = cu.get('allowedOrigins', [])
before = len(orig)
cu['allowedOrigins'] = [o for o in orig if f':{port}' not in o]
after = len(cu['allowedOrigins'])
with open(p, 'w', encoding='utf-8') as f:
    json.dump(c, f, indent=2, ensure_ascii=False)
    f.write('\n')
print(f'      removed {before - after} origin(s) from allowedOrigins')
PY
else
  echo "      config not found (skipped)."
fi

# 5) Restart gateway to apply changes
echo "[5/5] Restarting gateway..."
openclaw gateway restart >/dev/null 2>&1 || true
echo "      done."

# 6) Remove TLS certs
echo "[6/7] Removing TLS certificates..."
CERT_DIR="$VOICE_DIR/certs"
if [[ -d "$CERT_DIR" ]]; then
  rm -rf "$CERT_DIR"
  echo "      removed: $CERT_DIR"
else
  echo "      not found (skipped)."
fi

# 7) Remove workspace runtime files (voice-input.js, https-server.py, i18n.json)
echo "[7/7] Removing workspace runtime files..."
for f in voice-input.js https-server.py i18n.json; do
  rm -f "$VOICE_DIR/$f"
done
# Remove dir if empty
rmdir "$VOICE_DIR" 2>/dev/null && echo "      removed: $VOICE_DIR" || echo "      $VOICE_DIR not empty, kept."

echo ""
echo "=== Uninstall complete ==="
echo ""
echo "The faster-whisper backend (openclaw-transcribe.service) was NOT touched."
echo "To remove it too, uninstall faster-whisper-local-service separately."
