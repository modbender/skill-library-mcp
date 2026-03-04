#!/bin/bash

#########################################################
# SETUP BINANCE BOT — 20€ CAPITAL
# Initial configuration and launch
# Author: Georges Andronescu (Wesley Armando)
# Version: 2.0.0
#########################################################

EXECUTOR_PATH="/workspace/skills/crypto-executor/executor.py"
CONFIG_FILE="/workspace/data/bot_config.env"
# SECURITY: file will be chmod 600 after creation

echo "========================================"
echo "BINANCE BOT SETUP — 20€ CAPITAL"
echo "========================================"
echo ""

# ── Safety check ─────────────────────────────────────────────────────────────

if [ "$EUID" -eq 0 ]; then
    echo "⚠️  WARNING: Do not run as root. Use your normal user."
    exit 1
fi

# ── Create directories ────────────────────────────────────────────────────────

mkdir -p /workspace/skills/crypto-executor
mkdir -p /workspace/logs
mkdir -p /workspace/data
mkdir -p /workspace/scripts
mkdir -p /workspace/reports/daily
mkdir -p /workspace/config_history
echo "✅ Directories created"

# ── Check executor.py ─────────────────────────────────────────────────────────

if [ ! -f "$EXECUTOR_PATH" ]; then
    echo ""
    echo "❌ executor.py not found. Installing from GitHub..."
    wget -q "https://raw.githubusercontent.com/georges91560/crypto-executor/main/executor.py" \
         -O "$EXECUTOR_PATH"
    if [ ! -f "$EXECUTOR_PATH" ]; then
        echo "❌ Download failed. Install manually:"
        echo "   wget https://raw.githubusercontent.com/georges91560/crypto-executor/main/executor.py \\"
        echo "        -O $EXECUTOR_PATH"
        exit 1
    fi
    echo "✅ executor.py installed"
else
    echo "✅ executor.py found"
fi

# ── Check crypto-sniper-oracle ────────────────────────────────────────────────

ORACLE_PATH="/workspace/skills/crypto-sniper-oracle/crypto_oracle.py"
if [ ! -f "$ORACLE_PATH" ]; then
    echo ""
    echo "⚠️  crypto-sniper-oracle not found. Installing..."
    mkdir -p /workspace/skills/crypto-sniper-oracle
    # SECURITY: audit crypto_oracle.py before running — external code executed as subprocess
    # Pin a specific commit/tag on GitHub instead of downloading from main
    wget -q "https://raw.githubusercontent.com/georges91560/crypto-sniper-oracle/main/crypto_oracle.py" \
         -O "$ORACLE_PATH"
    if [ -f "$ORACLE_PATH" ]; then
        echo "✅ crypto-sniper-oracle installed"
    else
        echo "⚠️  Could not auto-install oracle. Install manually from:"
        echo "   https://github.com/georges91560/crypto-sniper-oracle"
    fi
else
    echo "✅ crypto-sniper-oracle found"
fi

# ── Check websocket-client ────────────────────────────────────────────────────

if ! python3 -c "import websocket" 2>/dev/null; then
    echo "📦 Installing websocket-client (for sub-100ms streams)..."
    pip install websocket-client --break-system-packages --quiet
    # On VPS/standard server: prefer → python3 -m venv venv && source venv/bin/activate && pip install websocket-client
    echo "✅ websocket-client installed"
else
    echo "✅ websocket-client available"
fi

# ── Credentials ───────────────────────────────────────────────────────────────

echo ""
echo "[CONFIG] Checking credentials..."

if [ -z "$BINANCE_API_KEY" ]; then
    echo "📝 Binance API Key:"
    read -r BINANCE_API_KEY
    export BINANCE_API_KEY
fi

if [ -z "$BINANCE_API_SECRET" ]; then
    echo "📝 Binance API Secret:"
    read -r BINANCE_API_SECRET
    export BINANCE_API_SECRET
fi

if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "📝 Telegram Bot Token (Enter to skip):"
    read -r TELEGRAM_BOT_TOKEN
    export TELEGRAM_BOT_TOKEN
fi

if [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo "📝 Telegram Chat ID (Enter to skip):"
    read -r TELEGRAM_CHAT_ID
    export TELEGRAM_CHAT_ID
fi

echo "✅ Credentials configured"

# ── Write config file ─────────────────────────────────────────────────────────

cat > "$CONFIG_FILE" << EOF
# Binance Bot Configuration — Generated $(date)
# ⚠️  chmod 600 this file

BINANCE_API_KEY="$BINANCE_API_KEY"
BINANCE_API_SECRET="$BINANCE_API_SECRET"
TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID="$TELEGRAM_CHAT_ID"

# Capital & Position Sizing (20€ conservative)
MAX_POSITION_SIZE_PCT="12"
DAILY_LOSS_LIMIT_PCT="2"
WEEKLY_LOSS_LIMIT_PCT="5"
DRAWDOWN_PAUSE_PCT="7"
DRAWDOWN_KILL_PCT="10"
EOF

chmod 600 "$CONFIG_FILE"
echo "✅ Config saved to $CONFIG_FILE (chmod 600)"

# ── Display summary ───────────────────────────────────────────────────────────

echo ""
echo "========================================"
echo "CONFIGURATION — 20€ CAPITAL"
echo "========================================"
echo ""
echo "💰 Capital:        \$22 (~20€)"
echo "📊 Max/trade:      12% = \$2.64"
echo "🛡️  Daily limit:   -2% = -\$0.44"
echo "🛡️  Weekly limit:  -5% = -\$1.10"
echo "🔴 Kill switch:    -10% = -\$2.20"
echo ""
echo "Strategy mix (Wesley will optimize):"
echo "  Scalping: 70% | Momentum: 25% | Stat Arb: 5%"
echo ""

# ── Stop existing bot ─────────────────────────────────────────────────────────

if pgrep -f "executor.py" > /dev/null || systemctl is-active --quiet crypto-executor 2>/dev/null; then
    echo "⚠️  Bot already running. Stopping..."
    sudo systemctl stop crypto-executor 2>/dev/null || pkill -f "executor.py"
    sleep 3
    echo "✅ Stopped"
fi

# ── Launch bot ────────────────────────────────────────────────────────────────

echo "[START] Launching crypto-executor..."
source "$CONFIG_FILE"

# Try systemd first
if systemctl list-unit-files crypto-executor.service &>/dev/null; then
    sudo systemctl start crypto-executor
    sleep 3
    if systemctl is-active --quiet crypto-executor; then
        echo "✅ Bot started via systemd"
        echo ""
        echo "📊 Monitor: sudo journalctl -u crypto-executor -f"
        exit 0
    fi
fi

# Fallback: direct launch
nohup python3 "$EXECUTOR_PATH" > /workspace/logs/binance_bot.log 2>&1 &
BOT_PID=$!
sleep 3

if ps -p $BOT_PID > /dev/null 2>&1; then
    echo "✅ Bot started (PID: $BOT_PID)"
    echo ""
    echo "📊 Monitor: tail -f /workspace/logs/binance_bot.log"
    echo "🛑 Stop: kill $BOT_PID  OR  pkill -f executor.py"
else
    echo "❌ Bot failed to start. Check logs:"
    echo "   tail -50 /workspace/logs/binance_bot.log"
    exit 1
fi

echo ""
echo "========================================"
echo "BOT RUNNING — \$22 CAPITAL"
echo "Wesley will optimize every 6 hours."
echo "========================================"
