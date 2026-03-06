#!/usr/bin/env bash
# Create and configure the audio-speaker-tools virtual environment.
#
# This script creates a venv with all required dependencies for:
# - Speaker diarization (pyannote, demucs)
# - Voice comparison (resemblyzer)
# - Audio processing (pydub, ffmpeg)
#
# Usage:
#   bash setup_venv.sh [venv_path]
#
# Default venv path: ./.venv
#
# Requirements:
# - Python 3.9+
# - ffmpeg (brew install ffmpeg)

set -euo pipefail

VENV_PATH="${1:-./.venv}"

echo "Setting up audio-speaker-tools venv at: $VENV_PATH"

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found in PATH" >&2
    exit 1
fi

# Check for ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "Error: ffmpeg not found. Install with: brew install ffmpeg" >&2
    exit 1
fi

# Create venv if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating venv..."
    python3 -m venv "$VENV_PATH"
else
    echo "Venv already exists at $VENV_PATH"
fi

# Activate venv
source "$VENV_PATH/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --quiet --upgrade pip

# Install PyTorch with MPS support (Metal Performance Shaders for Apple Silicon)
echo "Installing PyTorch with MPS support..."
pip install --quiet torch torchvision torchaudio

# Install audio processing libraries
echo "Installing audio processing libraries..."
pip install --quiet \
    demucs \
    pyannote.audio \
    pydub \
    resemblyzer \
    librosa

echo ""
echo "✓ Setup complete!"
echo ""
echo "Venv path: $VENV_PATH"
echo ""
echo "To activate:"
echo "  source $VENV_PATH/bin/activate"
echo ""
echo "To use with scripts:"
echo "  $VENV_PATH/bin/python scripts/diarize_and_slice_mps.py --help"
echo "  $VENV_PATH/bin/python scripts/compare_voices.py --help"
echo ""
echo "Required env var for diarization:"
echo "  export HF_TOKEN=<your-token>"
