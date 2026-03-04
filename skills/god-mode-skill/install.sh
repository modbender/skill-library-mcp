#!/bin/bash
# god-mode installation script

set -e

INSTALL_DIR="${HOME}/.local/share/god-mode"
BIN_DIR="${HOME}/.local/bin"

echo "🔭 Installing god-mode..."
echo ""

# Check prerequisites
echo "Checking prerequisites..."
MISSING=""

if ! command -v gh &>/dev/null; then
    MISSING="${MISSING}- gh (GitHub CLI): https://cli.github.com/\n"
fi

if ! command -v sqlite3 &>/dev/null; then
    MISSING="${MISSING}- sqlite3: Usually pre-installed, or 'apt install sqlite3'\n"
fi

if ! command -v jq &>/dev/null; then
    MISSING="${MISSING}- jq: brew install jq / apt install jq\n"
fi

if [ -n "$MISSING" ]; then
    echo "❌ Missing dependencies:"
    echo -e "$MISSING"
    echo "Install them and try again."
    exit 1
fi

echo "✅ All prerequisites found"
echo ""

# Clone or update
if [ -d "$INSTALL_DIR" ]; then
    echo "Updating existing installation..."
    cd "$INSTALL_DIR"
    git pull
else
    echo "Cloning repository..."
    git clone https://github.com/InfantLab/god-mode-skill "$INSTALL_DIR"
fi

# Create bin directory if needed
mkdir -p "$BIN_DIR"

# Symlink executable
echo "Creating symlink..."
ln -sf "$INSTALL_DIR/scripts/god" "$BIN_DIR/god"

# Make executable
chmod +x "$INSTALL_DIR/scripts/god"

echo ""
echo "✅ god-mode installed successfully!"
echo ""
echo "Next steps:"
echo "  1. Run: god setup"
echo "  2. Add a project: god projects add github:your/repo"
echo "  3. Sync data: god sync"
echo "  4. View status: god status"
echo ""

# Check PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "⚠️  Add $BIN_DIR to your PATH:"
    echo ""
    echo "   # Add to ~/.bashrc or ~/.zshrc:"
    echo "   export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
fi

echo "📖 Documentation: https://github.com/InfantLab/god-mode-skill"
