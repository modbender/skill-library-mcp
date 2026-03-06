#!/usr/bin/env bash
# Grago Installer
# Sets up Ollama + a default model, installs grago, and drops the skill into OpenClaw

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "╔══════════════════════════════════╗"
echo "║        GRAGO INSTALLER           ║"
echo "║  Stop burning tokens. Use yours. ║"
echo "╚══════════════════════════════════╝"
echo ""

# 1. Check for Ollama
if ! command -v ollama &>/dev/null; then
  echo -e "${YELLOW}Ollama not found. Installing...${NC}"
  if [[ "$(uname)" == "Darwin" ]]; then
    if command -v brew &>/dev/null; then
      brew install --cask ollama
    else
      echo "Please install Ollama manually from https://ollama.ai and re-run this script."
      exit 1
    fi
  else
    curl -fsSL https://ollama.ai/install.sh | sh
  fi
  echo -e "${GREEN}✓ Ollama installed${NC}"
else
  echo -e "${GREEN}✓ Ollama already installed${NC}"
fi

# 2. Start Ollama if not running
if ! ollama list &>/dev/null 2>&1; then
  echo "Starting Ollama..."
  ollama serve &>/dev/null &
  sleep 3
fi

# 3. Pull a default model if none present
MODEL_COUNT=$(ollama list 2>/dev/null | tail -n +2 | wc -l | tr -d ' ')
if [[ "$MODEL_COUNT" -eq 0 ]]; then
  echo -e "${YELLOW}No local models found. Pulling gemma2:9b (recommended)...${NC}"
  echo "This is a one-time download (~5.4 GB). Go make a coffee. ☕"
  ollama pull gemma2:9b
  DEFAULT_MODEL="gemma2:9b"
  echo -e "${GREEN}✓ gemma2:9b pulled${NC}"
else
  DEFAULT_MODEL=$(ollama list 2>/dev/null | tail -n +2 | head -1 | awk '{print $1}')
  echo -e "${GREEN}✓ Using existing model: ${DEFAULT_MODEL}${NC}"
fi

# 4. Install grago
INSTALL_DIR="/usr/local/bin"
if [[ ! -w "$INSTALL_DIR" ]]; then
  INSTALL_DIR="$HOME/.local/bin"
  mkdir -p "$INSTALL_DIR"
fi

cp grago.sh "$INSTALL_DIR/grago"
chmod +x "$INSTALL_DIR/grago"
echo -e "${GREEN}✓ grago installed to ${INSTALL_DIR}/grago${NC}"

# 5. Write config
CONFIG_DIR="$HOME/.grago"
mkdir -p "$CONFIG_DIR"
if [[ ! -f "$CONFIG_DIR/config.yaml" ]]; then
  cat > "$CONFIG_DIR/config.yaml" << YAML
default_model: ${DEFAULT_MODEL}
timeout: 30
max_input_chars: 16000
output_format: markdown
YAML
  echo -e "${GREEN}✓ Config written to ~/.grago/config.yaml${NC}"
else
  echo -e "${GREEN}✓ Config already exists at ~/.grago/config.yaml${NC}"
fi

# 6. Install OpenClaw skill
SKILL_DIRS=(
  "$HOME/.openclaw/workspace/skills/grago"
  "$HOME/Library/Application Support/openclaw/workspace/skills/grago"
)

SKILL_INSTALLED=false
for DIR in "${SKILL_DIRS[@]}"; do
  if [[ -d "$(dirname "$DIR")" ]]; then
    mkdir -p "$DIR"
    cp SKILL.md "$DIR/"
    echo -e "${GREEN}✓ OpenClaw skill installed to ${DIR}${NC}"
    SKILL_INSTALLED=true
    break
  fi
done

if [[ "$SKILL_INSTALLED" == false ]]; then
  echo -e "${YELLOW}⚠ OpenClaw workspace not found — copy SKILL.md manually to your skills folder${NC}"
fi

# 7. PATH check
if ! echo "$PATH" | grep -q "$INSTALL_DIR"; then
  echo ""
  echo -e "${YELLOW}Note: Add ${INSTALL_DIR} to your PATH if not already:${NC}"
  echo "  echo 'export PATH=\"\$PATH:${INSTALL_DIR}\"' >> ~/.zshrc && source ~/.zshrc"
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════${NC}"
echo -e "${GREEN}  Grago installed! Quick test:${NC}"
echo -e "${GREEN}  grago fetch \"https://example.com\" --analyze \"Summarize this\"${NC}"
echo -e "${GREEN}═══════════════════════════════════${NC}"
echo ""
echo "Full docs: https://github.com/solsuk/grago"
echo "Support:   https://underclassic.com"
echo ""
