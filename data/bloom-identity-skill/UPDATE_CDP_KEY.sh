#!/bin/bash
# This script helps convert .env keys to JSON format

echo "⚠️  This will create coinbase_cloud_api_key.json"
echo ""
echo "Option 1 (RECOMMENDED): Download from CDP Portal"
echo "  1. Visit https://portal.cdp.coinbase.com/"
echo "  2. Go to API Keys"
echo "  3. Download your key as JSON"
echo "  4. Rename to: coinbase_cloud_api_key.json"
echo ""
echo "Option 2: Use keys from .env (if you have the private key)"
echo "  - You need the FULL private key (BEGIN/END format)"
echo "  - Not just the CDP_API_KEY_SECRET"
echo ""
echo "Do you want to:"
echo "  1) I'll download from CDP Portal (recommended)"
echo "  2) Exit and I'll do it manually"
echo ""
read -p "Choice (1 or 2): " choice

if [ "$choice" = "1" ]; then
  echo ""
  echo "✅ Great! Please:"
  echo "   1. Go to https://portal.cdp.coinbase.com/"
  echo "   2. Download your API key JSON"
  echo "   3. Save it as: coinbase_cloud_api_key.json"
  echo ""
  echo "Then run: npm run build && node dist/index.js --user-id test"
else
  echo "✅ OK, you can manually create the JSON file."
fi
