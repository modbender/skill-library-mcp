#!/usr/bin/env bash
# Parakeet (NeMo) skill setup
# Creates venv and installs NVIDIA NeMo toolkit with ASR support
#
# Usage:
#   ./setup.sh              # Full install
#   ./setup.sh --check      # Verify installation
#   ./setup.sh --update     # Upgrade NeMo toolkit

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

INSTALL_DIARIZE=false

# Parse arguments
for arg in "$@"; do
    case "$arg" in
        --diarize) INSTALL_DIARIZE=true ;;
        --update)
            if [ ! -d "$VENV_DIR" ]; then
                echo "❌ No venv found at $VENV_DIR — run ./setup.sh first"
                exit 1
            fi
            echo "🔄 Upgrading NeMo toolkit and dependencies..."

            # Ensure torch >= 2.6.0 (required by NeMo 2.6+)
            TORCH_CUR=$("$VENV_DIR/bin/python" -c "import torch; print(torch.__version__.split('+')[0])" 2>/dev/null || echo "0.0.0")
            TORCH_NEEDS_UPGRADE=$("$VENV_DIR/bin/python" -c "
from packaging.version import Version
print('yes' if Version('$TORCH_CUR') < Version('2.6.0') else 'no')
" 2>/dev/null || echo "yes")
            if [ "$TORCH_NEEDS_UPGRADE" = "yes" ]; then
                echo "📦 Upgrading PyTorch (NeMo 2.6+ requires torch >= 2.6.0)..."
                HAS_CUDA_UPD=$("$VENV_DIR/bin/python" -c "import torch; print(torch.cuda.is_available())" 2>/dev/null || echo "False")
                if [ "$HAS_CUDA_UPD" = "True" ] || [ -n "$($VENV_DIR/bin/python -c 'import torch; print(torch.version.cuda)' 2>/dev/null)" ]; then
                    if command -v uv &> /dev/null; then
                        uv pip install --python "$VENV_DIR/bin/python" "torch>=2.6.0" torchaudio --index-url https://download.pytorch.org/whl/cu121
                    else
                        "$VENV_DIR/bin/pip" install "torch>=2.6.0" torchaudio --index-url https://download.pytorch.org/whl/cu121
                    fi
                else
                    if command -v uv &> /dev/null; then
                        uv pip install --python "$VENV_DIR/bin/python" "torch>=2.6.0" torchaudio
                    else
                        "$VENV_DIR/bin/pip" install "torch>=2.6.0" torchaudio
                    fi
                fi
            fi

            if command -v uv &> /dev/null; then
                uv pip install --python "$VENV_DIR/bin/python" --upgrade "nemo_toolkit[asr-only]"
            else
                "$VENV_DIR/bin/pip" install --upgrade "nemo_toolkit[asr-only]"
            fi
            echo "✅ NeMo toolkit updated"
            "$VENV_DIR/bin/python" -c "
import importlib.metadata, torch
print(f'nemo_toolkit: {importlib.metadata.version(\"nemo_toolkit\")}')
print(f'torch: {torch.__version__}')
print(f'cuda: {torch.cuda.is_available()}')
" 2>/dev/null || echo "Version check failed"
            exit 0
            ;;
        --check)
            echo "🔍 Parakeet skill system check"
            echo ""

            # Python
            if command -v python3 &>/dev/null; then
                PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")')
                echo "✅ Python: $PY_VER"
            else
                echo "❌ Python: not found"
            fi

            # ffmpeg
            if command -v ffmpeg &>/dev/null; then
                FF_VER=$(ffmpeg -version 2>&1 | head -1 | awk '{print $3}')
                echo "✅ ffmpeg: $FF_VER (format conversion available)"
            else
                echo "⚠️  ffmpeg: not found (needed for mp3/m4a/mp4 conversion)"
            fi

            # GPU/CUDA
            NVIDIA_SMI_CHECK=""
            if command -v nvidia-smi &>/dev/null; then
                NVIDIA_SMI_CHECK="nvidia-smi"
            elif grep -qi microsoft /proc/version 2>/dev/null; then
                for wsl_smi in /usr/lib/wsl/lib/nvidia-smi /usr/lib/wsl/drivers/*/nvidia-smi; do
                    [ -f "$wsl_smi" ] && NVIDIA_SMI_CHECK="$wsl_smi" && break
                done
            fi
            if [ -n "$NVIDIA_SMI_CHECK" ]; then
                GPU_CHECK=$("$NVIDIA_SMI_CHECK" --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)
                DRV_CHECK=$("$NVIDIA_SMI_CHECK" --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -1)
                if [ -n "$GPU_CHECK" ]; then
                    echo "✅ GPU: $GPU_CHECK (driver $DRV_CHECK)"
                else
                    echo "⚠️  GPU: nvidia-smi found but no GPU reported"
                fi
            else
                echo "⚠️  GPU: no NVIDIA GPU detected (CPU mode — will be slow)"
            fi

            # venv
            if [ -d "$VENV_DIR" ]; then
                echo "✅ venv: $VENV_DIR"

                # NeMo toolkit
                if "$VENV_DIR/bin/python" -c "import nemo.collections.asr" 2>/dev/null; then
                    NEMO_VER=$("$VENV_DIR/bin/python" -c "import importlib.metadata; print(importlib.metadata.version('nemo_toolkit'))" 2>/dev/null)
                    echo "✅ nemo_toolkit: $NEMO_VER"
                else
                    echo "❌ nemo_toolkit: not installed (run ./setup.sh)"
                fi

                # CUDA in venv
                CUDA_CHECK=$("$VENV_DIR/bin/python" -c "import torch; print(torch.cuda.is_available())" 2>/dev/null || echo "False")
                TORCH_VER=$("$VENV_DIR/bin/python" -c "import torch; print(torch.__version__)" 2>/dev/null || echo "unknown")
                TORCH_BASE=$(echo "$TORCH_VER" | sed 's/+.*//')
                if [ "$CUDA_CHECK" = "True" ]; then
                    CUDA_DEV=$("$VENV_DIR/bin/python" -c "import torch; print(torch.cuda.get_device_name(0))" 2>/dev/null)
                    echo "✅ CUDA in venv: available ($CUDA_DEV, PyTorch $TORCH_VER)"
                else
                    echo "⚠️  CUDA in venv: not available (CPU mode; check PyTorch CUDA install)"
                fi

                # Torch version check (NeMo 2.6+ needs torch >= 2.6.0)
                TORCH_OK=$("$VENV_DIR/bin/python" -c "
from packaging.version import Version
print('ok' if Version('$TORCH_BASE') >= Version('2.6.0') else 'old')
" 2>/dev/null || echo "unknown")
                if [ "$TORCH_OK" = "old" ]; then
                    echo "⚠️  PyTorch $TORCH_BASE is below 2.6.0 — NeMo 2.6+ requires torch >= 2.6.0"
                    echo "   Run: ./setup.sh --update  or reinstall torch manually"
                fi

                # Model cache check
                MODEL_CACHE="$HOME/.cache/huggingface/hub"
                PARAKEET_CACHED=$(find "$MODEL_CACHE" -type d -name "*parakeet*" 2>/dev/null | head -1)
                if [ -n "$PARAKEET_CACHED" ]; then
                    echo "✅ Model cached: $(basename "$PARAKEET_CACHED")"
                else
                    echo "ℹ️  Model not cached yet (will download on first use, ~1.2GB)"
                fi
            else
                echo "❌ venv: not found (run ./setup.sh)"
            fi

            # yt-dlp
            YTDLP_CHECK=""
            if command -v yt-dlp &>/dev/null; then
                YTDLP_CHECK="yt-dlp"
            elif [ -f "$HOME/.local/share/pipx/venvs/yt-dlp/bin/yt-dlp" ]; then
                YTDLP_CHECK="$HOME/.local/share/pipx/venvs/yt-dlp/bin/yt-dlp"
            fi
            if [ -n "$YTDLP_CHECK" ]; then
                YTDLP_VER=$("$YTDLP_CHECK" --version 2>/dev/null)
                echo "✅ yt-dlp: $YTDLP_VER (URL/YouTube input available)"
            else
                echo "ℹ️  yt-dlp: not installed (URL/YouTube input unavailable; pipx install yt-dlp)"
            fi

            echo ""
            exit 0
            ;;
        --help|-h)
            echo "Usage: ./setup.sh [--diarize] [--check] [--update]"
            echo ""
            echo "Options:"
            echo "  --diarize    Also verify/install NeMo diarization dependencies"
            echo "  --check      Verify system dependencies (GPU, Python, venv, NeMo, ffmpeg)"
            echo "  --update     Upgrade NeMo toolkit in the existing venv"
            exit 0
            ;;
    esac
done

echo "🦜 Setting up Parakeet (NeMo) skill..."

# Detect OS
OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS" in
    Linux*)  OS_TYPE="linux" ;;
    Darwin*) OS_TYPE="macos" ;;
    *)       OS_TYPE="unknown" ;;
esac

echo "✓ Platform: $OS_TYPE ($ARCH)"

# Check for Python 3.10+
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10 or later."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo "❌ Python 3.10+ required (found $PYTHON_VERSION)"
    exit 1
fi

echo "✓ Python $PYTHON_VERSION"

# Check for ffmpeg (recommended for format conversion)
if command -v ffmpeg &> /dev/null; then
    echo "✓ ffmpeg found (format conversion available)"
else
    echo "⚠️  ffmpeg not found — only .wav and .flac files will work natively."
    echo "   Install ffmpeg for mp3/m4a/mp4/ogg support:"
    if [ "$OS_TYPE" = "macos" ]; then
        echo "   brew install ffmpeg"
    else
        echo "   Ubuntu/Debian: sudo apt install ffmpeg"
        echo "   Fedora: sudo dnf install ffmpeg"
        echo "   Arch: sudo pacman -S ffmpeg"
    fi
fi

# Detect GPU
HAS_CUDA=false
GPU_NAME=""
NVIDIA_SMI=""

if [ "$OS_TYPE" = "linux" ]; then
    if command -v nvidia-smi &> /dev/null; then
        NVIDIA_SMI="nvidia-smi"
    else
        if grep -qi microsoft /proc/version 2>/dev/null; then
            for wsl_smi in /usr/lib/wsl/lib/nvidia-smi /usr/lib/wsl/drivers/*/nvidia-smi; do
                if [ -f "$wsl_smi" ]; then
                    NVIDIA_SMI="$wsl_smi"
                    echo "✓ WSL2 detected"
                    break
                fi
            done
        fi
    fi

    if [ -n "$NVIDIA_SMI" ]; then
        GPU_NAME=$($NVIDIA_SMI --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)
        if [ -n "$GPU_NAME" ]; then
            HAS_CUDA=true
        fi
    fi
fi

if [ "$HAS_CUDA" = true ]; then
    echo "✓ GPU detected: $GPU_NAME"
else
    echo "⚠️  No NVIDIA GPU detected. NeMo will use CPU (much slower)."
fi

# Create venv
if [ -d "$VENV_DIR" ]; then
    echo "✓ Virtual environment exists"
else
    echo "Creating virtual environment..."
    if command -v uv &> /dev/null; then
        uv venv "$VENV_DIR" --python python3
    else
        python3 -m venv "$VENV_DIR"
    fi
    echo "✓ Virtual environment created"
fi

# Helper: install with uv or pip
pip_install() {
    if command -v uv &> /dev/null; then
        uv pip install --python "$VENV_DIR/bin/python" "$@"
    else
        "$VENV_DIR/bin/pip" install "$@"
    fi
}

# Upgrade pip if not using uv
if ! command -v uv &> /dev/null; then
    "$VENV_DIR/bin/pip" install --upgrade pip
fi

# Install PyTorch with CUDA support FIRST (before NeMo, to avoid CPU-only torch)
# NeMo 2.6+ requires torch >= 2.6.0
MIN_TORCH_VERSION="2.6.0"

needs_torch_install() {
    local existing
    existing=$("$VENV_DIR/bin/python" -c "import torch; print(torch.__version__.split('+')[0])" 2>/dev/null) || return 0
    "$VENV_DIR/bin/python" -c "
from packaging.version import Version
import sys
sys.exit(0 if Version('$existing') >= Version('$MIN_TORCH_VERSION') else 1)
" 2>/dev/null && return 1 || return 0
}

if [ "$HAS_CUDA" = true ]; then
    echo ""
    echo "🚀 Installing PyTorch with CUDA support..."
    echo "   NeMo 2.6+ requires torch >= $MIN_TORCH_VERSION."
    echo "   This enables GPU-accelerated transcription (~3380x realtime!)."
    echo ""
    if command -v uv &> /dev/null; then
        uv pip install --python "$VENV_DIR/bin/python" "torch>=$MIN_TORCH_VERSION" torchaudio --index-url https://download.pytorch.org/whl/cu121
    else
        "$VENV_DIR/bin/pip" install "torch>=$MIN_TORCH_VERSION" torchaudio --index-url https://download.pytorch.org/whl/cu121
    fi
    echo "✓ PyTorch with CUDA installed"
else
    echo ""
    echo "Installing PyTorch (CPU)..."
    pip_install "torch>=$MIN_TORCH_VERSION" torchaudio
    echo "✓ PyTorch (CPU) installed"
fi

# Install NeMo toolkit + omegaconf from requirements.txt
# requirements.txt uses [asr-only] NOT [asr] — avoids ~19 training-only packages
# (wandb, transformers, datasets, lightning, pandas, peft, etc.)
# Savings: ~400MB fewer packages than [asr]
echo ""
echo "📦 Installing NeMo toolkit (ASR inference)..."
echo "   This may take a few minutes..."
echo ""
pip_install -r "$SCRIPT_DIR/requirements.txt"
echo "✓ NeMo toolkit installed"

# Install diarization dependencies if requested
if [ "$INSTALL_DIARIZE" = true ]; then
    echo ""
    echo "🔊 Installing NeMo diarization dependencies..."
    echo "   NeMo's ClusteringDiarizer uses TitaNet + MarbleNet VAD."
    echo "   These models will be downloaded on first use."
    echo ""
    # pyannote.audio as fallback diarizer
    pip_install pyannote.audio
    echo "✓ pyannote.audio installed (fallback diarizer)"

    # Check for HuggingFace token (needed for pyannote fallback)
    HF_TOKEN_PATH="$HOME/.cache/huggingface/token"
    if [ ! -f "$HF_TOKEN_PATH" ]; then
        echo ""
        echo "⚠️  No HuggingFace token found at $HF_TOKEN_PATH"
        echo "   NeMo diarization works without a token, but pyannote fallback requires:"
        echo "   1. A HuggingFace account and token (huggingface-cli login)"
        echo "   2. Accept: https://hf.co/pyannote/speaker-diarization-3.1"
    else
        echo "✓ HuggingFace token found"
    fi
fi

# Verify CUDA is available in the venv
echo ""
CUDA_VERIFY=$("$VENV_DIR/bin/python" -c "import torch; print(torch.cuda.is_available())" 2>/dev/null || echo "False")
if [ "$CUDA_VERIFY" = "True" ]; then
    CUDA_DEV=$("$VENV_DIR/bin/python" -c "import torch; print(torch.cuda.get_device_name(0))" 2>/dev/null)
    echo "✅ CUDA verified: $CUDA_DEV"
elif [ "$HAS_CUDA" = true ]; then
    echo "⚠️  CUDA was detected but PyTorch can't access it."
    echo "   Try manually installing PyTorch with CUDA:"
    echo "   uv pip install --python $VENV_DIR/bin/python torch torchaudio --index-url https://download.pytorch.org/whl/cu121"
fi

# Verify NeMo installation
NEMO_VERIFY=$("$VENV_DIR/bin/python" -c "import nemo.collections.asr; print('ok')" 2>/dev/null || echo "failed")
if [ "$NEMO_VERIFY" = "ok" ]; then
    NEMO_VER=$("$VENV_DIR/bin/python" -c "import importlib.metadata; print(importlib.metadata.version('nemo_toolkit'))" 2>/dev/null)
    echo "✅ NeMo toolkit verified: $NEMO_VER"
else
    echo "❌ NeMo toolkit installation failed. Check errors above."
    exit 1
fi

# Make scripts executable
chmod +x "$SCRIPT_DIR/scripts/"* 2>/dev/null || true

echo ""
echo "✅ Setup complete!"
echo ""
if [ "$CUDA_VERIFY" = "True" ]; then
    echo "🚀 GPU acceleration enabled — expect blazing-fast transcription"
    echo "   Model only needs ~2GB VRAM (your GPU has plenty of room)"
else
    echo "💻 CPU mode — transcription will work but be slower"
fi
if [ "$INSTALL_DIARIZE" = true ]; then
    echo "🔊 Speaker diarization enabled (--diarize flag)"
fi
echo ""
echo "Usage:"
echo "  $SCRIPT_DIR/scripts/transcribe audio.wav"
echo "  $SCRIPT_DIR/scripts/transcribe audio.mp3 --format srt -o subtitles.srt"
echo "  $SCRIPT_DIR/scripts/transcribe audio.wav --diarize"
echo ""
echo "First run will download the model (~1.2GB for parakeet-tdt-0.6b-v3)."
