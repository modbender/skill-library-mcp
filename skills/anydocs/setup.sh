#!/bin/bash
# Setup script for anydocs
# Recommended approach: Uses Python virtual environment (isolated, safe)
# Alternative: Use --system-packages flag to install globally (requires caution)

set -e

echo "================================"
echo "anydocs Setup"
echo "================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 is required but not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✓ Python 3 found: $PYTHON_VERSION"

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo "✗ pip3 is required but not installed"
    exit 1
fi

echo "✓ pip3 found"
echo ""

# Determine installation method
if [ "$1" == "--system-packages" ]; then
    echo "⚠️  WARNING: Installing system-wide with --break-system-packages"
    echo "   This can conflict with system package managers."
    echo "   Recommended: Use virtual environment instead."
    echo ""
    
    read -p "Continue? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi
    
    echo "Installing dependencies globally..."
    pip3 install --break-system-packages -r requirements.txt
    VENV_ACTIVE=false
else
    # Default: Use virtual environment (safe, isolated)
    echo "Creating virtual environment (recommended)..."
    python3 -m venv venv
    source venv/bin/activate
    
    echo "✓ Virtual environment activated"
    echo ""
    
    echo "Installing dependencies to venv..."
    pip install -r requirements.txt
    VENV_ACTIVE=true
fi

echo "✓ Dependencies installed"
echo ""

# Run tests
echo "Running tests..."
python3 test_anydocs.py
echo ""

# Make executable
chmod +x anydocs.py
echo "✓ anydocs.py is executable"

# Setup symlink (optional)
if [ "$1" == "--system" ] || [ "$2" == "--system" ]; then
    echo ""
    echo "Installing system-wide symlink..."
    sudo ln -sf "$(pwd)/anydocs.py" /usr/local/bin/anydocs
    echo "✓ anydocs available as 'anydocs' command (requires 'venv' activation)"
fi

echo ""
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""

if [ "$VENV_ACTIVE" = true ]; then
    echo "Virtual environment is ACTIVE."
    echo ""
    echo "Next time you use anydocs, activate the venv:"
    echo "  source venv/bin/activate"
    echo ""
fi

echo "Next steps:"
echo "  1. Configure a documentation site:"
echo "     python3 anydocs.py config vuejs https://vuejs.org https://vuejs.org/sitemap.xml"
echo ""
echo "  2. Build the index:"
echo "     python3 anydocs.py index vuejs"
echo ""
echo "  3. Search!"
echo "     python3 anydocs.py search 'composition api' --profile vuejs"
echo ""
echo "For more examples, see: examples/QUICKSTART.md"
echo ""
echo "Security & Advanced:"
echo "  - For SPA indexing with browser rendering, use: anydocs index <profile> --use-browser"
echo "  - Requires OpenClaw gateway token (see README.md for details)"
echo "  - Browser rendering only works with HTTPS URLs for security"
echo ""
