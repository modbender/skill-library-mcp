#!/bin/bash
# One-line installer for Smart Memory
# Usage: curl -sL https://raw.githubusercontent.com/BluePointDigital/smart-memory/main/install.sh | bash

set -e

echo "🧠 Installing Smart Memory for OpenClaw..."
echo ""

# Detect OpenClaw workspace
if [ -d "$HOME/.openclaw/workspace" ]; then
    WORKSPACE="$HOME/.openclaw/workspace"
elif [ -d "/config/.openclaw/workspace" ]; then
    WORKSPACE="/config/.openclaw/workspace"
else
    echo "❌ Could not find OpenClaw workspace"
    echo "Please run from your OpenClaw workspace directory"
    exit 1
fi

echo "📁 Found workspace: $WORKSPACE"
echo ""

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version $NODE_VERSION found. Please upgrade to 18+"
    exit 1
fi

echo "✅ Node.js $(node --version) found"
echo ""

# Clone or download
echo "📥 Downloading Smart Memory..."
REPO_URL="https://github.com/BluePointDigital/smart-memory"

if command -v git &> /dev/null; then
    # Git available - clone
    cd /tmp
    rm -rf smart-memory-temp 2>/dev/null || true
    git clone --depth 1 "$REPO_URL.git" smart-memory-temp
    
    # Copy files
    cp -r smart-memory-temp/skills/vector-memory "$WORKSPACE/skills/"
    cp -r smart-memory-temp/smart-memory "$WORKSPACE/"
    rm -rf smart-memory-temp
else
    # No git - download tarball
    cd /tmp
    curl -L "$REPO_URL/archive/main.tar.gz" | tar xz
    cp -r smart-memory-main/skills/vector-memory "$WORKSPACE/skills/"
    cp -r smart-memory-main/smart-memory "$WORKSPACE/"
    rm -rf smart-memory-main
fi

echo "✅ Files installed"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
cd "$WORKSPACE/smart-memory"
npm install --silent

echo "✅ Dependencies installed"
echo ""

# Initial sync
echo "🔄 Indexing memory files..."
node smart_memory.js --sync

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Quick test:"
echo "  node smart-memory/smart_memory.js --search 'test query'"
echo ""
echo "To use Focus Mode:"
echo "  node smart-memory/smart_memory.js --focus"
echo ""
echo "The memory_search tool now uses Smart Memory with dual retrieval modes!"
