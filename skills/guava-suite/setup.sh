#!/usr/bin/env bash
# setup.sh — GuavaSuite installer
# Runs automatically when installed via clawhub or manually
# Why: Users need one command to get everything working

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OPENCLAW_DIR="$HOME/.openclaw"
PLUGINS_DIR="$OPENCLAW_DIR/plugins"
SUITE_DIR="$OPENCLAW_DIR/guava-suite"
CONFIG_FILE="$OPENCLAW_DIR/openclaw.json"

echo ""
echo "🍈 GuavaSuite Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── 1. Check Node.js ──
if ! command -v node &>/dev/null; then
    echo "❌ Node.js is required. Install from: https://nodejs.org"
    exit 1
fi

NODE_VERSION=$(node -v | sed 's/v//' | cut -d. -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js >= 18 required (found: $(node -v))"
    exit 1
fi

echo "  ✅ Node.js $(node -v)"

# ── 2. Check guard-scanner dependency ──
if [ -d "$OPENCLAW_DIR/skills/guard-scanner" ] || command -v guard-scanner &>/dev/null; then
    echo "  ✅ guard-scanner found"
else
    echo "  ⚠️  guard-scanner not found"
    echo "     Install: clawhub install guard-scanner"
    echo "     Or: npm install -g guard-scanner"
    echo ""
    read -p "  Continue without guard-scanner? (y/N): " -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# ── 3. Install dependencies ──
echo ""
echo "  📦 Installing dependencies..."

cd "$SCRIPT_DIR"
npm install --production --omit=dev 2>&1 | tail -1

# Also install in services/license-api
if [ -d "$SCRIPT_DIR/services/license-api" ]; then
    cd "$SCRIPT_DIR/services/license-api"
    npm install --production --omit=dev 2>&1 | tail -1
fi

cd "$SCRIPT_DIR"
echo "  ✅ Dependencies installed"

# ── 4. Create suite directory ──
mkdir -p "$SUITE_DIR"
echo "  ✅ Suite directory: $SUITE_DIR"

# ── 5. Copy plugin to OpenClaw plugins directory ──
mkdir -p "$PLUGINS_DIR"

# If guard-scanner plugin exists, update its config to know about Suite
# Don't overwrite — just ensure suite integration config is present
PLUGIN_CONFIG="$SUITE_DIR/config.json"
if [ ! -f "$PLUGIN_CONFIG" ]; then
    cat > "$PLUGIN_CONFIG" << 'EOF'
{
    "suiteEnabled": false,
    "guardMode": "enforce",
    "tokenFile": "~/.openclaw/guava-suite/token.jwt",
    "activatedAt": null,
    "walletAddress": null
}
EOF
    echo "  ✅ Suite config created"
else
    echo "  ✅ Suite config exists (preserved)"
fi

# ── 6. Add AGENTS.md entry (if not present) ──
AGENTS_FILE="$OPENCLAW_DIR/workspace/AGENTS.md"
if [ -f "$AGENTS_FILE" ]; then
    if ! grep -q "guava-suite" "$AGENTS_FILE" 2>/dev/null; then
        echo "" >> "$AGENTS_FILE"
        echo "## GuavaSuite 🍈" >> "$AGENTS_FILE"
        echo "Premium security suite. Activate: \`node skills/guava-suite/services/license-api/src/activate.js --status\`" >> "$AGENTS_FILE"
        echo "  ✅ AGENTS.md updated"
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🍈 Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Get $GUAVA tokens on Polygon Mainnet"
echo "     Token: 0x25cBD481901990bF0ed2ff9c5F3C0d4f743AC7B8"
echo "     Buy: https://quickswap.exchange/#/swap"
echo ""
echo "  2. Activate GuavaSuite:"
echo "     node $SCRIPT_DIR/services/license-api/src/activate.js --wallet 0xYOUR_ADDRESS"
echo ""
echo "  3. Check status anytime:"
echo "     node $SCRIPT_DIR/services/license-api/src/activate.js --status"
echo ""
