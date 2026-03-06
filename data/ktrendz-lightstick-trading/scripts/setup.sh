#!/bin/bash
# K-Trendz API Key Setup

CONFIG_DIR="$HOME/.config/ktrendz"
CONFIG_FILE="$CONFIG_DIR/config.json"

echo "🎤 K-Trendz Lightstick Trading Setup"
echo "======================================"
echo ""

# Check if already configured
if [ -f "$CONFIG_FILE" ]; then
    echo "✓ Existing configuration found"
    read -p "Reconfigure? (y/N): " reconfigure
    if [ "$reconfigure" != "y" ] && [ "$reconfigure" != "Y" ]; then
        echo "Setup cancelled."
        exit 0
    fi
fi

# Check environment variable
if [ -n "$KTRENDZ_API_KEY" ]; then
    echo "✓ Found KTRENDZ_API_KEY in environment"
    API_KEY="$KTRENDZ_API_KEY"
else
    echo "Enter your K-Trendz API key"
    echo "(Get one from the K-Trendz team)"
    echo ""
    read -sp "API Key: " API_KEY
    echo ""
fi

if [ -z "$API_KEY" ]; then
    echo "✗ API key is required"
    exit 1
fi

# Validate API key by calling token-price
echo ""
echo "Validating API key..."

RESPONSE=$(curl -s -X POST "https://k-trendz.com/api/bot/token-price" \
    -H "Content-Type: application/json" \
    -H "x-bot-api-key: $API_KEY" \
    -d '{"artist_name": "RIIZE"}')

if echo "$RESPONSE" | grep -q '"success":true'; then
    echo "✓ API key validated successfully"
else
    echo "✗ Invalid API key or API error"
    echo "Response: $RESPONSE"
    exit 1
fi

# Save configuration
mkdir -p "$CONFIG_DIR"
cat > "$CONFIG_FILE" << EOF
{
    "api_key": "$API_KEY",
    "base_url": "https://k-trendz.com/api/bot",
    "configured_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF

chmod 600 "$CONFIG_FILE"

echo ""
echo "✓ Configuration saved to $CONFIG_FILE"
echo ""
echo "You're ready to trade! Try:"
echo "  ./scripts/price.sh RIIZE"
echo "  ./scripts/buy.sh RIIZE"
