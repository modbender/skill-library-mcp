#!/usr/bin/env bash
# Garmin Health Analysis - Clawdbot Skill Installation
# Run this after cloning the skill to your Clawdbot skills directory

set -e  # Exit on error

echo "🏃 Installing Garmin Health Analysis Skill..."
echo

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not found"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Install Python dependencies
echo
echo "📦 Installing Python dependencies..."

if pip3 install --user garminconnect fitparse gpxpy 2>/dev/null; then
    echo "✓ Dependencies installed (--user)"
elif pip3 install --break-system-packages garminconnect fitparse gpxpy 2>/dev/null; then
    echo "✓ Dependencies installed (--break-system-packages)"
elif pip3 install garminconnect fitparse gpxpy 2>/dev/null; then
    echo "✓ Dependencies installed (system-wide)"
else
    echo "❌ Failed to install Python dependencies"
    echo "   Try manually: pip3 install --user garminconnect fitparse gpxpy"
    exit 1
fi

# Create config from example if it doesn't exist
if [ ! -f "config.json" ] && [ -f "config.example.json" ]; then
    echo
    echo "📝 Creating config.json from example..."
    cp config.example.json config.json
    echo "✓ config.json created (edit with your credentials)"
fi

# Success
echo
echo "✅ Installation complete!"
echo
echo "Next steps:"
echo "  1. Add your Garmin credentials:"
echo "     - Edit config.json, or"
echo "     - Set GARMIN_EMAIL and GARMIN_PASSWORD env vars, or"
echo "     - Add to ~/.clawdbot/clawdbot.json skills config"
echo
echo "  2. Authenticate:"
echo "     python3 scripts/garmin_auth.py login"
echo
echo "  3. Test:"
echo "     python3 scripts/garmin_data.py summary --days 7"
echo
echo "📖 Read SKILL.md for full documentation"
