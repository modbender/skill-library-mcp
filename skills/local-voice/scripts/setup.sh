#!/bin/bash
# StellaVoice Setup Script
# Builds and installs the local TTS/STT daemon

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
INSTALL_DIR="${HOME}/clawd/bin"
PLIST_DIR="${HOME}/Library/LaunchAgents"
LOG_DIR="${HOME}/.clawdbot/logs"

echo "🚀 StellaVoice Setup"
echo "===================="

# Check architecture
if [[ "$(uname -m)" != "arm64" ]]; then
    echo "❌ Error: This must run on Apple Silicon (arm64)"
    echo "   Current: $(uname -m)"
    exit 1
fi

# Check for espeak-ng
if ! command -v espeak-ng &> /dev/null; then
    echo "📦 Installing espeak-ng..."
    brew install espeak-ng
fi

# Create directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$LOG_DIR"

# Build
echo "🔨 Building StellaVoice..."
cd "$SKILL_DIR/sources"
swift build -c release

# Install binary
echo "📁 Installing binary..."
cp .build/release/StellaVoice "$INSTALL_DIR/"

# Install framework
if [[ -d ".build/arm64-apple-macosx/release/ESpeakNG.framework" ]]; then
    rm -rf "$INSTALL_DIR/ESpeakNG.framework"
    cp -R .build/arm64-apple-macosx/release/ESpeakNG.framework "$INSTALL_DIR/"
fi

# Fix rpath
install_name_tool -add_rpath @executable_path "$INSTALL_DIR/StellaVoice" 2>/dev/null || true

# Create LaunchAgent
echo "⚙️  Creating LaunchAgent..."
cat > "$PLIST_DIR/com.stella.voice.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.stella.voice</string>
    <key>ProgramArguments</key>
    <array>
        <string>${INSTALL_DIR}/StellaVoice</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>HOME</key>
        <string>${HOME}</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>${LOG_DIR}/stella-voice.log</string>
    <key>StandardErrorPath</key>
    <string>${LOG_DIR}/stella-voice.err.log</string>
    <key>WorkingDirectory</key>
    <string>${HOME}</string>
</dict>
</plist>
EOF

# Load service
echo "🔄 Loading service..."
launchctl unload "$PLIST_DIR/com.stella.voice.plist" 2>/dev/null || true
launchctl load "$PLIST_DIR/com.stella.voice.plist"

# Wait for startup
echo "⏳ Waiting for models to load (~15s)..."
sleep 15

# Test
if curl -s http://127.0.0.1:18790/health | grep -q "ok"; then
    echo ""
    echo "✅ StellaVoice is running!"
    echo ""
    echo "API Endpoints:"
    echo "  POST http://127.0.0.1:18790/synthesize  - TTS"
    echo "  POST http://127.0.0.1:18790/transcribe  - STT"
    echo "  GET  http://127.0.0.1:18790/health      - Health"
    echo ""
    echo "Test TTS:"
    echo "  curl -X POST http://127.0.0.1:18790/synthesize -d 'Hello!' -o test.wav"
else
    echo "❌ Service failed to start. Check logs:"
    echo "  tail -f $LOG_DIR/stella-voice.err.log"
    exit 1
fi
