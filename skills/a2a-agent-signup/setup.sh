#!/bin/bash
# Setup script for a2a-agent-signup CLI command
# Run this after installing the skill: bash setup.sh

SKILL_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BIN_DIR="$HOME/bin"

# Create ~/bin if it doesn't exist
mkdir -p "$BIN_DIR"

# Install dependencies
cd "$SKILL_DIR"
npm install --quiet

# Create symlink
ln -sf "$SKILL_DIR/index.js" "$BIN_DIR/a2a-agent-signup"
chmod +x "$SKILL_DIR/index.js"

echo "✓ a2a-agent-signup linked to $BIN_DIR/a2a-agent-signup"

# Add ~/bin to PATH in ~/.bashrc if not already there
if ! grep -q 'export PATH="$HOME/bin:\$PATH"' ~/.bashrc; then
  echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
  echo "✓ Added ~/bin to ~/.bashrc"
fi

# Run the wizard
echo ""
echo "✓ Setup complete! Starting a2a-agent-signup..."
echo ""

# Run the script directly
node "$SKILL_DIR/index.js"
