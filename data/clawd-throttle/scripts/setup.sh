#!/bin/bash
set -e

echo ""
echo "=== Clawd Throttle Setup ==="
echo "Universal LLM Cost Optimizer — 8 providers, 30+ models"
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "Error: Node.js 18+ is required. Install from https://nodejs.org/"
    exit 1
fi

echo "Node.js version: $(node --version)"

# Install dependencies
echo ""
echo "Installing dependencies..."
npm install

echo ""
echo "Dependencies installed."

# --- Provider API Keys (all optional) ---
echo ""
echo "Configure your LLM providers (all optional — press Enter to skip):"
echo "You only need ONE provider to get started."
echo ""

# Anthropic
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "[Anthropic] Claude Opus, Sonnet, Haiku"
    echo "  Get a key at: https://console.anthropic.com/settings/keys"
    read -rp "  ANTHROPIC_API_KEY: " ANTHROPIC_API_KEY
    [ -n "$ANTHROPIC_API_KEY" ] && export ANTHROPIC_API_KEY
else
    echo "[Anthropic] Key found in environment."
fi

# Google
if [ -z "$GOOGLE_AI_API_KEY" ]; then
    echo "[Google] Gemini 2.5 Pro, Flash, Flash-Lite"
    echo "  Get a key at: https://aistudio.google.com/app/apikey"
    read -rp "  GOOGLE_AI_API_KEY: " GOOGLE_AI_API_KEY
    [ -n "$GOOGLE_AI_API_KEY" ] && export GOOGLE_AI_API_KEY
else
    echo "[Google] Key found in environment."
fi

# OpenAI
if [ -z "$OPENAI_API_KEY" ]; then
    echo "[OpenAI] GPT-5.2, GPT-5.1, GPT-5-mini, o3"
    echo "  Get a key at: https://platform.openai.com/api-keys"
    read -rp "  OPENAI_API_KEY: " OPENAI_API_KEY
    [ -n "$OPENAI_API_KEY" ] && export OPENAI_API_KEY
else
    echo "[OpenAI] Key found in environment."
fi

# DeepSeek
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "[DeepSeek] DeepSeek-Chat, DeepSeek-Reasoner"
    echo "  Get a key at: https://platform.deepseek.com/api-keys"
    read -rp "  DEEPSEEK_API_KEY: " DEEPSEEK_API_KEY
    [ -n "$DEEPSEEK_API_KEY" ] && export DEEPSEEK_API_KEY
else
    echo "[DeepSeek] Key found in environment."
fi

# xAI
if [ -z "$XAI_API_KEY" ]; then
    echo "[xAI] Grok-4, Grok-3, Grok-3-mini"
    echo "  Get a key at: https://console.x.ai/"
    read -rp "  XAI_API_KEY: " XAI_API_KEY
    [ -n "$XAI_API_KEY" ] && export XAI_API_KEY
else
    echo "[xAI] Key found in environment."
fi

# Moonshot
if [ -z "$MOONSHOT_API_KEY" ]; then
    echo "[Moonshot] Kimi K2.5, K2-thinking"
    echo "  Get a key at: https://platform.moonshot.ai/console/api-keys"
    read -rp "  MOONSHOT_API_KEY: " MOONSHOT_API_KEY
    [ -n "$MOONSHOT_API_KEY" ] && export MOONSHOT_API_KEY
else
    echo "[Moonshot] Key found in environment."
fi

# Mistral
if [ -z "$MISTRAL_API_KEY" ]; then
    echo "[Mistral] Mistral Large, Small, Codestral"
    echo "  Get a key at: https://console.mistral.ai/api-keys"
    read -rp "  MISTRAL_API_KEY: " MISTRAL_API_KEY
    [ -n "$MISTRAL_API_KEY" ] && export MISTRAL_API_KEY
else
    echo "[Mistral] Key found in environment."
fi

# Ollama
echo "[Ollama] Local models (no API key needed)"
if [ -z "$OLLAMA_BASE_URL" ]; then
    echo "  Default: http://localhost:11434/v1"
    read -rp "  OLLAMA_BASE_URL (press Enter for default): " OLLAMA_BASE_URL
    [ -n "$OLLAMA_BASE_URL" ] && export OLLAMA_BASE_URL
else
    echo "  Base URL: $OLLAMA_BASE_URL"
fi

# Count configured
CONFIGURED=1  # Ollama is always available
[ -n "$ANTHROPIC_API_KEY" ]  && CONFIGURED=$((CONFIGURED + 1))
[ -n "$GOOGLE_AI_API_KEY" ]  && CONFIGURED=$((CONFIGURED + 1))
[ -n "$OPENAI_API_KEY" ]     && CONFIGURED=$((CONFIGURED + 1))
[ -n "$DEEPSEEK_API_KEY" ]   && CONFIGURED=$((CONFIGURED + 1))
[ -n "$XAI_API_KEY" ]        && CONFIGURED=$((CONFIGURED + 1))
[ -n "$MOONSHOT_API_KEY" ]   && CONFIGURED=$((CONFIGURED + 1))
[ -n "$MISTRAL_API_KEY" ]    && CONFIGURED=$((CONFIGURED + 1))

echo ""
echo "$CONFIGURED provider(s) configured (including Ollama)."

# Create config directory
CONFIG_DIR="${CLAWD_THROTTLE_CONFIG_DIR:-$HOME/.config/clawd-throttle}"
mkdir -p "$CONFIG_DIR"
echo ""
echo "Config directory: $CONFIG_DIR"

# Select routing mode
echo ""
echo "Select your default routing mode:"
echo ""
echo "  1. eco          Cheapest models first. Great for high-volume, simple tasks."
echo "  2. standard     Balanced. Cost-effective mix of quality and savings."
echo "  3. performance  Best quality. Premium models for complex reasoning."
echo ""
read -rp "Enter choice [1/2/3] (default: 2): " CHOICE
case "$CHOICE" in
    1) MODE="eco" ;;
    3) MODE="performance" ;;
    *) MODE="standard" ;;
esac

# Write config.json
cat > "$CONFIG_DIR/config.json" << CONFIGEOF
{
  "mode": "$MODE",
  "logging": {
    "level": "info",
    "logFilePath": "$CONFIG_DIR/routing.jsonl"
  },
  "classifier": {
    "weightsPath": "",
    "thresholds": {
      "simpleMax": 0.30,
      "complexMin": 0.65
    }
  },
  "modelCatalogPath": ""
}
CONFIGEOF

# Append provider sections only if keys were provided
# (The env vars will be picked up at runtime regardless)

echo ""
echo "Configuration saved to: $CONFIG_DIR/config.json"
echo "Routing mode: $MODE"
echo ""
echo "Tip: Set API keys as environment variables for automatic pickup:"
echo "  export ANTHROPIC_API_KEY=sk-..."
echo "  export OPENAI_API_KEY=sk-..."
echo "  export GOOGLE_AI_API_KEY=..."
echo ""
echo "Setup complete! To start:"
echo "  npm start               # MCP stdio server"
echo "  npm start -- --http     # MCP + HTTP proxy"
echo "  npm start -- --http-only # HTTP proxy only"
echo ""
