#!/bin/bash
# Bittensor SN85 Vibe Miner - Start Miners
# Launches PM2 processes for upscaler and/or compressor

set -e

INSTALL_DIR="${INSTALL_DIR:-$HOME/vidaio-subnet}"
WALLET_NAME="${WALLET_NAME:-default}"

echo "🐍 SN85 Vibe Miner - Start Miners"
echo "=================================="
echo

# Load environment if exists
if [ -f ~/.sn85_miner_env ]; then
    source ~/.sn85_miner_env
    echo "✅ Loaded environment from ~/.sn85_miner_env"
else
    echo "⚠️  No environment file found (run register.sh first)"
fi

if [ -f ~/.sn85_storage_config ]; then
    source ~/.sn85_storage_config
    echo "✅ Loaded storage config"
else
    echo "⚠️  No storage config found (run storage_setup.sh first)"
fi

echo

# Check installation
if [ ! -d "$INSTALL_DIR" ]; then
    echo "❌ vidaio-subnet not found at $INSTALL_DIR"
    echo "   Run ./scripts/install.sh first"
    exit 1
fi

cd "$INSTALL_DIR"

# Detect environment for port mapping
if [ -f "/.dockerenv" ] || grep -q docker /proc/1/cgroup 2>/dev/null; then
    ENV="docker"
elif command -v vastai &> /dev/null || [ -n "$VAST_CONTAINERLABEL" ]; then
    ENV="vastai"
else
    ENV="baremetal"
fi

echo "📍 Environment: $ENV"
echo

# Get external ports for Vast.ai
if [ "$ENV" == "vastai" ]; then
    echo "🔍 Detecting Vast.ai port mappings..."
    
    # Vast.ai maps ports via environment variables
    # We use non-conflicting internal ports
    UPSCALER_INTERNAL_PORT=8384
    COMPRESSOR_INTERNAL_PORT=1111
    
    # Find external ports from env vars
    UPSCALER_EXTERNAL_PORT=$(env | grep "VAST_TCP_PORT_8384" | cut -d'=' -f2 || echo "")
    COMPRESSOR_EXTERNAL_PORT=$(env | grep "VAST_TCP_PORT_1111" | cut -d'=' -f2 || echo "")
    
    if [ -z "$UPSCALER_EXTERNAL_PORT" ]; then
        echo "⚠️  WARNING: Could not detect upscaler external port"
        read -p "Enter external port for upscaler (or press Enter for 8384): " UPSCALER_EXTERNAL_PORT
        UPSCALER_EXTERNAL_PORT=${UPSCALER_EXTERNAL_PORT:-8384}
    fi
    
    if [ -z "$COMPRESSOR_EXTERNAL_PORT" ]; then
        echo "⚠️  WARNING: Could not detect compressor external port"
        read -p "Enter external port for compressor (or press Enter for 1111): " COMPRESSOR_EXTERNAL_PORT
        COMPRESSOR_EXTERNAL_PORT=${COMPRESSOR_EXTERNAL_PORT:-1111}
    fi
    
    echo "   Upscaler: internal=$UPSCALER_INTERNAL_PORT, external=$UPSCALER_EXTERNAL_PORT"
    echo "   Compressor: internal=$COMPRESSOR_INTERNAL_PORT, external=$COMPRESSOR_EXTERNAL_PORT"
    echo
else
    # Bare metal or Docker - use default ports
    UPSCALER_INTERNAL_PORT=8000
    UPSCALER_EXTERNAL_PORT=8000
    COMPRESSOR_INTERNAL_PORT=8001
    COMPRESSOR_EXTERNAL_PORT=8001
fi

# Start services
echo "========================================="
echo "🚀 Starting Miner Services"
echo "========================================="
echo

# Start worker services first
echo "📦 Starting worker services..."

pm2 start services/upscale/server.py \
    --name video-upscaler \
    --interpreter python3 \
    --cwd "$INSTALL_DIR/services/upscale" \
    || echo "   (video-upscaler may already be running)"

pm2 start services/compress/server.py \
    --name video-compressor \
    --interpreter python3 \
    --cwd "$INSTALL_DIR/services/compress" \
    || echo "   (video-compressor may already be running)"

pm2 start services/compress/deleter.py \
    --name video-deleter \
    --interpreter python3 \
    --cwd "$INSTALL_DIR/services/compress" \
    || echo "   (video-deleter may already be running)"

echo "✅ Worker services started"
echo

# Start upscaler miner if requested
if [ -n "$UPSCALER_UID" ]; then
    echo "🔧 Starting upscaler miner (UID $UPSCALER_UID)..."
    
    pm2 start neurons/miner.py \
        --name video-miner \
        --interpreter "$INSTALL_DIR/venv/bin/python" \
        --cwd "$INSTALL_DIR" \
        -- \
        --netuid 85 \
        --subtensor.network finney \
        --wallet.name "$WALLET_NAME" \
        --wallet.hotkey mining \
        --axon.port "$UPSCALER_INTERNAL_PORT" \
        --axon.external_port "$UPSCALER_EXTERNAL_PORT" \
        --logging.debug \
        || echo "   (video-miner may already be running)"
    
    echo "✅ Upscaler miner started"
    echo "   Port: $UPSCALER_EXTERNAL_PORT"
    echo
fi

# Start compressor miner if requested
if [ -n "$COMPRESSOR_UID" ]; then
    echo "🔧 Starting compressor miner (UID $COMPRESSOR_UID)..."
    
    pm2 start neurons/miner_compress.py \
        --name video-miner-compress \
        --interpreter "$INSTALL_DIR/venv/bin/python" \
        --cwd "$INSTALL_DIR" \
        -- \
        --netuid 85 \
        --subtensor.network finney \
        --wallet.name "$WALLET_NAME" \
        --wallet.hotkey mining2 \
        --axon.port "$COMPRESSOR_INTERNAL_PORT" \
        --axon.external_port "$COMPRESSOR_EXTERNAL_PORT" \
        --logging.debug \
        || echo "   (video-miner-compress may already be running)"
    
    echo "✅ Compressor miner started"
    echo "   Port: $COMPRESSOR_EXTERNAL_PORT"
    echo
fi

# Show status
echo "========================================="
echo "📊 Miner Status"
echo "========================================="
pm2 list
echo

echo "========================================="
echo "✅ Miners Started!"
echo "========================================="
echo
echo "📋 Next Steps:"
echo "   1. Monitor logs: pm2 logs"
echo "   2. Check status: ./scripts/monitor.sh"
echo "   3. Wait for first tasks (upscaler: 30-60min)"
echo "   4. Verify VMAF calculation in compressor logs"
echo
echo "⏱️  Immunity period: 7200 blocks (~24 hours)"
echo "   Monitor closely during this time!"
echo
