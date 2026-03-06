#!/bin/bash
# 01-check-dependencies.sh
# Checks all required dependencies before installing Claude Code

set -e

echo "🔍 Checking Claude Code dependencies..."
echo ""

ERRORS=0

# Check OS
OS=$(uname -s)
echo "📦 Operating System: $OS"
if [[ "$OS" != "Darwin" && "$OS" != "Linux" ]]; then
    echo "   ❌ Claude Code requires macOS or Linux"
    ERRORS=$((ERRORS + 1))
else
    echo "   ✅ Supported OS"
fi

# Check Node.js (required for claude-mem)
echo ""
echo "📦 Node.js:"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "   ✅ Installed: $NODE_VERSION"
    
    # Check if version is >= 18
    NODE_MAJOR=$(echo "$NODE_VERSION" | sed 's/v//' | cut -d. -f1)
    if [[ "$NODE_MAJOR" -lt 18 ]]; then
        echo "   ⚠️  Warning: Node.js 18+ recommended for claude-mem"
    fi
else
    echo "   ⚠️  Not installed (optional, needed for claude-mem)"
fi

# Check Bun (required for claude-mem)
echo ""
echo "📦 Bun:"
if command -v bun &> /dev/null; then
    BUN_VERSION=$(bun --version)
    echo "   ✅ Installed: $BUN_VERSION"
else
    echo "   ⚠️  Not installed (optional, needed for claude-mem)"
    echo "   Install: curl -fsSL https://bun.sh/install | bash"
fi

# Check Git
echo ""
echo "📦 Git:"
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    echo "   ✅ $GIT_VERSION"
else
    echo "   ❌ Git not installed (required)"
    ERRORS=$((ERRORS + 1))
fi

# Check curl
echo ""
echo "📦 curl:"
if command -v curl &> /dev/null; then
    echo "   ✅ Installed"
else
    echo "   ❌ curl not installed (required for installation)"
    ERRORS=$((ERRORS + 1))
fi

# Check existing Claude Code installation
echo ""
echo "📦 Claude Code:"
if [[ -f ~/.local/bin/claude ]]; then
    CLAUDE_VERSION=$(~/.local/bin/claude --version 2>/dev/null || echo "unknown")
    echo "   ✅ Already installed: $CLAUDE_VERSION"
    echo "   Location: ~/.local/bin/claude"
else
    echo "   ℹ️  Not installed yet"
fi

# Check PATH
echo ""
echo "📦 PATH configuration:"
if [[ ":$PATH:" == *":$HOME/.local/bin:"* ]]; then
    echo "   ✅ ~/.local/bin is in PATH"
else
    echo "   ⚠️  ~/.local/bin not in PATH"
    echo "   Add to your shell config: export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

# Check disk space
echo ""
echo "📦 Disk space:"
AVAILABLE=$(df -h ~ | awk 'NR==2 {print $4}')
echo "   Available: $AVAILABLE"

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [[ $ERRORS -eq 0 ]]; then
    echo "✅ All required dependencies satisfied!"
    echo "Run: ./02-install-claude-code.sh"
    exit 0
else
    echo "❌ $ERRORS required dependency issue(s) found"
    echo "Please fix the issues above before installing"
    exit 1
fi
