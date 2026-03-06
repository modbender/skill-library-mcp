#!/usr/bin/env bash
# PackageTracker — Setup script
# Creates venv, installs dependencies, and prepares data directory.
#
# Usage: bash scripts/setup.sh
# Run from the skill root: /path/to/package-tracker/

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

echo "📦 Setting up PackageTracker..."
echo "   Skill directory: $SKILL_DIR"

# Create data directory
mkdir -p "$SCRIPT_DIR/data"
echo "✅ Created data/ directory"

# Create venv in scripts/ (next to the Python files)
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv "$SCRIPT_DIR/venv"
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi

# Install dependencies
echo "📥 Installing dependencies..."
"$SCRIPT_DIR/venv/bin/pip" install -q --upgrade pip
"$SCRIPT_DIR/venv/bin/pip" install -q -r "$SCRIPT_DIR/requirements.txt"
echo "✅ Dependencies installed"

# Create .env template if it doesn't exist
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    cat > "$SCRIPT_DIR/.env" << 'EOF'
# 17track API key — Get yours free at https://admin.17track.net
# Free tier: 100 tracking registrations/month, unlimited status checks
SEVENTEEN_TRACK_API_KEY=

# Telegram notifications (optional)
# Create a bot via @BotFather, get chat ID via @userinfobot
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
EOF
    echo "✅ Created .env template — edit scripts/.env to add your API keys"
else
    echo "ℹ️  .env already exists — skipping"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit scripts/.env and add your 17track API key"
echo "  2. Activate: source scripts/venv/bin/activate"
echo "  3. Try:      python scripts/cli.py list"
echo ""
