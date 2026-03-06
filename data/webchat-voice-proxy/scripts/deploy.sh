#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
VOICE_DIR="$WORKSPACE/voice-input"
UI_DIR="${OPENCLAW_UI_DIR:-$(npm -g root 2>/dev/null)/openclaw/dist/control-ui}"
INDEX="$UI_DIR/index.html"
ASSET_DIR="$UI_DIR/assets"
CFG="${OPENCLAW_CONFIG_PATH:-$HOME/.openclaw/openclaw.json}"
VOICE_HTTPS_PORT="${VOICE_HTTPS_PORT:-8443}"
VOICE_HOST="${VOICE_HOST:-}"

# --- Input validation (injection prevention) ---
# All env-var inputs are validated before use in sed, python, or systemd units.
if ! [[ "$VOICE_HTTPS_PORT" =~ ^[0-9]+$ ]] || (( VOICE_HTTPS_PORT < 1 || VOICE_HTTPS_PORT > 65535 )); then
  echo "ERROR: VOICE_HTTPS_PORT must be a valid port (1-65535), got: $VOICE_HTTPS_PORT" >&2
  exit 1
fi

# SECURITY: Default to localhost (127.0.0.1) so the proxy is NOT exposed to the
# local network.  Only when the user explicitly sets VOICE_HOST to a LAN IP will
# the proxy bind externally.  This is intentional — exposing the HTTPS proxy on
# a LAN IP means any device on the same network can reach it.
if [[ -z "$VOICE_HOST" ]]; then
  VOICE_HOST="127.0.0.1"
fi

# SECURITY: host must be IP or hostname — reject shell metacharacters, sed
# delimiters, and quotes to prevent injection in sed/systemd/python contexts.
if ! [[ "$VOICE_HOST" =~ ^[a-zA-Z0-9._-]+$ ]]; then
  echo "ERROR: VOICE_HOST contains invalid characters: $VOICE_HOST" >&2
  exit 1
fi

ALLOWED_ORIGIN="https://${VOICE_HOST}:${VOICE_HTTPS_PORT}"

mkdir -p "$VOICE_DIR"

# 0) Language selection
VOICE_LANG="${VOICE_LANG:-}"
if [[ -z "$VOICE_LANG" ]] && [[ -t 0 ]]; then
  echo ""
  echo "Available UI languages: auto (browser default), en, de, zh"
  read -r -p "Choose UI language [auto]: " VOICE_LANG
fi
VOICE_LANG="${VOICE_LANG:-auto}"

# SECURITY: lang is interpolated into sed replacement — strict allowlist prevents
# injection via crafted language codes (only lowercase alpha + 'auto' allowed).
if ! [[ "$VOICE_LANG" =~ ^([a-zA-Z]{2,5}(-[a-zA-Z]{2,5})?|auto)$ ]]; then
  echo "ERROR: VOICE_LANG must be a language code (en, de, en-US, zh) or 'auto', got: $VOICE_LANG" >&2
  exit 1
fi

# 1) Copy bundled assets from skill -> workspace runtime dir
cp -f "$SKILL_DIR/assets/voice-input.js" "$VOICE_DIR/voice-input.js"
cp -f "$SKILL_DIR/assets/https-server.py" "$VOICE_DIR/https-server.py"
cp -f "$SKILL_DIR/assets/i18n.json" "$VOICE_DIR/i18n.json" 2>/dev/null || true

# Patch default language into voice-input.js if not auto
if [[ "$VOICE_LANG" != "auto" && -n "$VOICE_LANG" ]]; then
  # Insert a line after LANG_KEY that sets the default
  sed -i "/const LANG_KEY = 'oc-voice-lang';/a\\
  const DEFAULT_LANG = '${VOICE_LANG}';" "$VOICE_DIR/voice-input.js"
  # Patch getLang to use DEFAULT_LANG
  sed -i "s|const nav = (navigator.language || 'en').slice(0, 2);|const nav = DEFAULT_LANG || (navigator.language || 'en').slice(0, 2);|" "$VOICE_DIR/voice-input.js"
  echo "UI language set to: ${VOICE_LANG}"
else
  echo "UI language: auto-detect (browser default)"
fi

# 2) Deploy voice-input asset + inject index (idempotent)
mkdir -p "$ASSET_DIR"
cp -f "$VOICE_DIR/voice-input.js" "$ASSET_DIR/voice-input.js"

if ! grep -q 'voice-input.js' "$INDEX"; then
  sed -i 's|</body>|    <script src="./assets/voice-input.js"></script>\n  </body>|' "$INDEX"
fi

# 3) Ensure gateway allowedOrigins contains computed origin
python3 - "$CFG" "$ALLOWED_ORIGIN" << 'PY'
import json, sys
p, origin = sys.argv[1], sys.argv[2]
with open(p, 'r', encoding='utf-8') as f:
    c = json.load(f)
g = c.setdefault('gateway', {})
cu = g.setdefault('controlUi', {})
orig = cu.setdefault('allowedOrigins', [])
if origin not in orig:
    orig.append(origin)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(c, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(f'allowedOrigin ensured: {origin}')
PY

# 4) Install/refresh HTTPS proxy service
# Find python with aiohttp: prefer venv if exists, else system python3
PYTHON_BIN=""
if [[ -x "${WORKSPACE}/.venv-faster-whisper/bin/python" ]]; then
  PYTHON_BIN="${WORKSPACE}/.venv-faster-whisper/bin/python"
elif python3 -c "import aiohttp" 2>/dev/null; then
  PYTHON_BIN="$(command -v python3)"
else
  echo "ERROR: No python with aiohttp found. Install aiohttp: pip3 install 'aiohttp>=3.9.0'" >&2
  exit 1
fi

# Verify minimum aiohttp version (>=3.9.0)
AIOHTTP_VERSION=$("$PYTHON_BIN" -c "import aiohttp; print(aiohttp.__version__)" 2>/dev/null || echo "0.0.0")
AIOHTTP_MAJOR=$(echo "$AIOHTTP_VERSION" | cut -d. -f1)
AIOHTTP_MINOR=$(echo "$AIOHTTP_VERSION" | cut -d. -f2)
if (( AIOHTTP_MAJOR < 3 )) || (( AIOHTTP_MAJOR == 3 && AIOHTTP_MINOR < 9 )); then
  echo "ERROR: aiohttp >= 3.9.0 required, found $AIOHTTP_VERSION. Upgrade: pip3 install 'aiohttp>=3.9.0'" >&2
  exit 1
fi

mkdir -p "$HOME/.config/systemd/user"
cat > "$HOME/.config/systemd/user/openclaw-voice-https.service" <<UNIT
[Unit]
Description=OpenClaw Voice HTTPS Proxy (Control UI + WS + Transcribe)
After=network.target

[Service]
Type=simple
ExecStart=${PYTHON_BIN} ${VOICE_DIR}/https-server.py
Restart=always
RestartSec=2
Environment=WORKSPACE=${WORKSPACE}
Environment=VOICE_HTTPS_PORT=${VOICE_HTTPS_PORT}
Environment=VOICE_ALLOWED_ORIGIN=${ALLOWED_ORIGIN}
Environment=VOICE_BIND_HOST=${VOICE_HOST}

[Install]
WantedBy=default.target
UNIT

systemctl --user daemon-reload
systemctl --user enable --now openclaw-voice-https.service
systemctl --user restart openclaw-voice-https.service

# 5) Install gateway startup hook (survives openclaw update)
HOOK_DIR="$HOME/.openclaw/hooks/voice-input-inject"
mkdir -p "$HOOK_DIR"
cp -f "$SKILL_DIR/hooks/handler.ts" "$HOOK_DIR/handler.ts"
cp -f "$SKILL_DIR/hooks/inject.sh" "$HOOK_DIR/inject.sh"
cp -f "$SKILL_DIR/hooks/HOOK.md" "$HOOK_DIR/HOOK.md"
chmod +x "$HOOK_DIR/inject.sh"
echo "hook installed: $HOOK_DIR"

# 6) Restart gateway so allowedOrigins/injection hook applies cleanly
openclaw gateway restart >/dev/null 2>&1 || true

echo "deploy:ok host=${VOICE_HOST} port=${VOICE_HTTPS_PORT} origin=${ALLOWED_ORIGIN}"
