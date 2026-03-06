#!/usr/bin/env bash
# Super-Transcribe — First-time setup
# Detects your system, checks prerequisites, and installs the best backend(s).
#
# Usage:
#   ./setup.sh                # Auto-detect system and install recommended backend
#   ./setup.sh --all          # Install both backends
#   ./setup.sh --backend fw   # Install only faster-whisper
#   ./setup.sh --backend pk   # Install only Parakeet
#   ./setup.sh --diarize      # Also install speaker diarization deps
#   ./setup.sh --check        # Check prerequisites only, don't install
#   ./setup.sh --help         # Show this help

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR/scripts"
TRANSCRIBE="$SCRIPTS_DIR/transcribe"

# ── Colors (safe for non-TTY) ─────────────────────────────────────────
if [ -t 1 ]; then
    BOLD='\033[1m' DIM='\033[2m' RED='\033[31m' GREEN='\033[32m'
    YELLOW='\033[33m' CYAN='\033[36m' RESET='\033[0m'
else
    BOLD='' DIM='' RED='' GREEN='' YELLOW='' CYAN='' RESET=''
fi

ok()   { printf "  ${GREEN}✅${RESET} %s\n" "$*"; }
warn() { printf "  ${YELLOW}⚠️${RESET}  %s\n" "$*"; }
err()  { printf "  ${RED}❌${RESET} %s\n" "$*"; }
info() { printf "  ${CYAN}ℹ️${RESET}  %s\n" "$*"; }
step() { printf "\n${BOLD}%s${RESET}\n" "$*"; }

# ── Parse args ────────────────────────────────────────────────────────
INSTALL_BACKEND=""   # empty = auto-detect
INSTALL_ALL=false
INSTALL_DIARIZE=false
CHECK_ONLY=false

usage() {
    cat <<'EOF'
🎙️ Super-Transcribe Setup

Detects your system, checks prerequisites, and installs the best backend.

💡 TIP: For a fully automated setup (deps + backends in one command):
    ./scripts/transcribe --quickstart

USAGE:
    ./setup.sh                   Auto-detect and install recommended backend
    ./setup.sh --all             Install both backends (faster-whisper + Parakeet)
    ./setup.sh --backend fw      Install only faster-whisper
    ./setup.sh --backend pk      Install only Parakeet
    ./setup.sh --diarize         Also install speaker diarization dependencies
    ./setup.sh --check           Check prerequisites only (no install)
    ./setup.sh --help            Show this help

PREREQUISITES:
    Required:   Python 3.10+
    Recommended: NVIDIA GPU + CUDA drivers (CPU is 50-100× slower)
    Optional:    ffmpeg (audio format conversion, required for mp3/m4a/mp4)
                 yt-dlp (YouTube/URL downloads)
                 HuggingFace token (for pyannote diarization with faster-whisper)

WHICH BACKEND?
    Parakeet:       Best accuracy, fastest (3380× realtime), auto-punctuation.
                    Needs NVIDIA GPU. Supports 25 European languages.
    faster-whisper: Good accuracy, fast (20× realtime). 99+ languages,
                    translation, initial prompting. Works on CPU & macOS.

    If unsure, just run ./setup.sh — it picks the best option for your system.
EOF
    exit 0
}

while [ $# -gt 0 ]; do
    case "$1" in
        --help|-h) usage ;;
        --check)   CHECK_ONLY=true ;;
        --all)     INSTALL_ALL=true ;;
        --diarize) INSTALL_DIARIZE=true ;;
        --backend)
            [ $# -ge 2 ] || { err "--backend needs a value: fw | pk | faster-whisper | parakeet"; exit 1; }
            INSTALL_BACKEND="$2"; shift
            ;;
        --backend=*) INSTALL_BACKEND="${1#--backend=}" ;;
        *) err "Unknown option: $1"; echo "Run ./setup.sh --help for usage."; exit 1 ;;
    esac
    shift
done

# Normalize backend name
normalize_backend() {
    case "$1" in
        faster-whisper|fw|whisper) echo "faster-whisper" ;;
        parakeet|pk|nemo)          echo "parakeet" ;;
        *)                         echo "" ;;
    esac
}

if [ -n "$INSTALL_BACKEND" ]; then
    INSTALL_BACKEND=$(normalize_backend "$INSTALL_BACKEND")
    [ -n "$INSTALL_BACKEND" ] || { err "Unknown backend. Choose: fw | pk | faster-whisper | parakeet"; exit 1; }
fi

# ── System detection ──────────────────────────────────────────────────
step "🔍 Checking system..."

OS="$(uname -s)"
ARCH="$(uname -m)"
IS_WSL=false
IS_MACOS=false
HAS_CUDA=false
HAS_APPLE_SILICON=false
GPU_NAME=""
PYTHON_OK=false
FFMPEG_OK=false
YTDLP_OK=false
HF_TOKEN_OK=false

# OS detection
case "$OS" in
    Linux*)
        if grep -qi microsoft /proc/version 2>/dev/null; then
            IS_WSL=true
            ok "Platform: WSL2 on Windows ($ARCH)"
        else
            ok "Platform: Linux ($ARCH)"
        fi
        ;;
    Darwin*)
        IS_MACOS=true
        if [ "$ARCH" = "arm64" ]; then
            HAS_APPLE_SILICON=true
            ok "Platform: macOS Apple Silicon"
        else
            ok "Platform: macOS Intel ($ARCH)"
        fi
        ;;
    *)
        warn "Platform: $OS ($ARCH) — not officially supported"
        ;;
esac

# Python
if command -v python3 &>/dev/null; then
    PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")')
    PY_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
    PY_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')
    if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 10 ]; then
        PYTHON_OK=true
        ok "Python $PY_VER"
    else
        err "Python $PY_VER — need 3.10+ (upgrade: https://python.org)"
    fi
else
    err "Python 3 not found"
    echo ""
    echo "  Install Python 3.10+:"
    if $IS_MACOS; then
        echo "    brew install python@3.12"
    else
        echo "    Ubuntu/Debian: sudo apt install python3 python3-venv"
        echo "    Fedora:        sudo dnf install python3"
    fi
fi

# uv (pip accelerator)
if command -v uv &>/dev/null; then
    ok "uv found (fast package installer)"
else
    info "uv not found — will use pip (slower installs)"
    info "Install uv for faster setup: curl -LsSf https://astral.sh/uv/install.sh | sh"
fi

# GPU/CUDA
NVIDIA_SMI=""
if $IS_MACOS; then
    if $HAS_APPLE_SILICON; then
        info "GPU: Apple Silicon — no CUDA, but faster-whisper runs well on CPU (~3-5× realtime)"
    else
        info "GPU: Intel Mac — CPU-only mode (slower, but functional)"
    fi
else
    if command -v nvidia-smi &>/dev/null; then
        NVIDIA_SMI="nvidia-smi"
    elif $IS_WSL; then
        for wsl_smi in /usr/lib/wsl/lib/nvidia-smi /usr/lib/wsl/drivers/*/nvidia-smi; do
            [ -f "$wsl_smi" ] && NVIDIA_SMI="$wsl_smi" && break
        done
    fi
    if [ -n "$NVIDIA_SMI" ]; then
        GPU_NAME=$("$NVIDIA_SMI" --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)
        if [ -n "$GPU_NAME" ]; then
            HAS_CUDA=true
            GPU_MEM=$("$NVIDIA_SMI" --query-gpu=memory.total --format=csv,noheader 2>/dev/null | head -1 | tr -d ' ')
            ok "GPU: $GPU_NAME ($GPU_MEM)"
        else
            warn "nvidia-smi found but no GPU reported"
        fi
    else
        warn "No NVIDIA GPU detected — transcription will be CPU-only (50-100× slower)"
        if $IS_WSL; then
            info "WSL CUDA setup: https://docs.nvidia.com/cuda/wsl-user-guide/"
        fi
    fi
fi

# ffmpeg
if command -v ffmpeg &>/dev/null; then
    FF_VER=$(ffmpeg -version 2>&1 | head -1 | awk '{print $3}')
    FFMPEG_OK=true
    ok "ffmpeg $FF_VER"
else
    warn "ffmpeg not found — only .wav files will work without it"
    echo ""
    echo "  Install ffmpeg (recommended):"
    if $IS_MACOS; then
        echo "    brew install ffmpeg"
    else
        echo "    Ubuntu/Debian: sudo apt install ffmpeg"
        echo "    Fedora:        sudo dnf install ffmpeg"
        echo "    Arch:           sudo pacman -S ffmpeg"
    fi
fi

# yt-dlp
YTDLP_PATH=""
if command -v yt-dlp &>/dev/null; then
    YTDLP_PATH="yt-dlp"
elif [ -f "$HOME/.local/share/pipx/venvs/yt-dlp/bin/yt-dlp" ]; then
    YTDLP_PATH="$HOME/.local/share/pipx/venvs/yt-dlp/bin/yt-dlp"
fi
if [ -n "$YTDLP_PATH" ]; then
    YTDLP_VER=$("$YTDLP_PATH" --version 2>/dev/null || echo "unknown")
    YTDLP_OK=true
    ok "yt-dlp $YTDLP_VER (YouTube/URL support)"
else
    info "yt-dlp not found — YouTube/URL input won't work"
    info "Install: pipx install yt-dlp  (or: pip install yt-dlp)"
fi

# HuggingFace token
if [ -f "$HOME/.cache/huggingface/token" ]; then
    HF_TOKEN_OK=true
    ok "HuggingFace token found"
else
    info "HuggingFace token not found (needed for faster-whisper diarization)"
    info "Setup: pip install huggingface-hub && huggingface-cli login"
fi

# ── Check existing backends ───────────────────────────────────────────
step "📦 Backend status..."

FW_DIR="$SCRIPTS_DIR/backends/faster-whisper"
PK_DIR="$SCRIPTS_DIR/backends/parakeet"

FW_BUNDLED=false; FW_READY=false
PK_BUNDLED=false; PK_READY=false

[ -d "$FW_DIR" ] && [ -f "$FW_DIR/transcribe" ] && FW_BUNDLED=true
[ -d "$PK_DIR" ] && [ -f "$PK_DIR/transcribe" ] && PK_BUNDLED=true
[ -f "$FW_DIR/.venv/bin/python" ] && FW_READY=true
[ -f "$PK_DIR/venv/bin/python" ] && PK_READY=true

if $FW_READY; then
    FW_VER=$("$FW_DIR/.venv/bin/python" -c "import importlib.metadata; print(importlib.metadata.version('faster-whisper'))" 2>/dev/null || echo "unknown")
    ok "faster-whisper: installed (v$FW_VER)"
elif $FW_BUNDLED; then
    info "faster-whisper: bundled, not yet installed"
else
    warn "faster-whisper: not bundled"
fi

if $PK_READY; then
    PK_VER=$("$PK_DIR/venv/bin/python" -c "import importlib.metadata; print(importlib.metadata.version('nemo_toolkit'))" 2>/dev/null || echo "unknown")
    ok "Parakeet (NeMo): installed (v$PK_VER)"
elif $PK_BUNDLED; then
    info "Parakeet (NeMo): bundled, not yet installed"
else
    warn "Parakeet (NeMo): not bundled"
fi

# ── Check-only mode: stop here ────────────────────────────────────────
if $CHECK_ONLY; then
    step "📋 Summary"
    if ! $PYTHON_OK; then
        err "Python 3.10+ is required. Install it first."
        exit 1
    fi
    if $FW_READY || $PK_READY; then
        ok "At least one backend is installed — ready to transcribe!"
        echo ""
        echo "  Quick test: $TRANSCRIBE --backends"
    else
        info "No backends installed yet. Run ./setup.sh to install."
    fi
    exit 0
fi

# ── Pre-flight check ──────────────────────────────────────────────────
if ! $PYTHON_OK; then
    echo ""
    err "Cannot continue without Python 3.10+. Please install it first."
    exit 1
fi

# ── Decide what to install ────────────────────────────────────────────
BACKENDS_TO_INSTALL=()

if $INSTALL_ALL; then
    $FW_BUNDLED && BACKENDS_TO_INSTALL+=("faster-whisper")
    $PK_BUNDLED && BACKENDS_TO_INSTALL+=("parakeet")
elif [ -n "$INSTALL_BACKEND" ]; then
    BACKENDS_TO_INSTALL+=("$INSTALL_BACKEND")
else
    # Auto-detect: pick the best backend for this system
    step "🤖 Selecting best backend for your system..."

    if $HAS_CUDA && $PK_BUNDLED; then
        # GPU available → Parakeet is the best choice (3380× vs 20× realtime)
        BACKENDS_TO_INSTALL+=("parakeet")
        ok "Recommending Parakeet — best accuracy & speed with your GPU"
        if $FW_BUNDLED; then
            info "faster-whisper will auto-install if you need translation or 99+ languages"
            info "Or run ./setup.sh --all to install both now"
        fi
    elif $HAS_CUDA && $FW_BUNDLED; then
        # GPU but no Parakeet bundled → faster-whisper with GPU
        BACKENDS_TO_INSTALL+=("faster-whisper")
        ok "Recommending faster-whisper with GPU acceleration"
    elif $FW_BUNDLED; then
        # No GPU → faster-whisper (works well on CPU; Parakeet needs GPU)
        BACKENDS_TO_INSTALL+=("faster-whisper")
        if $HAS_APPLE_SILICON; then
            ok "Recommending faster-whisper — runs at ~3-5× realtime on Apple Silicon"
        elif $IS_MACOS; then
            ok "Recommending faster-whisper — CPU mode on Intel Mac"
        else
            ok "Recommending faster-whisper — works on CPU (GPU recommended for speed)"
        fi
        if $PK_BUNDLED; then
            info "Parakeet is also available but needs an NVIDIA GPU to be practical"
        fi
    elif $PK_BUNDLED; then
        BACKENDS_TO_INSTALL+=("parakeet")
        ok "Installing Parakeet (only backend available)"
    else
        err "No backends are bundled. Reinstall the skill."
        exit 1
    fi
fi

if [ ${#BACKENDS_TO_INSTALL[@]} -eq 0 ]; then
    err "Nothing to install."
    exit 1
fi

# ── Install backends ──────────────────────────────────────────────────
SETUP_ARGS=()
$INSTALL_DIARIZE && SETUP_ARGS+=(--diarize)

for backend in "${BACKENDS_TO_INSTALL[@]}"; do
    step "🔧 Installing $backend..."

    case "$backend" in
        faster-whisper)
            if $FW_READY && [ ${#SETUP_ARGS[@]} -eq 0 ]; then
                ok "faster-whisper is already installed — skipping"
            else
                bash "$FW_DIR/setup.sh" "${SETUP_ARGS[@]}"
            fi
            ;;
        parakeet)
            if $PK_READY && [ ${#SETUP_ARGS[@]} -eq 0 ]; then
                ok "Parakeet is already installed — skipping"
            else
                bash "$PK_DIR/setup.sh" "${SETUP_ARGS[@]}"
            fi
            ;;
    esac
done

# ── Done ──────────────────────────────────────────────────────────────
step "🎉 Setup complete!"
echo ""

# Show what's ready
echo "  Installed backends:"
if [ -f "$FW_DIR/.venv/bin/python" ]; then
    echo "    ✅ faster-whisper"
fi
if [ -f "$PK_DIR/venv/bin/python" ]; then
    echo "    ✅ Parakeet (NeMo)"
fi
echo ""

# Missing optional deps
MISSING_OPTIONAL=()
$FFMPEG_OK  || MISSING_OPTIONAL+=("ffmpeg (audio format conversion)")
$YTDLP_OK   || MISSING_OPTIONAL+=("yt-dlp (YouTube/URL downloads)")
if $INSTALL_DIARIZE && ! $HF_TOKEN_OK; then
    MISSING_OPTIONAL+=("HuggingFace token (for pyannote diarization)")
fi

if [ ${#MISSING_OPTIONAL[@]} -gt 0 ]; then
    echo "  Optional (install for full functionality):"
    for dep in "${MISSING_OPTIONAL[@]}"; do
        echo "    • $dep"
    done
    echo ""
fi

echo "  Quick start:"
echo "    $TRANSCRIBE audio.mp3                      # Transcribe a file"
echo "    $TRANSCRIBE audio.mp3 --diarize             # With speaker detection"
echo "    $TRANSCRIBE audio.mp3 --format srt -o s.srt # Generate subtitles"
echo "    $TRANSCRIBE --backends                      # Show installed backends"
echo ""
echo "  First transcription will download the model (~1-2 GB, one-time)."
echo ""
