#!/bin/bash
# 02-install-claude-code.sh
# Installs Claude Code CLI

set -e

echo "🚀 Installing Claude Code..."
echo ""

# Check if already installed
if [[ -f ~/.local/bin/claude ]]; then
    CURRENT_VERSION=$(~/.local/bin/claude --version 2>/dev/null || echo "unknown")
    echo "⚠️  Claude Code already installed: $CURRENT_VERSION"
    read -p "Reinstall/update? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping installation."
        exit 0
    fi
fi

# Create directory
mkdir -p ~/.local/bin

# Download and install
echo "📥 Downloading Claude Code..."
curl -fsSL https://claude.ai/install.sh | sh

# Verify installation
echo ""
echo "🔍 Verifying installation..."
if [[ -f ~/.local/bin/claude ]]; then
    VERSION=$(~/.local/bin/claude --version 2>/dev/null || echo "unknown")
    echo "✅ Claude Code installed successfully!"
    echo "   Version: $VERSION"
    echo "   Location: ~/.local/bin/claude"
else
    echo "❌ Installation failed - claude binary not found"
    exit 1
fi

# Check PATH
echo ""
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "⚠️  Add ~/.local/bin to your PATH:"
    echo ""
    echo "   For bash (~/.bashrc):"
    echo "   export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    echo "   For zsh (~/.zshrc):"
    echo "   export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    echo "   Then restart your terminal or run: source ~/.zshrc"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Run: ./03-first-time-auth.sh"
echo "2. Or start directly: ~/.local/bin/claude"
