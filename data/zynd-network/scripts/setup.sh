#!/usr/bin/env bash
# Setup script for the Zynd OpenClaw skill.
# Installs the zyndai-agent Python SDK and its dependencies.

set -e

echo "================================================"
echo "  Zynd AI Network - Skill Setup"
echo "================================================"
echo ""

# Check for python3
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 is not installed or not on PATH."
    echo "Install Python 3.12+ from https://python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python version: $PYTHON_VERSION"

# Check for pip
if ! python3 -m pip --version &> /dev/null; then
    echo "ERROR: pip is not available. Install pip first."
    exit 1
fi

echo ""
echo "Installing zyndai-agent SDK..."
python3 -m pip install --quiet --upgrade "zyndai-agent>=0.2.2"

echo ""
echo "Verifying installation..."
python3 -c "import zyndai_agent; print(f'zyndai-agent installed successfully')" 2>/dev/null

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================"
    echo "  Setup complete!"
    echo "================================================"
    echo ""
    echo "Next steps:"
    echo "  1. Get your API key from https://dashboard.zynd.ai"
    echo "  2. Set ZYND_API_KEY in your environment or OpenClaw skills config"
    echo "  3. Register your agent with zynd_register.py"
    echo ""
else
    echo ""
    echo "ERROR: Installation verification failed."
    echo "Try running: python3 -m pip install zyndai-agent"
    exit 1
fi
