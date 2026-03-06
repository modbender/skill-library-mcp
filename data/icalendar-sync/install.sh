#!/bin/bash
# Installation script for iCalendar Sync skill
# Security hardened version with error handling

set -e

SKILL_NAME="icalendar-sync"
SKILL_DIR="$HOME/.openclaw/skills/$SKILL_NAME"
MIN_PYTHON_VERSION="3.8"

echo "🚀 Installing iCalendar Sync for OpenClaw..."
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found"
    exit 1
fi

python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Python $python_version detected"

# Validate Python version
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "✓ Python version meets requirements (>= $MIN_PYTHON_VERSION)"
else
    echo "❌ Error: Python $MIN_PYTHON_VERSION or higher is required"
    echo "   Current version: $python_version"
    exit 1
fi

# Create skill directory
mkdir -p "$SKILL_DIR"
echo "✓ Created skill directory: $SKILL_DIR"

# Copy files
echo "📦 Copying skill files..."
cp -r src/ requirements.txt skill.yaml setup.py README.md LICENSE "$SKILL_DIR/"

# Install dependencies with error checking
echo "📥 Installing dependencies..."
if pip install -r "$SKILL_DIR/requirements.txt"; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Error: Failed to install dependencies"
    echo "   Please check your Python environment and try again"
    exit 1
fi

# Create CLI command directory
mkdir -p "$HOME/.local/bin"

# Check if command already exists
if [ -f "$HOME/.local/bin/icalendar-sync" ]; then
    echo "⚠️  Command 'icalendar-sync' already exists"
    read -p "   Overwrite? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "   Skipping CLI installation"
        echo ""
        echo "✅ Installation complete (CLI not updated)!"
        exit 0
    fi
fi

# Create CLI command (SECURITY: No more 'source .env' - using python-dotenv)
echo "🔗 Creating CLI command..."
cat > "$HOME/.local/bin/icalendar-sync" << 'EOF'
#!/usr/bin/env python3
# Secure wrapper for icalendar-sync
# Uses python-dotenv instead of bash source for security

import sys
import os
from pathlib import Path

# Add skill to Python path
skill_dir = Path.home() / '.openclaw' / 'skills' / 'icalendar-sync' / 'src'
sys.path.insert(0, str(skill_dir))

# Load environment safely using python-dotenv
try:
    from dotenv import load_dotenv
    env_file = Path.home() / '.openclaw' / '.env'
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    # python-dotenv not available, skip env loading
    pass

# Run the actual script with error handling
if __name__ == '__main__':
    try:
        from icalendar_sync import calendar
        calendar.main()
    except ImportError as e:
        print(f"Error: Could not import icalendar_sync module: {e}")
        print("Please ensure the skill is properly installed.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
EOF

chmod +x "$HOME/.local/bin/icalendar-sync"

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Make sure ~/.local/bin is in your PATH"
echo "  2. Run: icalendar-sync setup"
echo "  3. Enter your iCloud credentials"
echo "  4. Test: icalendar-sync list"
echo ""
echo "Security note: Credentials are stored securely using system keyring"
echo ""