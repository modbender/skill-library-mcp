#!/bin/bash
set -e

# ============================================================
#  OpenClaw XHS Skill — Installer
#  Installs the Xiaohongshu automation skill for OpenClaw.
# ============================================================

SKILL_NAME="xhs"
SKILL_DIR="$HOME/.openclaw/skills/$SKILL_NAME"
TOOLKIT_DIR="$SKILL_DIR/xhs-toolkit"
CRED_DIR="$HOME/.openclaw/credentials"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}[INFO]${NC} $1"; }
ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
fail()  { echo -e "${RED}[FAIL]${NC} $1"; exit 1; }

echo ""
echo "========================================"
echo "  OpenClaw XHS Skill Installer"
echo "  小红书自动化技能安装程序"
echo "========================================"
echo ""

# ----------------------------------------------------------
# 1. Check prerequisites
# ----------------------------------------------------------
info "Checking prerequisites..."

# uv
if ! command -v uv &>/dev/null; then
    fail "uv not found. Install it first:\n  brew install uv  (macOS)\n  curl -LsSf https://astral.sh/uv/install.sh | sh  (Linux)"
fi
ok "uv found: $(uv --version)"

# Chrome
CHROME_PATH=""
if [[ "$(uname)" == "Darwin" ]]; then
    CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
elif [[ -f /usr/bin/google-chrome ]]; then
    CHROME_PATH="/usr/bin/google-chrome"
elif [[ -f /usr/bin/google-chrome-stable ]]; then
    CHROME_PATH="/usr/bin/google-chrome-stable"
fi

if [[ -z "$CHROME_PATH" ]] || [[ ! -f "$CHROME_PATH" ]]; then
    fail "Google Chrome not found. Please install Chrome first."
fi
ok "Chrome found: $CHROME_PATH"

# OpenClaw
if ! command -v openclaw &>/dev/null; then
    warn "openclaw not found in PATH. Make sure OpenClaw is installed."
    warn "  npm install -g openclaw"
else
    ok "openclaw found"
fi

# ----------------------------------------------------------
# 2. Copy files
# ----------------------------------------------------------
info "Installing skill to $SKILL_DIR ..."

# Back up existing installation if any
if [[ -d "$SKILL_DIR" ]]; then
    warn "Existing installation found. Backing up to ${SKILL_DIR}.bak"
    rm -rf "${SKILL_DIR}.bak"
    mv "$SKILL_DIR" "${SKILL_DIR}.bak"
fi

mkdir -p "$SKILL_DIR/scripts"
mkdir -p "$SKILL_DIR/data/trending"
mkdir -p "$SKILL_DIR/data/generated"
mkdir -p "$SKILL_DIR/data/published"
mkdir -p "$SKILL_DIR/chrome-data"
mkdir -p "$CRED_DIR"

# Copy SKILL.md
cp "$REPO_DIR/SKILL.md" "$SKILL_DIR/SKILL.md"

# Copy scripts
cp "$REPO_DIR/scripts/"*.py "$SKILL_DIR/scripts/"

# Copy xhs-toolkit
cp -R "$REPO_DIR/xhs-toolkit" "$TOOLKIT_DIR"

ok "Files copied"

# ----------------------------------------------------------
# 3. Install Python dependencies
# ----------------------------------------------------------
info "Installing Python dependencies (uv sync) ..."
cd "$TOOLKIT_DIR"
uv sync 2>&1 | tail -5
ok "Python dependencies installed"

# Also install extra deps used by scripts (jieba, Pillow)
info "Installing extra dependencies (jieba, Pillow) ..."
uv pip install jieba Pillow 2>&1 | tail -3
ok "Extra dependencies installed"

# ----------------------------------------------------------
# 4. Configure openclaw.json
# ----------------------------------------------------------
OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"

if [[ ! -f "$OPENCLAW_CONFIG" ]]; then
    warn "openclaw.json not found at $OPENCLAW_CONFIG"
    warn "Skipping config injection. You'll need to configure manually."
    warn "See config.example.json in the repo for the required settings."
else
    info "Configuring openclaw.json ..."

    # Ask for OpenRouter API key
    echo ""
    echo -e "${CYAN}Image generation requires an OpenAI-compatible API.${NC}"
    echo "You can use OpenRouter, NanoBanana, or any provider."
    echo ""
    read -p "Enter your image API key (or press Enter to skip): " IMAGE_KEY
    read -p "Enter your image API base URL (e.g. https://openrouter.ai/api/v1/chat/completions): " IMAGE_URL
    read -p "Enter your image model name (e.g. google/gemini-3-pro-image-preview): " IMAGE_MDL

    if [[ -z "$IMAGE_KEY" ]]; then
        IMAGE_KEY=""
        warn "No API key provided. Set IMAGE_API_KEY in openclaw.json before using AI image generation."
    fi
    if [[ -z "$IMAGE_URL" ]]; then
        IMAGE_URL=""
    fi
    if [[ -z "$IMAGE_MDL" ]]; then
        IMAGE_MDL=""
    fi

    # Try to read existing gateway token
    GATEWAY_TOKEN=$(python3 -c "
import json, sys
try:
    cfg = json.load(open('$OPENCLAW_CONFIG'))
    token = cfg.get('gateway', {}).get('token', '')
    if not token:
        # Try to find it in existing xhs config
        token = cfg.get('skills', {}).get('entries', {}).get('xhs', {}).get('env', {}).get('OPENCLAW_GATEWAY_TOKEN', '')
    print(token)
except:
    print('')
" 2>/dev/null || echo "")

    if [[ -z "$GATEWAY_TOKEN" ]]; then
        GATEWAY_TOKEN="<SET_YOUR_GATEWAY_TOKEN>"
        warn "Could not detect gateway token. Set OPENCLAW_GATEWAY_TOKEN in openclaw.json."
    fi

    # Inject config using the helper script (safe JSON manipulation)
    python3 "$REPO_DIR/scripts/configure_openclaw.py" \
        --config "$OPENCLAW_CONFIG" \
        --toolkit-dir "$TOOLKIT_DIR" \
        --cookies-file "$CRED_DIR/xhs_cookies.json" \
        --data-dir "$SKILL_DIR/data" \
        --chrome-profile "$SKILL_DIR/chrome-data" \
        --chrome-path "$CHROME_PATH" \
        --image-api-key "$IMAGE_KEY" \
        --image-base-url "$IMAGE_URL" \
        --image-model "$IMAGE_MDL" \
        --gateway-token "$GATEWAY_TOKEN"

    ok "openclaw.json configured"
fi

# ----------------------------------------------------------
# 5. Done
# ----------------------------------------------------------
echo ""
echo "========================================"
echo -e "  ${GREEN}Installation complete!${NC}"
echo "========================================"
echo ""
echo "Next steps:"
echo ""
echo "  1. Login to Xiaohongshu (scan QR code once):"
echo -e "     ${CYAN}cd $TOOLKIT_DIR && uv run python $SKILL_DIR/scripts/xhs_login_persistent.py${NC}"
echo ""
echo "  2. Restart OpenClaw gateway:"
echo -e "     ${CYAN}openclaw gateway --force${NC}"
echo ""
echo "  3. Test in Telegram/Discord:"
echo "     - Say: \"小红书热点\" to fetch trending topics"
echo "     - Say: \"帮我生成一篇小红书\" to generate content"
echo "     - Say: \"发布\" to publish"
echo ""
if [[ -z "$IMAGE_KEY" ]]; then
    echo -e "  ${YELLOW}Remember to set IMAGE_API_KEY, IMAGE_BASE_URL, IMAGE_MODEL in ~/.openclaw/openclaw.json${NC}"
    echo ""
fi
