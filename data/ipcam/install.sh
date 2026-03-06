#!/usr/bin/env bash
# IP Camera Skill Installer
# Installs ffmpeg + Python venv with onvif-zeep, creates config template.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$HOME/.config/ipcam"
CONFIG_FILE="$CONFIG_DIR/config.json"

echo "=== ipcam skill installer ==="
echo ""

# ── ffmpeg ────────────────────────────────────────────────────────────────────
echo "Checking ffmpeg..."
if command -v ffmpeg &>/dev/null; then
  echo "  ✓ ffmpeg found"
else
  echo "  Installing ffmpeg..."
  if command -v brew &>/dev/null; then
    brew install ffmpeg
  elif command -v apt-get &>/dev/null; then
    sudo apt-get install -y ffmpeg
  else
    echo "  ✗ Please install ffmpeg manually." >&2; exit 1
  fi
  echo "  ✓ ffmpeg installed"
fi

# ── Python venv ──────────────────────────────────────────────────────────────
VENV_DIR="$SCRIPT_DIR/.venv"
echo ""
echo "Setting up Python venv..."
if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
  echo "  ✓ Created: $VENV_DIR"
else
  echo "  ✓ Exists: $VENV_DIR"
fi
"$VENV_DIR/bin/pip" install --quiet onvif-zeep
echo "  ✓ onvif-zeep installed"

# ── Config ───────────────────────────────────────────────────────────────────
echo ""
echo "Checking config..."
if [[ -f "$CONFIG_FILE" ]]; then
  echo "  ✓ Config exists: $CONFIG_FILE"
  if jq -e 'has("cameras")' "$CONFIG_FILE" >/dev/null 2>&1; then
    jq -r '.cameras | to_entries[] | "    \(.key): \(.value.ip):\(.value.rtsp_port // 554)"' "$CONFIG_FILE"
  fi
else
  mkdir -p "$CONFIG_DIR"
  cat > "$CONFIG_FILE" <<'EOF'
{
  "default": "cam1",
  "cameras": {
    "cam1": {
      "ip": "192.168.1.100",
      "username": "admin",
      "password": "YOUR_PASSWORD",
      "rtsp_port": 554,
      "onvif_port": 2020
    }
  }
}
EOF
  echo "  ✓ Config created: $CONFIG_FILE"
  echo "  ⚠  Edit config to set your camera IP and password."
fi

# ── Permissions ──────────────────────────────────────────────────────────────
chmod +x "$SCRIPT_DIR/scripts/camera.sh" "$SCRIPT_DIR/scripts/ptz.py" 2>/dev/null || true

echo ""
echo "=== Done ==="
echo ""
echo "Quick start:"
echo "  ptz.py discover --add        # scan & add cameras"
echo "  camera.sh snapshot           # take a snapshot"
echo "  ptz.py status                # PTZ position"
echo "  ptz.py stream-uri --save     # auto-detect RTSP paths"
