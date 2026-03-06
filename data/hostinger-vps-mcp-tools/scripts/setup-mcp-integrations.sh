#!/bin/bash
# Setup MCP Integrations (Zapier, Pipedream)
# Usage: ./setup-mcp-integrations.sh [ZAPIER_MCP_URL] [PIPEDREAM_API_KEY]
# Run as root or koda user

set -e

ZAPIER_URL="$1"
PIPEDREAM_KEY="$2"

KODA_HOME="/home/koda"
MCP_CONFIG="$KODA_HOME/.config/mcporter/mcporter.json"

echo "🔌 Setting up MCP Integrations"
echo "==============================="

# Install mcporter
echo "[1/3] Installing mcporter..."
npm install -g mcporter

# Create config directory
mkdir -p "$(dirname "$MCP_CONFIG")"

# Initialize config
cat > "$MCP_CONFIG" << 'EOF'
{
  "servers": {}
}
EOF

# Add Zapier if provided
if [ -n "$ZAPIER_URL" ]; then
    echo "[2/3] Configuring Zapier MCP..."
    mcporter config add zapier --url "$ZAPIER_URL" --config "$MCP_CONFIG"
    echo "  ✓ Zapier connected"
else
    echo "[2/3] Skipping Zapier (no URL provided)"
fi

# Add Pipedream if provided
if [ -n "$PIPEDREAM_KEY" ]; then
    echo "[3/3] Configuring Pipedream MCP..."
    mcporter config add pipedream \
        --url "https://api.pipedream.com/v1/connect/mcp" \
        --header "Authorization: Bearer $PIPEDREAM_KEY" \
        --config "$MCP_CONFIG"
    echo "  ✓ Pipedream connected"
else
    echo "[3/3] Skipping Pipedream (no API key provided)"
fi

chown -R koda:koda "$KODA_HOME/.config"

echo ""
echo "✅ MCP integrations configured!"
echo ""
echo "Test with:"
echo "  mcporter list --config $MCP_CONFIG"
echo "  mcporter list zapier --schema --config $MCP_CONFIG"
echo ""
echo "Available integrations:"
mcporter list --config "$MCP_CONFIG" 2>/dev/null || echo "  (run as koda user to list)"
