#!/usr/bin/env bash
# Qwen3-TTS VoiceDesign — One-click setup
# Tested on: Windows (Git Bash/CMD), Linux, macOS
# Requirements: Python 3.10+, CUDA GPU (4GB+ VRAM), ~4GB disk for model
#
# Usage:
#   bash setup.sh [install_dir]
#   # Default install_dir: ./qwen3-tts
#
# After setup, start the server:
#   bash setup.sh start [install_dir]

set -euo pipefail

ACTION="${1:-install}"
INSTALL_DIR="${2:-${1:-qwen3-tts}}"

# If first arg looks like a path, treat as install
if [[ "$ACTION" == "start" ]]; then
    INSTALL_DIR="${2:-qwen3-tts}"
else
    INSTALL_DIR="${1:-qwen3-tts}"
    ACTION="install"
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$INSTALL_DIR/.venv"

# ---------- Detect OS ----------
detect_python() {
    for cmd in python3 python; do
        if command -v "$cmd" &>/dev/null; then
            echo "$cmd"
            return
        fi
    done
    echo "ERROR: Python not found. Install Python 3.10+" >&2
    exit 1
}

# ---------- Install ----------
do_install() {
    echo "=== Qwen3-TTS VoiceDesign Setup ==="
    echo "Install dir: $INSTALL_DIR"
    echo ""

    PYTHON=$(detect_python)
    PY_VER=$($PYTHON --version 2>&1)
    echo "Python: $PYTHON ($PY_VER)"

    # Create install dir
    mkdir -p "$INSTALL_DIR"

    # Create venv
    if [[ ! -d "$VENV_DIR" ]]; then
        echo "Creating virtual environment..."
        $PYTHON -m venv "$VENV_DIR"
    fi

    # Activate venv
    if [[ -f "$VENV_DIR/bin/activate" ]]; then
        source "$VENV_DIR/bin/activate"
    elif [[ -f "$VENV_DIR/Scripts/activate" ]]; then
        source "$VENV_DIR/Scripts/activate"
    fi

    # Install dependencies
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install qwen-tts soundfile pydub uvicorn fastapi numpy

    # Install PyTorch with CUDA (if not already)
    if ! python -c "import torch; assert torch.cuda.is_available()" 2>/dev/null; then
        echo "Installing PyTorch with CUDA..."
        pip install torch --index-url https://download.pytorch.org/whl/cu128
    fi

    # Download model (via modelscope for China, huggingface otherwise)
    echo ""
    echo "Downloading VoiceDesign model (~3.5GB)..."
    echo "Trying ModelScope first (faster in China)..."
    if pip install modelscope 2>/dev/null && python -c "
from modelscope import snapshot_download
path = snapshot_download('Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign')
print(f'Model downloaded to: {path}')
" 2>/dev/null; then
        echo "Model downloaded via ModelScope ✓"
    else
        echo "ModelScope failed, trying HuggingFace..."
        python -c "
from qwen_tts import Qwen3TTSModel
m = Qwen3TTSModel.from_pretrained('Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign')
print('Model downloaded via HuggingFace ✓')
del m
"
    fi

    # Copy server script
    cp "$SCRIPT_DIR/tts_server.py" "$INSTALL_DIR/tts_server.py"
    cp "$SCRIPT_DIR/batch_seeds.sh" "$INSTALL_DIR/batch_seeds.sh" 2>/dev/null || true

    # Create .env template
    if [[ ! -f "$INSTALL_DIR/.env" ]]; then
        cat > "$INSTALL_DIR/.env" << 'ENVEOF'
# Qwen3-TTS Configuration
# Uncomment and edit as needed

# TTS_SEED=4096
# TTS_INSTRUCT=18岁温柔女大学生，声音柔和温暖...
# TTS_MODEL_PATH=Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign
# TTS_PORT=8881
# TTS_HOST=0.0.0.0
ENVEOF
    fi

    echo ""
    echo "=== Setup complete! ==="
    echo ""
    echo "To start the server:"
    echo "  cd $INSTALL_DIR"
    echo "  source .venv/bin/activate   # or .venv\\Scripts\\activate on Windows"
    echo "  python tts_server.py"
    echo ""
    echo "Or configure via environment:"
    echo "  TTS_SEED=201 TTS_PORT=8881 python tts_server.py"
    echo ""
    echo "Test:"
    echo "  curl 'http://localhost:8881/tts?text=你好' -o test.mp3"
}

# ---------- Start ----------
do_start() {
    if [[ -f "$VENV_DIR/bin/activate" ]]; then
        source "$VENV_DIR/bin/activate"
    elif [[ -f "$VENV_DIR/Scripts/activate" ]]; then
        source "$VENV_DIR/Scripts/activate"
    else
        echo "ERROR: venv not found at $VENV_DIR. Run setup first." >&2
        exit 1
    fi

    # Load .env if exists
    if [[ -f "$INSTALL_DIR/.env" ]]; then
        set -a
        source "$INSTALL_DIR/.env"
        set +a
    fi

    echo "Starting Qwen3-TTS server on port ${TTS_PORT:-8881}..."
    python "$INSTALL_DIR/tts_server.py"
}

# ---------- Main ----------
case "$ACTION" in
    install) do_install ;;
    start)   do_start ;;
    *)       do_install ;;
esac
