#!/bin/bash
#
# Crypto Scam Detector - Silent Installation Script
# Installs all dependencies without verbose output
#

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Silent mode - redirect output
exec 3>&1
exec 4>&2
exec 1>/dev/null 2>&1

# Print to user (bypass silent mode)
print_msg() {
    echo "$1" >&3
}

# Check Python 3
if ! command -v python3 &> /dev/null; then
    print_msg "❌ Python 3 is required but not installed"
    exit 1
fi

print_msg "🔍 Installing Crypto Scam Detector..."

# Create virtual environment if it doesn't exist
if [ ! -d "$SKILL_DIR/venv" ]; then
    python3 -m venv "$SKILL_DIR/venv"
fi

# Activate and install dependencies
source "$SKILL_DIR/venv/bin/activate"
pip install --upgrade pip
pip install -r "$SKILL_DIR/requirements.txt"

# Make scripts executable
chmod +x "$SKILL_DIR/crypto_check.py" 2>/dev/null || true
chmod +x "$SKILL_DIR/setup.sh" 2>/dev/null || true

# Restore output
exec 1>&3
exec 2>&4

# Success message
echo ""
echo "✅ Crypto Scam Detector installed successfully!"
echo ""
echo "🛡️  Ready to protect your crypto transactions"
echo "🔍 Detects: Phishing, Honeypots, Rug Pulls, Ponzi schemes"
echo "📊 Multi-source verification with live blockchain data"
echo ""
echo "💡 Tip: Add your Etherscan API key for enhanced analysis"
echo "   Run: ./setup.sh"
echo "   Get free key: https://etherscan.io/myapikey"
echo ""
