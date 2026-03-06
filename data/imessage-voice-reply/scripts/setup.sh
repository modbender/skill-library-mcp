#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$SKILL_DIR/.venv"
KOKORO_DIR="$HOME/.cache/kokoro-onnx"

echo "🎤 Setting up iMessage Voice Reply..."

# Create venv
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

echo "📦 Installing Python dependencies..."
"$VENV_DIR/bin/pip" install -q --upgrade pip
"$VENV_DIR/bin/pip" install -q kokoro-onnx soundfile numpy

# Download Kokoro models
if [ ! -f "$KOKORO_DIR/kokoro-v1.0.onnx" ] || [ ! -f "$KOKORO_DIR/voices-v1.0.bin" ]; then
    echo "🧠 Downloading Kokoro TTS models (~136MB)..."
    mkdir -p "$KOKORO_DIR"
    "$VENV_DIR/bin/python" -c "
from kokoro_onnx import Kokoro
import os
model_dir = os.path.expanduser('~/.cache/kokoro-onnx')
Kokoro(os.path.join(model_dir, 'kokoro-v1.0.onnx'), os.path.join(model_dir, 'voices-v1.0.bin'))
print('Models ready.')
"
else
    echo "✅ Kokoro models already downloaded."
fi

# Check for ffmpeg (needed as fallback on non-macOS)
if ! command -v afconvert &>/dev/null; then
    echo "⚠️  afconvert not found (non-macOS). Checking ffmpeg..."
    if ! command -v ffmpeg &>/dev/null; then
        echo "❌ ffmpeg required on non-macOS. Install: brew install ffmpeg"
        exit 1
    fi
    echo "✅ ffmpeg available (will use as fallback encoder)."
else
    echo "✅ afconvert available (native Apple audio encoder)."
fi

echo ""
echo "✅ Setup complete!"
echo "   Generate voice: $VENV_DIR/bin/python $SCRIPT_DIR/generate_voice_reply.py \"Hello world\""
