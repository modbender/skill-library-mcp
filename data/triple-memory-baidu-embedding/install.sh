#!/bin/bash
# Installation script for Triple Memory System with Baidu Embedding
# Installs the skill to the Clawdbot skills directory

set -e

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$HOME/clawd/skills/triple-memory-baidu-embedding"

echo "🚀 Installing Triple Memory System with Baidu Embedding..."

# Check if source exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Source directory not found: $SOURCE_DIR"
    exit 1
fi

# Create skills directory if it doesn't exist
mkdir -p "$HOME/clawd/skills/"

# Check if target already exists and backup if needed
if [ -d "$TARGET_DIR" ]; then
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_DIR="${TARGET_DIR}_backup_$TIMESTAMP"
    echo "⚠️  Target already exists, backing up to: $BACKUP_DIR"
    mv "$TARGET_DIR" "$BACKUP_DIR"
fi

# Copy the skill
echo "📁 Copying skill files..."
cp -r "$SOURCE_DIR" "$HOME/clawd/skills/triple-memory-baidu-embedding"

# Set permissions
echo "🔒 Setting permissions..."
chmod +x "$HOME/clawd/skills/triple-memory-baidu-embedding/scripts/baidu-memory-tools.sh"
chmod +x "$HOME/clawd/skills/triple-memory-baidu-embedding/scripts/triple-integration.sh"

# Check dependencies
echo "🔍 Checking dependencies..."

MISSING_DEPS=()

if [ ! -d "$HOME/clawd/skills/git-notes-memory" ]; then
    MISSING_DEPS+=("git-notes-memory")
fi

if [ ! -d "$HOME/clawd/skills/memory-baidu-embedding-db" ]; then
    MISSING_DEPS+=("memory-baidu-embedding-db")
fi

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo "⚠️  Missing dependencies:"
    for dep in "${MISSING_DEPS[@]}"; do
        echo "   - $dep"
    done
    echo ""
    echo "💡 Install missing dependencies with:"
    for dep in "${MISSING_DEPS[@]}"; do
        echo "   clawdhub install $dep"
    done
    echo ""
fi

echo "✅ Installation completed!"
echo "📁 Skill installed to: $HOME/clawd/skills/triple-memory-baidu-embedding"
echo ""
echo "📋 Next steps:"
echo "   1. Ensure dependencies are installed: git-notes-memory, memory-baidu-embedding-db"
echo "   2. Configure Baidu API credentials (optional but recommended):"
echo "      export BAIDU_API_STRING='your_bce_v3_api_string'"
echo "      export BAIDU_SECRET_KEY='your_secret_key'"
echo "      Note: Without API credentials, system will operate in degraded mode"
echo "   3. Test the installation:"
echo "      bash $HOME/clawd/skills/triple-memory-baidu-embedding/scripts/triple-integration.sh status"