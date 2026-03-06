#!/usr/bin/env bash
# install.sh — One-command installer for the Qwen3-TTS OpenClaw skill
# Usage: bash install.sh
#   or:  curl -fsSL https://raw.githubusercontent.com/daMustermann/claw-qwen3-tts/main/install.sh | bash
set -euo pipefail

# ─── Colors ───
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()   { echo -e "${RED}[ERR]${NC}   $*"; }

# ─── Config ───
SKILL_NAME="qwen3-tts"
REPO_URL="https://github.com/daMustermann/claw-qwen3-tts.git"
SKILLS_DIR="${OPENCLAW_SKILLS_DIR:-${HOME}/clawd/skills}"
INSTALL_DIR="${SKILLS_DIR}/${SKILL_NAME}"

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║  🎤 Qwen3-TTS OpenClaw Skill — Installer v1.0   ║${NC}"
echo -e "${BOLD}║  Author: daMustermann                           ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════════════╝${NC}"
echo ""

# ─── Step 1: Check prerequisites ───
info "Checking prerequisites..."

MISSING=()
for cmd in git python3 ffmpeg sox curl; do
    if ! command -v "$cmd" &>/dev/null; then
        MISSING+=("$cmd")
    fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
    err "Missing required tools: ${MISSING[*]}"
    echo ""

    # Detect distro and suggest install command
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        case "$ID" in
            cachyos|arch|endeavouros|manjaro)
                echo "  sudo pacman -S ${MISSING[*]/#/} base-devel"
                ;;
            ubuntu|debian|pop|linuxmint)
                echo "  sudo apt update && sudo apt install -y ${MISSING[*]/#/} build-essential python3-venv"
                ;;
            fedora|rhel|centos)
                echo "  sudo dnf install -y ${MISSING[*]/#/} gcc gcc-c++ make"
                ;;
            opensuse*|suse)
                echo "  sudo zypper install -y ${MISSING[*]/#/} gcc gcc-c++ make"
                ;;
            *)
                echo "  Please install: ${MISSING[*]}"
                ;;
        esac
    fi
    echo ""
    exit 1
fi
ok "Prerequisites OK"

# ─── Step 2: Create skills directory ───
if [ ! -d "$SKILLS_DIR" ]; then
    info "Creating skills directory: $SKILLS_DIR"
    mkdir -p "$SKILLS_DIR"
fi

# ─── Step 3: Clone or update the repo ───
if [ -d "$INSTALL_DIR" ]; then
    if [ -d "$INSTALL_DIR/.git" ]; then
        info "Skill already installed, updating..."
        cd "$INSTALL_DIR"
        git pull --ff-only origin main 2>/dev/null || {
            warn "Git pull failed, continuing with existing version"
        }
        ok "Updated to latest version"
    else
        warn "Directory $INSTALL_DIR exists but is not a git repo"
        warn "Skipping clone — using existing files"
    fi
else
    info "Cloning skill from GitHub..."
    git clone "$REPO_URL" "$INSTALL_DIR"
    ok "Cloned to $INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# ─── Step 4: Make scripts executable ───
info "Setting script permissions..."
chmod +x scripts/*.sh 2>/dev/null || true
ok "Scripts are executable"

# ─── Step 5: Run environment setup ───
info "Running environment setup (GPU detection, venv, dependencies)..."
echo ""
bash "$INSTALL_DIR/scripts/setup_env.sh"
echo ""

# ─── Step 6: Verify installation ───
info "Verifying installation..."

if [ -d "$INSTALL_DIR/.venv" ]; then
    ok "Virtual environment created"
else
    err "Virtual environment not found — setup may have failed"
    exit 1
fi

if [ -f "$INSTALL_DIR/SKILL.md" ]; then
    ok "SKILL.md present"
else
    err "SKILL.md missing"
    exit 1
fi

if [ -f "$INSTALL_DIR/config.json" ]; then
    ok "Config generated"
else
    warn "config.json not found — will be created on first server start"
fi

# ─── Done ───
echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║  ✅ Installation complete!                       ║${NC}"
echo -e "${BOLD}║                                                  ║${NC}"
echo -e "${BOLD}║  Installed to: ${INSTALL_DIR}${NC}"
echo -e "${BOLD}║                                                  ║${NC}"
echo -e "${BOLD}║  Quick test:                                     ║${NC}"
echo -e "${BOLD}║    bash ${INSTALL_DIR}/scripts/start_server.sh   ║${NC}"
echo -e "${BOLD}║    bash ${INSTALL_DIR}/scripts/health_check.sh   ║${NC}"
echo -e "${BOLD}║                                                  ║${NC}"
echo -e "${BOLD}║  OpenClaw now has access to the qwen3-tts skill. ║${NC}"
echo -e "${BOLD}║  Just ask it to generate speech or design voices!║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════════════╝${NC}"
echo ""
