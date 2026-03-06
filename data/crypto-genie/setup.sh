#!/bin/bash
# Setup script for Crypto Genie
# Helps users configure API key securely

cd "$(dirname "$0")"

echo "=================================================="
echo "🔐 Crypto Genie - Secure Setup"
echo "=================================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please run install.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run setup wizard
python secure_key_manager.py

echo ""
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Start the server: ./start.sh"
echo "2. Use OpenClaw to check crypto addresses"
echo ""
echo "Your API key is encrypted and stored securely."
echo "The skill will work automatically!"
echo ""
