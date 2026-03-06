#!/bin/bash
# Twilio Skill Setup Script
# Sets up environment variables and installs dependencies

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Twilio Skill Setup"
echo "===================="
echo ""

# Check if .env file exists
if [ -f "$SKILL_DIR/.env" ]; then
    echo "✓ .env file found"
else
    echo "⚠ .env file not found. Creating from template..."
    cp "$SKILL_DIR/.env.example" "$SKILL_DIR/.env"
    echo "✓ Created .env file"
    echo ""
    echo "📝 Please edit the .env file with your credentials:"
    echo "   vim $SKILL_DIR/.env"
    echo ""
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r "$SKILL_DIR/requirements.txt" > /dev/null 2>&1
echo "✓ Dependencies installed"

# Check if credentials are set
if [ -z "$TWILIO_ACCOUNT_SID" ]; then
    echo ""
    echo "⚠ Loading credentials from .env..."
    set -a
    source "$SKILL_DIR/.env"
    set +a
fi

# Validate credentials
if [ -z "$TWILIO_ACCOUNT_SID" ] || [ "$TWILIO_ACCOUNT_SID" = "your_account_sid_here" ]; then
    echo ""
    echo "❌ TWILIO_ACCOUNT_SID not configured"
    echo "   Edit $SKILL_DIR/.env and set your credentials"
    exit 1
fi

if [ -z "$TWILIO_AUTH_TOKEN" ] || [ "$TWILIO_AUTH_TOKEN" = "your_auth_token_here" ]; then
    echo ""
    echo "❌ TWILIO_AUTH_TOKEN not configured"
    echo "   Edit $SKILL_DIR/.env and set your credentials"
    exit 1
fi

if [ -z "$TWILIO_PHONE_NUMBER" ] || [ "$TWILIO_PHONE_NUMBER" = "+1234567890" ]; then
    echo ""
    echo "❌ TWILIO_PHONE_NUMBER not configured"
    echo "   Edit $SKILL_DIR/.env and set your credentials"
    exit 1
fi

echo ""
echo "✓ Credentials loaded successfully"
echo ""
echo "📝 Configuration Summary:"
echo "   Account SID: ${TWILIO_ACCOUNT_SID:0:10}..."
echo "   Phone Number: $TWILIO_PHONE_NUMBER"
echo ""
echo "✅ Setup complete!"
echo ""
echo "Ready to use:"
echo "   python $SKILL_DIR/call.py --phone '+1234567890' --message 'Hello'"
echo "   python $SKILL_DIR/sms.py --phone '+1234567890' --message 'Hello'"
echo ""
echo "💡 Tip: Add this to your ~/.bashrc or ~/.zshrc to load credentials automatically:"
echo "   source $SKILL_DIR/.env"
echo ""
