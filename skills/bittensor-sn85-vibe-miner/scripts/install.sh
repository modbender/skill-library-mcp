#!/bin/bash
# Bittensor SN85 Vibe Miner - Installation Script
# Author: Mark Jeffrey
# Installs all dependencies for VidAIo subnet mining

set -e

echo "🐍 Bittensor SN85 Vibe Miner - Installation"
echo "=========================================="
echo

# Detect environment
if [ -f "/.dockerenv" ] || grep -q docker /proc/1/cgroup 2>/dev/null; then
    ENV="docker"
elif command -v vastai &> /dev/null || [ -n "$VAST_CONTAINERLABEL" ]; then
    ENV="vastai"
else
    ENV="baremetal"
fi

echo "📍 Detected environment: $ENV"
echo

# Check for GPU
if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ ERROR: nvidia-smi not found. NVIDIA GPU required."
    exit 1
fi

GPU_INFO=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
echo "✅ GPU detected: $GPU_INFO"
echo

# Check NVENC support
if nvidia-smi --query-gpu=encoder.stats.sessionCount --format=csv,noheader &> /dev/null; then
    echo "✅ NVENC hardware encoding supported"
else
    echo "⚠️  WARNING: NVENC support unclear, may not work optimally"
fi
echo

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt-get update -qq
sudo apt-get install -y \
    python3.10 python3.10-venv python3-pip \
    ffmpeg \
    git \
    npm \
    curl \
    build-essential \
    libvulkan1 \
    vulkan-utils \
    > /dev/null 2>&1

echo "✅ System packages installed"
echo

# Install PM2
if ! command -v pm2 &> /dev/null; then
    echo "📦 Installing PM2 process manager..."
    sudo npm install -g pm2 > /dev/null 2>&1
    echo "✅ PM2 installed"
else
    echo "✅ PM2 already installed"
fi
echo

# Install video2x (CRITICAL: CLI version for speed)
echo "📦 Installing video2x (optimized CLI)..."
if ! command -v video2x &> /dev/null; then
    # Install from releases (binary is much faster than Python)
    VIDEO2X_VERSION="6.3.1"
    VIDEO2X_URL="https://github.com/k4yt3x/video2x/releases/download/${VIDEO2X_VERSION}/video2x-linux-amd64.zip"
    
    cd /tmp
    curl -sL "$VIDEO2X_URL" -o video2x.zip
    unzip -q video2x.zip
    sudo mv video2x /usr/local/bin/
    sudo chmod +x /usr/local/bin/video2x
    rm video2x.zip
    
    echo "✅ video2x ${VIDEO2X_VERSION} installed"
else
    echo "✅ video2x already installed"
fi
echo

# Install btcli if not present
if ! command -v btcli &> /dev/null; then
    echo "📦 Installing Bittensor CLI..."
    pip3 install bittensor --quiet
    echo "✅ btcli installed"
else
    echo "✅ btcli already installed"
fi
echo

# Clone vidaio-subnet repository
INSTALL_DIR="${INSTALL_DIR:-$HOME/vidaio-subnet}"

if [ -d "$INSTALL_DIR" ]; then
    echo "📁 vidaio-subnet already exists at $INSTALL_DIR"
    read -p "   Overwrite? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$INSTALL_DIR"
    else
        echo "⏭️  Skipping repository clone"
        INSTALL_DIR=""
    fi
fi

if [ -n "$INSTALL_DIR" ]; then
    echo "📦 Cloning vidaio-subnet repository..."
    git clone https://github.com/VidAIo/vidaio-subnet.git "$INSTALL_DIR" --quiet
    cd "$INSTALL_DIR"
    echo "✅ Repository cloned to $INSTALL_DIR"
    echo
    
    # Create Python virtual environment
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    # Install Python dependencies
    echo "📦 Installing Python dependencies (this may take a few minutes)..."
    pip install --upgrade pip setuptools wheel --quiet
    pip install -r requirements.txt --quiet
    
    # Install bittensor 9.12.2 (CRITICAL: NOT 10.x, breaks API)
    pip install bittensor==9.12.2 --quiet
    
    echo "✅ Python dependencies installed"
    echo
    
    # Apply VMAF patch
    echo "🔧 Applying VMAF calculation patch..."
    PATCH_FILE="$(dirname "$0")/../patches/validator_merger_vmaf.patch"
    
    if [ -f "$PATCH_FILE" ]; then
        # Backup original
        cp services/compress/validator_merger.py services/compress/validator_merger.py.backup
        
        # Apply patch
        patch -p1 < "$PATCH_FILE" --quiet
        
        echo "✅ VMAF patch applied (backup saved)"
    else
        echo "⚠️  WARNING: VMAF patch file not found, will need manual application"
    fi
    echo
fi

# Summary
echo "=========================================="
echo "✅ Installation Complete!"
echo "=========================================="
echo
echo "📋 Next Steps:"
echo "   1. Set up storage (BackBlaze B2 or Hippius)"
echo "   2. Create/import TAO wallet"
echo "   3. Register miners on SN85"
echo "   4. Start mining!"
echo
echo "🔧 Installation Directory: $INSTALL_DIR"
echo "🎮 GPU: $GPU_INFO"
echo "🌐 Environment: $ENV"
echo
echo "Run ./scripts/register.sh to continue setup"
echo
