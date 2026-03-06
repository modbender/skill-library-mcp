#!/bin/bash

# TRIZ Systematic Innovation Skill Installer
set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.openclaw/skills"

echo "Installing TRIZ Systematic Innovation skill..."

# Create skills directory if it doesn't exist
mkdir -p "$INSTALL_DIR"

# Copy all skill files
cp "$SKILL_DIR/SKILL.md" "$INSTALL_DIR/triz.SKILL.md"
cp "$SKILL_DIR/triz.js" "$INSTALL_DIR/triz.js"
cp "$SKILL_DIR/package.json" "$INSTALL_DIR/triz.package.json"
cp "$SKILL_DIR/README.md" "$INSTALL_DIR/triz.README.md"

# Make the CLI executable
chmod +x "$INSTALL_DIR/triz.js"

# Create symlink for easy access
ln -sf "$INSTALL_DIR/triz.js" "$HOME/.npm-global/bin/triz" 2>/dev/null || true

echo "TRIZ Systematic Innovation skill installed successfully!"
echo "Usage: triz --help"