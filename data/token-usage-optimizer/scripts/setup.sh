#!/bin/bash
# Setup wizard for token-usage-optimizer

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
TOKEN_FILE="$BASE_DIR/.tokens"

echo "🔧 Token Usage Optimizer Setup"
echo ""
echo "You need OAuth tokens from Claude Code CLI."
echo "See references/token-extraction.md for instructions."
echo ""

# Check if already configured
if [ -f "$TOKEN_FILE" ]; then
  echo "⚠️  Tokens already configured in $TOKEN_FILE"
  read -p "Overwrite? (y/N): " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
  fi
fi

# Prompt for access token
echo "1️⃣  Enter your Access Token (sk-ant-oat01-...):"
read -r ACCESS_TOKEN

if [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ Access token required"
  exit 1
fi

# Prompt for refresh token
echo ""
echo "2️⃣  Enter your Refresh Token (sk-ant-ort01-...):"
read -r REFRESH_TOKEN

if [ -z "$REFRESH_TOKEN" ]; then
  echo "⚠️  No refresh token provided (optional but recommended)"
fi

# Save to file
cat > "$TOKEN_FILE" <<EOF
# Claude Code OAuth Tokens
# Generated: $(date)

ACCESS_TOKEN="$ACCESS_TOKEN"
REFRESH_TOKEN="$REFRESH_TOKEN"
EOF

chmod 600 "$TOKEN_FILE"

echo ""
echo "✅ Tokens saved to $TOKEN_FILE"
echo ""
echo "Next steps:"
echo "  ./scripts/check-usage.sh   # Check your usage"
echo "  ./scripts/report.sh        # Human-readable report"
echo ""
echo "To integrate with heartbeat, add to HEARTBEAT.md:"
echo "  $BASE_DIR/scripts/report.sh"
