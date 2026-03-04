#!/bin/bash
# Twilio Emergency Call Setup Script
# Author: Micheal Sun

CONFIG_DIR="$HOME/.openclaw/workspace/telcall-twilio/config"
CONFIG_FILE="$CONFIG_DIR/twilio.json"

echo "📞 Twilio Emergency Call - Setup"
echo "=================================="
echo ""

# Create config directory
mkdir -p "$CONFIG_DIR"

# Check if config already exists
if [ -f "$CONFIG_FILE" ]; then
    echo "⚠️  Configuration already exists."
    read -p "Overwrite? (y/N): " overwrite
    if [[ ! "$overwrite" =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi
fi

echo "Please enter your Twilio credentials:"
echo ""

# Get Account SID
read -p "Account SID (AC...): " account_sid
if [ -z "$account_sid" ]; then
    echo "❌ Account SID is required"
    exit 1
fi

# Get Auth Token
read -p "Auth Token: " auth_token
if [ -z "$auth_token" ]; then
    echo "❌ Auth Token is required"
    exit 1
fi

# Get Twilio phone number
read -p "Twilio Phone Number (e.g., +15551234567): " from_number
if [ -z "$from_number" ]; then
    echo "❌ Twilio phone number is required"
    exit 1
fi

# Get destination phone number
read -p "Your Phone Number (e.g., +8613812345678): " to_number
if [ -z "$to_number" ]; then
    echo "❌ Your phone number is required"
    exit 1
fi

# Save configuration
cat > "$CONFIG_FILE" << EOF
{
    "account_sid": "$account_sid",
    "auth_token": "$auth_token",
    "from_number": "$from_number",
    "to_number": "$to_number"
}
EOF

# Set secure permissions
chmod 600 "$CONFIG_FILE"

echo ""
echo "✅ Configuration saved to: $CONFIG_FILE"
echo ""
echo "📋 Summary:"
echo "   Twilio Number: $from_number"
echo "   Destination:   $to_number"
echo ""
echo "🧪 Test your setup with:"
echo "   bash ~/.openclaw/workspace/telcall-twilio/scripts/call.sh \"Test message\""
