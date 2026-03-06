#!/bin/bash
# install.sh - Mini Diary installation script
# Security: Only copies files and sets safe permissions, no dangerous operations

set -euo pipefail  # Strict mode: exit on error, undefined variables, pipe failures
IFS=$'\n\t'        # Safer word splitting

# Security disclaimer
echo "🔒 Security: This installer only copies files and sets safe permissions" >&2

echo "📦 Installing Mini Diary..."
echo "=========================="

# Check if running in OpenClaw environment
if [ -z "$OPENCLAW_HOME" ]; then
    echo "⚠️  Not running in OpenClaw environment"
    echo "This skill is designed for OpenClaw agents."
    echo "Visit https://openclaw.ai to learn more."
    exit 1
fi

# Determine installation directory
INSTALL_DIR="${OPENCLAW_HOME}/skills/mini-diary"
if [ -z "$INSTALL_DIR" ]; then
    INSTALL_DIR="/root/.openclaw/skills/mini-diary"
fi

echo "Installation directory: $INSTALL_DIR"

# Create directory if it doesn't exist
mkdir -p "$INSTALL_DIR"

# Copy all files
echo "📄 Copying files..."
cp -r ./* "$INSTALL_DIR/" 2>/dev/null || true

# Make scripts executable (safe mode - only if files exist and are owned by user)
if [ -d "$INSTALL_DIR/scripts" ]; then
    for script in "$INSTALL_DIR/scripts/"*.sh; do
        if [ -f "$script" ] && [ -O "$script" ]; then  # -O checks if file is owned by effective user
            chmod 755 "$script"
            echo "  ✓ $(basename "$script") set to 755"
        else
            echo "  ⚠️  Skipping $(basename "$script") - not owned by user"
        fi
    done
fi

# Create default diary file if it doesn't exist
DEFAULT_DIARY="$HOME/diary.md"
if [ ! -f "$DEFAULT_DIARY" ]; then
    echo "📓 Creating default diary file: $DEFAULT_DIARY"
    cp "$INSTALL_DIR/templates/diary_template.md" "$DEFAULT_DIARY"
    echo "✅ Default diary created"
fi

# Create configuration example
CONFIG_EXAMPLE="$HOME/.mini-diary-example.sh"
cat > "$CONFIG_EXAMPLE" << 'EOF'
# Mini Diary Configuration Example
# Copy to ~/.mini-diary-config.sh and customize

# Diary file location
export DIARY_FILE="$HOME/diary.md"

# NextCloud sync directory (optional)
# export NEXTCLOUD_SYNC_DIR="/path/to/nextcloud/diary"

# Custom tags configuration (optional)
# export TAGS_CONFIG="$HOME/.mini-diary-tags.json"

# Debug mode (optional)
# export MINI_DIARY_DEBUG=1

# Add to your shell profile:
# source ~/.mini-diary-config.sh
EOF

echo "⚙️  Configuration example created: $CONFIG_EXAMPLE"

# Installation complete
echo ""
echo "✅ Mini Diary installation complete!"
echo ""
echo "Quick start:"
echo "1. Configure environment variables:"
echo "   source $CONFIG_EXAMPLE"
echo ""
echo "2. Add your first note:"
echo "   mini-diary add \"My first note with Mini Diary\""
echo ""
echo "3. Search your diary:"
echo "   mini-diary search --stats"
echo "   mini-diary search --tag \"📅\""
echo ""
echo "📚 Documentation:"
echo "- View SKILL.md for detailed usage"
echo "- Check examples/ for sample diary"
echo "- Read templates/ for customization"
echo ""
echo "Need help? Create an issue at:"
echo "https://github.com/PrintXDreams/mini-diary/issues"
echo ""
echo "Happy journaling! 📓✨"