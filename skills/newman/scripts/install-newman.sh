#!/bin/bash
# Newman installation and verification script
# Usage: ./install-newman.sh [--global|--local]

set -e

INSTALL_TYPE="${1:---global}"

echo "🚀 Installing Newman..."

if [ "$INSTALL_TYPE" = "--global" ]; then
    echo "Installing globally (requires sudo/root if needed)..."
    npm install -g newman newman-reporter-htmlextra
    
    echo ""
    echo "✅ Newman installed globally!"
    echo ""
    newman --version
    
elif [ "$INSTALL_TYPE" = "--local" ]; then
    echo "Installing locally to current directory..."
    
    if [ ! -f "package.json" ]; then
        npm init -y
    fi
    
    npm install --save-dev newman newman-reporter-htmlextra
    
    echo ""
    echo "✅ Newman installed locally!"
    echo ""
    npx newman --version
    
    echo ""
    echo "Add to package.json scripts:"
    echo '  "test": "newman run collections/api-tests.json"'
    
else
    echo "❌ Invalid option: $INSTALL_TYPE"
    echo "Usage: $0 [--global|--local]"
    exit 1
fi

echo ""
echo "📦 Installed reporters:"
newman run --reporters 2>&1 | grep -A 20 "reporters:" || echo "- cli (built-in)"
echo "- htmlextra (installed)"

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Export your Postman collection (v2.1 format)"
echo "2. Export your environment (if using variables)"
echo "3. Run: newman run your-collection.json -e your-environment.json"
