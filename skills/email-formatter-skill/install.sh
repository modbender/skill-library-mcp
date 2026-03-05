#!/bin/bash
# Email Formatter Skill - Installation Script
# This script sets up the email formatter skill for AI agents

set -e  # Exit on error

echo "🔧 Email Formatter Skill - Installation Starting..."
echo ""

# Create skill workspace
SKILL_DIR="$HOME/.email-formatter-skill"
echo "📁 Creating skill directory at $SKILL_DIR"
mkdir -p "$SKILL_DIR/scripts"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Copy scripts if they exist
if [ -d "$SCRIPT_DIR/scripts" ]; then
    echo "📋 Copying helper scripts..."
    cp "$SCRIPT_DIR"/scripts/*.py "$SKILL_DIR/scripts/" 2>/dev/null || true
    chmod +x "$SKILL_DIR"/scripts/*.py
fi

# Check Python version
echo ""
echo "🐍 Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✓ Found: $PYTHON_VERSION"
else
    echo "   ✗ Python 3 not found!"
    echo "   The skill will have limited functionality"
fi

# Optional: Try to install Python packages
echo ""
echo "📦 Checking optional dependencies..."
echo "   (These enhance functionality but are not required)"

# Function to check if a Python package is installed
check_package() {
    python3 -c "import $1" 2>/dev/null
    return $?
}

# Try to install optional packages (silently fail if not possible)
if command -v pip3 &> /dev/null; then
    echo "   Installing optional packages..."
    
    # Try with --break-system-packages flag (for newer systems)
    pip3 install --break-system-packages --quiet language-tool-python textstat 2>/dev/null || \
    # Fallback to --user flag
    pip3 install --user --quiet language-tool-python textstat 2>/dev/null || \
    echo "   Note: Could not install optional packages (this is OK)"
    
    # Check what was installed
    if check_package "language_tool_python"; then
        echo "   ✓ language-tool-python installed"
    fi
    
    if check_package "textstat"; then
        echo "   ✓ textstat installed"
    fi
else
    echo "   pip3 not available - skipping optional packages"
fi

# Make scripts executable
if [ -d "$SKILL_DIR/scripts" ]; then
    chmod +x "$SKILL_DIR"/scripts/*.py 2>/dev/null || true
fi

# Create a quick test
echo ""
echo "🧪 Running verification test..."
if python3 -c "print('✓ Python works')" 2>/dev/null; then
    echo "   ✓ Basic Python test passed"
else
    echo "   ✗ Basic Python test failed"
fi

# Test helper scripts
if [ -f "$SKILL_DIR/scripts/security_scan.py" ]; then
    if python3 "$SKILL_DIR/scripts/security_scan.py" "test email" &>/dev/null; then
        echo "   ✓ Security scanner works"
    fi
fi

# Create config file
cat > "$SKILL_DIR/config.txt" << EOF
Email Formatter Skill Configuration
====================================
Installation Date: $(date)
Installation Path: $SKILL_DIR
Python Version: $(python3 --version 2>/dev/null || echo "Not available")

Available Scripts:
- grammar_check.py
- tone_analyzer.py  
- readability.py
- security_scan.py

Usage:
  python3 $SKILL_DIR/scripts/security_scan.py "email text"
  python3 $SKILL_DIR/scripts/grammar_check.py "email text"
  python3 $SKILL_DIR/scripts/tone_analyzer.py "email text"
  python3 $SKILL_DIR/scripts/readability.py "email text"
EOF

echo ""
echo "=" * 60
echo "✅ Email Formatter Skill Installation Complete!"
echo ""
echo "📍 Installation Directory: $SKILL_DIR"
echo "📋 Configuration saved to: $SKILL_DIR/config.txt"
echo ""
echo "🚀 Ready to use! The skill can now format and analyze emails."
echo ""

# Show quick usage
echo "Quick Test:"
echo "  python3 $SKILL_DIR/scripts/security_scan.py 'Hello, this is a test email'"
echo ""

exit 0
