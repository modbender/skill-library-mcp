#!/bin/bash
set -e

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Error: This skill is macOS-only"
    echo "   Menu bar apps are not supported on Windows or Linux"
    exit 1
fi

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
APP_DIR="$SKILL_DIR/assets/openclaw-menubar"

echo "📦 Installing OpenClaw Menu Bar dependencies..."

if [ ! -d "$APP_DIR" ]; then
    echo "❌ Error: openclaw-menubar not found at $APP_DIR"
    exit 1
fi

cd "$APP_DIR"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm not found. Please install Node.js first."
    echo "   Download from: https://nodejs.org/"
    exit 1
fi

# Install dependencies
npm install

echo "✅ Installation complete!"
echo ""
echo "Next: Run 'scripts/start.sh' to launch the menu bar app"
