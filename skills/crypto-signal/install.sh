#!/bin/bash
# Install crypto-signal CLI
set -e

INSTALL_DIR="${OPENCLAW_SKILLS_DIR:-$HOME/.openclaw/skills}/crypto-signal"
mkdir -p "$INSTALL_DIR"

# Copy CLI script
cp "$(dirname "$0")/crypto-signal.py" "$INSTALL_DIR/crypto-signal.py"
chmod +x "$INSTALL_DIR/crypto-signal.py"

# Create wrapper
cat > /usr/local/bin/crypto-signal << 'EOF'
#!/bin/bash
python3 "${OPENCLAW_SKILLS_DIR:-$HOME/.openclaw/skills}/crypto-signal/crypto-signal.py" "$@"
EOF
chmod +x /usr/local/bin/crypto-signal

echo "✅ crypto-signal installed. Set CRYPTOSIGNAL_API_KEY to get started."
echo "   Get your free key at https://cryptosignal.pro"
