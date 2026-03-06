#!/bin/bash
# Setup script for ChaosChain OpenClaw Skill
# Run this after installing the skill via ClawHub

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SKILL_DIR="$( dirname "$SCRIPT_DIR" )"

echo "🔧 Setting up ChaosChain OpenClaw Skill..."
echo "   Skill directory: $SKILL_DIR"

# Create virtual environment
if [ ! -d "$SKILL_DIR/.venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv "$SKILL_DIR/.venv"
fi

# Activate and install dependencies
echo "📚 Installing dependencies..."
source "$SKILL_DIR/.venv/bin/activate"
pip install --quiet --upgrade pip
pip install --quiet -r "$SKILL_DIR/requirements.txt"

# Make wrapper scripts executable
echo "🔑 Making scripts executable..."
chmod +x "$SCRIPT_DIR"/*.py 2>/dev/null || true

echo ""
echo "✅ ChaosChain skill setup complete!"
echo ""
echo "📖 Available commands:"
echo "   /chaoschain verify <agent_id>    - Verify agent identity"
echo "   /chaoschain reputation <agent_id> - Get reputation breakdown"
echo "   /chaoschain whoami               - Check your own identity"
echo "   /chaoschain register             - Register as ERC-8004 agent"
echo ""
echo "🔗 Explorer: https://8004scan.io"
