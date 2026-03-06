#!/bin/bash
set -e

# QuantumOS Setup Script
# Installs and configures QuantumOS dashboard for OpenClaw

REPO="https://github.com/murtiurti4/quantumos.git"
INSTALL_DIR="$HOME/Projects/quantumos"
MC_DIR="$HOME/.openclaw/mission-control"
DASH_DIR="$HOME/.openclaw/dashboard-data"
OC_CONFIG="$HOME/.openclaw/openclaw.json"

echo ""
echo "  ╔═══════════════════════════════════╗"
echo "  ║        QuantumOS Setup            ║"
echo "  ╚═══════════════════════════════════╝"
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Install Node.js 20+ from https://nodejs.org"
    exit 1
fi

NODE_VER=$(node -v | sed 's/v//' | cut -d. -f1)
if [ "$NODE_VER" -lt 20 ]; then
    echo "❌ Node.js 20+ required (found v$(node -v)). Update from https://nodejs.org"
    exit 1
fi
echo "✅ Node.js $(node -v)"

# Check git
if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Install git first."
    exit 1
fi
echo "✅ Git found"

# Clone or update repo
if [ -d "$INSTALL_DIR" ]; then
    echo "📁 QuantumOS already exists at $INSTALL_DIR"
    cd "$INSTALL_DIR"
    echo "   Pulling latest..."
    git pull --ff-only 2>/dev/null || echo "   (skipped pull - may have local changes)"
else
    echo "📥 Cloning QuantumOS..."
    mkdir -p "$(dirname "$INSTALL_DIR")"
    git clone "$REPO" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install --no-audit --no-fund 2>&1 | tail -1

# Create data directories
mkdir -p "$MC_DIR" "$DASH_DIR"
echo "📁 Data directories ready"

# Create .env.local if missing
if [ ! -f .env.local ]; then
    echo "⚙️  Setting up environment..."

    # Try to auto-detect gateway token
    GW_TOKEN=""
    GW_PORT="18789"
    if [ -f "$OC_CONFIG" ]; then
        GW_TOKEN=$(python3 -c "import json; c=json.load(open('$OC_CONFIG')); print(c.get('gateway',{}).get('token',''))" 2>/dev/null || echo "")
        GW_PORT_FOUND=$(python3 -c "import json; c=json.load(open('$OC_CONFIG')); print(c.get('gateway',{}).get('port',''))" 2>/dev/null || echo "")
        if [ -n "$GW_PORT_FOUND" ]; then
            GW_PORT="$GW_PORT_FOUND"
        fi
    fi

    if [ -z "$GW_TOKEN" ]; then
        echo ""
        echo "   Couldn't auto-detect gateway token."
        echo "   Find it in: ~/.openclaw/openclaw.json → gateway.token"
        echo ""
        read -p "   Enter your OpenClaw gateway token: " GW_TOKEN
    else
        echo "   ✅ Auto-detected gateway token"
    fi

    cat > .env.local << EOF
OPENCLAW_GATEWAY_PORT=$GW_PORT
OPENCLAW_GATEWAY_TOKEN=$GW_TOKEN
EOF
    echo "   ✅ Created .env.local"
else
    echo "⚙️  .env.local already exists (keeping existing)"
fi

# Initialize empty data files if needed
if [ ! -f "$MC_DIR/tasks.json" ]; then
    echo '[]' > "$MC_DIR/tasks.json"
fi
if [ ! -f "$MC_DIR/agents.json" ]; then
    echo '[]' > "$MC_DIR/agents.json"
fi
if [ ! -f "$MC_DIR/activities.json" ]; then
    echo '[]' > "$MC_DIR/activities.json"
fi
if [ ! -f "$MC_DIR/notifications.json" ]; then
    echo '[]' > "$MC_DIR/notifications.json"
fi

echo ""
echo "  ✅ QuantumOS is ready!"
echo ""
echo "  To start:"
echo "    cd $INSTALL_DIR"
echo "    npm run dev"
echo ""
echo "  Then open: http://localhost:3005"
echo ""
echo "  On first open, enter your gateway token in Settings."
echo "  (It's in ~/.openclaw/openclaw.json → gateway.token)"
echo ""
