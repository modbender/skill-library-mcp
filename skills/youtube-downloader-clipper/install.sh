#!/bin/bash

# ClawHub YouTube Clipping Skill Installer
# This script installs the skill to Claude Code's skills directory

set -e

echo "🎬 Installing ClawHub YouTube Clipping Skill..."

# Define paths
SKILL_DIR="$HOME/.claude/skills/clawhub"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create skills directory if it doesn't exist
mkdir -p "$SKILL_DIR"

# Copy skill files
echo "📁 Copying skill files to $SKILL_DIR..."
cp "$SOURCE_DIR/skill.json" "$SKILL_DIR/"
cp "$SOURCE_DIR/prompt.md" "$SKILL_DIR/"
cp "$SOURCE_DIR/README.md" "$SKILL_DIR/"

echo "✅ Skill files installed successfully!"

# Check for yt-dlp
echo ""
echo "🔍 Checking for dependencies..."
if command -v yt-dlp &> /dev/null; then
    echo "✅ yt-dlp is installed ($(yt-dlp --version | head -n1))"
else
    echo "❌ yt-dlp is NOT installed"
    echo ""
    echo "Please install yt-dlp:"
    echo "  macOS:   brew install yt-dlp"
    echo "  Linux:   sudo apt install yt-dlp"
    echo "  Pip:     pip install yt-dlp"
fi

# Check for ffmpeg (optional but recommended)
if command -v ffmpeg &> /dev/null; then
    echo "✅ ffmpeg is installed (optional, for advanced clipping)"
else
    echo "⚠️  ffmpeg is not installed (optional, but recommended for clipping)"
    echo "   Install: brew install ffmpeg"
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Usage: /clawhub <youtube-url> [options]"
echo "Example: /clawhub https://youtube.com/watch?v=xxx --clip 00:30-02:15"
