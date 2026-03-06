#!/bin/bash
# iapctl installation script for OpenClaw
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/iapctl/venv"
VENV_BIN="$VENV_DIR/bin"

echo "📦 Installing iapctl..."

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install dependencies
echo "📥 Installing dependencies..."
cd "$SCRIPT_DIR/iapctl"
pip install -e . 'scrapli[paramiko]'

# Create wrapper script
echo "🔗 Creating wrapper script..."
cat > /opt/homebrew/bin/iapctl << WRAPPEREOF
#!/bin/bash
# Wrapper script for iapctl
source "$VENV_DIR/bin/activate"
python -m iapctl.cli "\$@"
WRAPPEREOF

# Make wrapper executable
chmod +x /opt/homebrew/bin/iapctl

# Create symlink to venv
ln -sf "$VENV_DIR" /opt/homebrew/iapctl-venv

echo ""
echo "✅ iapctl installed successfully!"
echo ""
echo "📌 Location: /opt/homebrew/bin/iapctl"
echo "🧹 To uninstall: rm /opt/homebrew/bin/iapctl /opt/homebrew/iapctl-venv"
echo ""
echo "🚀 Quick start:"
echo "  iapctl discover --cluster test-iap --vc 192.168.20.56 --out ./out"
echo "  iapctl snapshot --cluster test-iap --vc 192.168.20.56 --out ./out"
echo ""
