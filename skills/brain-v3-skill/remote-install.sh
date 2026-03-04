#!/bin/bash
# ClawBrain Remote Installer
# Usage: curl -fsSL https://raw.githubusercontent.com/clawcolab/clawbrain/main/remote-install.sh | bash
# 
# ⚠️  SECURITY WARNING ⚠️
# This script downloads and executes code from the internet.
# For production use, consider manual installation:
#   git clone https://github.com/clawcolab/clawbrain.git
#   cd clawbrain && ./install.sh

set -e

echo "🧠 ClawBrain Remote Installer"
echo "=============================="
echo ""
echo "⚠️  Security Notice:"
echo "This script will download and execute code from GitHub."
echo "For production environments, we recommend manual installation:"
echo "  git clone https://github.com/clawcolab/clawbrain.git"
echo "  cd clawbrain && ./install.sh"
echo ""
read -p "Continue with automated installation? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 0
fi
echo ""

# Detect skills directory - check for existing skills directories first
SKILLS_DIR=""

# Check existing skills directories in priority order
for dir in "$HOME/clawd/skills" "$HOME/.openclaw/skills" "$HOME/.clawdbot/skills"; do
    if [ -d "$dir" ]; then
        SKILLS_DIR="$dir"
        break
    fi
done

# If no skills dir found, create one based on config
if [ -z "$SKILLS_DIR" ]; then
    if [ -d "$HOME/clawd" ]; then
        mkdir -p "$HOME/clawd/skills"
        SKILLS_DIR="$HOME/clawd/skills"
    elif [ -d "$HOME/.openclaw" ]; then
        mkdir -p "$HOME/.openclaw/skills"
        SKILLS_DIR="$HOME/.openclaw/skills"
    elif [ -d "$HOME/.clawdbot" ]; then
        mkdir -p "$HOME/.clawdbot/skills"
        SKILLS_DIR="$HOME/.clawdbot/skills"
    else
        # Default fallback
        mkdir -p "$HOME/clawd/skills"
        SKILLS_DIR="$HOME/clawd/skills"
    fi
fi

echo "📁 Installing to: $SKILLS_DIR/clawbrain"

# Clone or update
if [ -d "$SKILLS_DIR/clawbrain" ]; then
    echo "📥 Updating existing installation..."
    cd "$SKILLS_DIR/clawbrain"
    git fetch --all
    git checkout feature/openclaw-plugin-integration 2>/dev/null || git checkout main
    git pull
else
    echo "📥 Cloning clawbrain..."
    git clone -b feature/openclaw-plugin-integration https://github.com/clawcolab/clawbrain.git "$SKILLS_DIR/clawbrain" 2>/dev/null || \
    git clone https://github.com/clawcolab/clawbrain.git "$SKILLS_DIR/clawbrain"
    cd "$SKILLS_DIR/clawbrain"
fi

# Display commit information for transparency
echo ""
echo "📋 Installation Details:"
echo "Repository: https://github.com/clawcolab/clawbrain"
echo "Commit: $(git rev-parse HEAD)"
echo "Date: $(git log -1 --format=%cd)"
echo "Author: $(git log -1 --format=%an)"
echo ""

# Run local installer
chmod +x install.sh
./install.sh
