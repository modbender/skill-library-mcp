#!/usr/bin/env bash
# Install are.na CLI

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/bin"
mkdir -p "$BIN_DIR"

# Copy the arena script
cp "$SCRIPT_DIR/arena" "$BIN_DIR/arena"
chmod +x "$BIN_DIR/arena"

echo "✓ Installed to $BIN_DIR/arena"
echo ""
echo "Add to PATH:"
echo "  echo 'export PATH=\"\$HOME/bin:\$PATH\"' >> ~/.zshrc"
echo ""
echo "Usage:"
echo "  arena auth YOUR_TOKEN"
echo "  arena me"
