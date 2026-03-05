#!/bin/bash
set -e
GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; exit 1; }
info() { echo -e "${YELLOW}[INFO]${NC} $1"; }

info "Checking Node.js..."
command -v node >/dev/null 2>&1 || fail "Node.js not found. Install Node 18+ first."
NODE_VER=$(node -e "process.stdout.write(process.version.slice(1).split('.')[0])")
[ "$NODE_VER" -ge 18 ] || fail "Node.js 18+ required (found v$NODE_VER)"
ok "Node.js v$NODE_VER"

info "Checking gemini-cli..."
if ! command -v gemini >/dev/null 2>&1; then
  info "Installing @google/gemini-cli..."
  npm install -g @google/gemini-cli || fail "Failed to install gemini-cli"
fi
ok "gemini-cli $(gemini --version 2>/dev/null)"

info "Checking gcloud..."
if ! command -v gcloud >/dev/null 2>&1; then
  info "Installing google-cloud-cli via apt..."
  curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
  echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee /etc/apt/sources.list.d/google-cloud-sdk.list
  apt-get update -q && apt-get install -y google-cloud-cli || fail "Failed to install gcloud"
fi
ok "gcloud: $(gcloud --version 2>/dev/null | head -1)"

info "Installing ask-gemini wrapper..."
WRAPPER_PATH="/usr/local/bin/ask-gemini"
cat > "$WRAPPER_PATH" << 'WRAPPER'
#!/bin/bash
# ask-gemini — Gemini via Google subscription (no API cost)
# Usage: ask-gemini "prompt" | ask-gemini -m gemini-2.5-pro "prompt" | echo "text" | ask-gemini "instruction"
# Agentic coding: cd /project && GOOGLE_GENAI_USE_GCA=true gemini -m gemini-2.5-pro -y -p "task"
MODEL=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    -m|--model) MODEL="$2"; shift 2 ;;
    *) PROMPT="$*"; break ;;
  esac
done
if [ ! -t 0 ]; then
  STDIN_DATA=$(cat)
  FULL_PROMPT="${PROMPT:+$PROMPT$'\n'}$STDIN_DATA"
else
  FULL_PROMPT="$PROMPT"
fi
[ -z "$FULL_PROMPT" ] && { echo "Usage: ask-gemini \"prompt\"" >&2; exit 1; }
export GOOGLE_GENAI_USE_GCA=true
exec gemini -m "${MODEL:-gemini-3.1-pro-preview}" -p "$FULL_PROMPT" 2>&1 | grep -v "^Loaded cached credentials"
WRAPPER
chmod +x "$WRAPPER_PATH"
ok "ask-gemini installed at $WRAPPER_PATH"

CREDS="$HOME/.config/gcloud/application_default_credentials.json"
echo ""
if [ -f "$CREDS" ]; then
  ok "GCA credentials found. You're ready to go!"
else
  echo -e "${YELLOW}━━━ AUTH REQUIRED ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo "1. On this VPS (headless):   gcloud auth application-default login --no-browser"
  echo "2. On laptop with browser:   gcloud auth application-default login --remote-bootstrap=\"<URL>\""
  echo "3. Then complete Gemini CLI auth: GOOGLE_GENAI_USE_GCA=true gemini -p \"hello\""
  echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
fi
echo ""
echo -e "${GREEN}Setup complete!${NC} Test with: ask-gemini \"hello\""
