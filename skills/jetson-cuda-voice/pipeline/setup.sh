#!/usr/bin/env bash
# Jetson CUDA Voice Pipeline — one-command setup
# Usage: bash setup.sh [/path/to/voice_pipeline.py] [OPENROUTER_API_KEY]
#
# Installs systemd user services for whisper-server and voice-pipeline.
# Re-run to update an existing install.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIPELINE="$SCRIPT_DIR/voice_pipeline.py"
API_KEY="${2:-${OPENROUTER_API_KEY:-your-key-here}}"
WHISPER_BIN="${WHISPER_BIN:-$HOME/.local/bin/whisper-server-gpu}"
WHISPER_MODEL="${WHISPER_MODEL:-$HOME/.local/share/whisper/models/ggml-base.bin}"
SYSTEMD_DIR="$HOME/.config/systemd/user"

# Optionally override pipeline path
[[ -n "${1:-}" && -f "$1" ]] && PIPELINE="$1"

echo "📁 Installing to: $SYSTEMD_DIR"
mkdir -p "$SYSTEMD_DIR"

# ── whisper-server.service ─────────────────────────────────────────────────
cat > "$SYSTEMD_DIR/whisper-server.service" << EOF
[Unit]
Description=Whisper STT Server (whisper.cpp CUDA — Jetson)
After=network.target
StartLimitIntervalSec=60
StartLimitBurst=5

[Service]
Type=simple
ExecStart=$WHISPER_BIN \\
    -m $WHISPER_MODEL \\
    --host 127.0.0.1 \\
    --port 8181 \\
    -t 4 \\
    --inference-path /inference \\
    -l auto
Restart=always
RestartSec=5
StandardOutput=append:/tmp/whisper-server.log
StandardError=append:/tmp/whisper-server.log

[Install]
WantedBy=default.target
EOF

# ── voice-pipeline.service ─────────────────────────────────────────────────
cat > "$SYSTEMD_DIR/voice-pipeline.service" << EOF
[Unit]
Description=Jetson CUDA Voice Pipeline (wake word + STT + TTS)
After=sound.target whisper-server.service
Wants=whisper-server.service

[Service]
Type=simple
Environment="OPENROUTER_API_KEY=$API_KEY"
ExecStart=$(command -v python3) $PIPELINE
Restart=always
RestartSec=5
StandardOutput=append:/tmp/voice-pipeline.log
StandardError=append:/tmp/voice-pipeline.log

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable whisper-server voice-pipeline

echo ""
echo "✅ Services installed. Verify paths look correct:"
echo "   Whisper binary : $WHISPER_BIN"
echo "   Whisper model  : $WHISPER_MODEL"
echo "   Pipeline       : $PIPELINE"
echo ""
echo "Then start:"
echo "   bash manage.sh start"
echo ""
echo "📌 Tip — ReSpeaker autosuspend fix (run once as root):"
echo "   sudo tee /etc/udev/rules.d/99-usb-audio-nosuspend.rules << 'UDEV'"
echo "   ACTION==\"add\", SUBSYSTEM==\"usb\", ATTR{idVendor}==\"2886\", ATTR{idProduct}==\"0007\", \\"
echo "     ATTR{power/control}=\"on\", ATTR{power/autosuspend}=\"-1\""
echo "   UDEV"
echo "   sudo udevadm control --reload-rules"
