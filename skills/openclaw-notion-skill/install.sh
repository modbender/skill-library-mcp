#!/bin/bash
# Install script for Notion Skill

echo "📝 Installing Notion Skill for OpenClaw..."

cd "$(dirname "$0")"

# Check if package.json exists (full version) or use standalone
if [ -f "package.json" ]; then
    echo "Installing dependencies..."
    npm install
    npm run build
    echo "✅ Full version installed!"
else
    # Use standalone version
    mv package-standalone.json package.json
    echo "Installing standalone dependencies..."
    npm install
    echo "✅ Standalone version installed!"
fi

echo ""
echo "Next steps:"
echo "1. Add to ~/.openclaw/.env: NOTION_TOKEN=secret_xxxxxxxxxx"
echo "2. Share your Notion pages with the integration (Share → Add connections)"
echo "3. Test: node notion-cli.js test"
echo ""
echo "See SKILL.md for full documentation."
