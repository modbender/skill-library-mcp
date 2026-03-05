#!/bin/bash
# PhoenixShield Install Script
# Installs phoenix-shield to system PATH

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/usr/local/bin"
BINARY_NAME="phoenix-shield"

echo "🔥 PhoenixShield Installer"
echo "=========================="

# Check if running as root for system install
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Note: Installing to user bin (~/.local/bin) without sudo"
    INSTALL_DIR="$HOME/.local/bin"
    mkdir -p "$INSTALL_DIR"
fi

# Copy binary
echo "📦 Installing $BINARY_NAME to $INSTALL_DIR..."
cp "$SCRIPT_DIR/scripts/phoenix-shield" "$INSTALL_DIR/$BINARY_NAME"
chmod +x "$INSTALL_DIR/$BINARY_NAME"

# Create config directory
echo "📁 Creating config directories..."
mkdir -p /var/backups/phoenix 2>/dev/null || mkdir -p "$HOME/.phoenix/backups"

# Check if in PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo ""
    echo "⚠️  $INSTALL_DIR is not in your PATH"
    echo "   Add this to your ~/.bashrc or ~/.zshrc:"
    echo "   export PATH=\"$INSTALL_DIR:\$PATH\""
fi

echo ""
echo "✅ PhoenixShield installed successfully!"
echo ""
echo "Usage:"
echo "  phoenix-shield init myproject"
echo "  phoenix-shield --help"
echo ""
