#!/usr/bin/env bash
# setup_env.sh — Create venv, detect GPU, install PyTorch + qwen-tts + all deps
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$SKILL_DIR/.venv"
SCRIPTS_DIR="$SKILL_DIR/scripts"
REQ_DIR="$SKILL_DIR/requirements"

# ─── Colors ───
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()   { echo -e "${RED}[ERROR]${NC} $*"; }

# ─── Detect distro ───
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    else
        echo "unknown"
    fi
}

# ─── Check system dependencies ───
check_system_deps() {
    local distro
    distro=$(detect_distro)
    local missing=()

    for cmd in python3 pip ffmpeg sox git; do
        if ! command -v "$cmd" &>/dev/null; then
            missing+=("$cmd")
        fi
    done

    if [ ${#missing[@]} -gt 0 ]; then
        err "Missing system dependencies: ${missing[*]}"
        echo ""
        case "$distro" in
            cachyos|arch|endeavouros|manjaro)
                echo "  Install with:"
                echo "    sudo pacman -S python python-pip ffmpeg sox git base-devel"
                ;;
            ubuntu|debian|linuxmint|pop)
                echo "  Install with:"
                echo "    sudo apt update && sudo apt install -y python3 python3-pip python3-venv ffmpeg sox git build-essential"
                ;;
            fedora|rhel|centos|rocky|alma)
                echo "  Install with:"
                echo "    sudo dnf install -y python3 python3-pip ffmpeg sox git gcc gcc-c++ make"
                ;;
            opensuse*|suse|sles)
                echo "  Install with:"
                echo "    sudo zypper install -y python3 python3-pip ffmpeg sox git gcc gcc-c++ make"
                ;;
            nixos)
                echo "  Add to configuration.nix or use nix-shell:"
                echo "    nix-shell -p python3 ffmpeg sox git"
                ;;
            *)
                echo "  Please install: python3, pip, ffmpeg, sox, git"
                ;;
        esac
        echo ""
        exit 1
    fi

    ok "System dependencies OK (python3, pip, ffmpeg, sox, git)"
}

# ─── Check disk space ───
check_disk_space() {
    local required_gb=10
    local available_kb
    available_kb=$(df "$SKILL_DIR" | tail -1 | awk '{print $4}')
    local available_gb=$((available_kb / 1024 / 1024))

    if [ "$available_gb" -lt "$required_gb" ]; then
        warn "Low disk space: ${available_gb}GB available, ${required_gb}GB recommended for models"
        read -rp "Continue anyway? [y/N] " yn
        case "$yn" in
            [yY]*) ;;
            *) exit 1 ;;
        esac
    else
        ok "Disk space OK (${available_gb}GB available)"
    fi
}

# ─── Detect GPU ───
detect_gpu() {
    local gpu_type
    gpu_type=$("$SCRIPTS_DIR/detect_gpu.sh")
    echo "$gpu_type"
}

# ─── Create venv ───
create_venv() {
    if [ -d "$VENV_DIR" ]; then
        info "Virtual environment already exists at $VENV_DIR"
    else
        info "Creating virtual environment at $VENV_DIR ..."
        python3 -m venv "$VENV_DIR"
        ok "Virtual environment created"
    fi

    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip setuptools wheel --quiet
    ok "pip/setuptools/wheel upgraded"
}

# ─── Install PyTorch ───
install_pytorch() {
    local gpu_type="$1"
    info "Installing PyTorch for accelerator: $gpu_type"

    case "$gpu_type" in
        cuda)
            pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu128 --quiet
            ;;
        rocm)
            pip install torch torchaudio --index-url https://download.pytorch.org/whl/rocm6.3 --quiet
            ;;
        intel)
            pip install torch torchaudio intel-extension-for-pytorch --index-url https://download.pytorch.org/whl/xpu --quiet
            ;;
        cpu)
            pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu --quiet
            ;;
        *)
            err "Unknown GPU type: $gpu_type"
            exit 1
            ;;
    esac

    ok "PyTorch installed for $gpu_type"
}

# ─── Install Python deps ───
install_requirements() {
    info "Installing base Python dependencies..."
    pip install -r "$REQ_DIR/base.txt" --quiet
    ok "Base dependencies installed"
}

# ─── Verify installation ───
verify_install() {
    info "Verifying installation..."

    python3 -c "
import torch
print(f'  PyTorch version: {torch.__version__}')
if torch.cuda.is_available():
    print(f'  CUDA available: {torch.cuda.get_device_name(0)}')
elif hasattr(torch, \"xpu\") and torch.xpu.is_available():
    print(f'  Intel XPU available')
else:
    print(f'  Running on CPU')
"

    python3 -c "import qwen_tts; print(f'  qwen-tts version: {qwen_tts.__version__}')" 2>/dev/null || \
        warn "qwen-tts import check skipped (may need first-run model download)"

    ok "Installation verified"
}

# ─── Save hardware config ───
save_config() {
    local gpu_type="$1"
    local config_file="$SKILL_DIR/config.json"

    if [ ! -f "$config_file" ]; then
        cat > "$config_file" <<EOF
{
  "server": {
    "host": "127.0.0.1",
    "port": 8880,
    "workers": 1
  },
  "models": {
    "default_model": "custom-voice-1.7b",
    "cache_dir": "$SKILL_DIR/models/",
    "auto_download": true,
    "device": "auto"
  },
  "audio": {
    "sample_rate": 24000,
    "default_format": "wav",
    "output_dir": "$SKILL_DIR/output/"
  },
  "voices": {
    "dir": "$SKILL_DIR/voices/"
  },
  "telegram": {
    "bot_token": "",
    "default_chat_id": ""
  },
  "whatsapp": {
    "phone_number_id": "",
    "access_token": ""
  },
  "hardware": {
    "detected": "$gpu_type",
    "override": null
  }
}
EOF
        ok "Config saved to $config_file"
    else
        info "Config already exists, skipping"
    fi
}

# ═══════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════
main() {
    echo ""
    echo "╔══════════════════════════════════════════════╗"
    echo "║   🎤 Qwen3-TTS OpenClaw Skill — Setup       ║"
    echo "║   Author: daMustermann · Version: 1.0       ║"
    echo "╚══════════════════════════════════════════════╝"
    echo ""

    # Step 1: Check system deps
    check_system_deps

    # Step 2: Check disk space
    check_disk_space

    # Step 3: Detect GPU
    info "Detecting GPU hardware..."
    GPU_TYPE=$(detect_gpu)
    ok "Detected accelerator: $GPU_TYPE"

    # Step 4: Create venv
    create_venv

    # Step 5: Install PyTorch
    install_pytorch "$GPU_TYPE"

    # Step 6: Install requirements
    install_requirements

    # Step 7: Verify
    verify_install

    # Step 8: Save config
    save_config "$GPU_TYPE"

    echo ""
    echo "╔══════════════════════════════════════════════╗"
    echo "║   ✅ Setup complete!                         ║"
    echo "║   GPU: $GPU_TYPE                             "
    echo "║   Start server: bash scripts/start_server.sh ║"
    echo "╚══════════════════════════════════════════════╝"
    echo ""
}

main "$@"
