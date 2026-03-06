#!/bin/bash
# Publish Scrapling skill to ClawHub

cd "$(dirname "$0")"

echo "========================================="
echo "Publishing Scrapling Skill to ClawHub"
echo "========================================="
echo ""

# Check if logged in
if ! clawhub whoami >/dev/null 2>&1; then
    echo "⚠️  Not logged in to ClawHub"
    echo ""
    echo "Opening browser for authentication..."
    echo "This will:"
    echo "  1. Open your browser to clawhub.com"
    echo "  2. You'll sign in (GitHub, Google, or email)"
    echo "  3. Grant access to the CLI"
    echo "  4. Return here to continue"
    echo ""
    read -p "Press Enter to open browser for login..."
    
    clawhub login
    
    if [ $? -ne 0 ]; then
        echo "❌ Login failed"
        exit 1
    fi
fi

# Show current user
echo ""
echo "✅ Logged in as: $(clawhub whoami)"
echo ""

# Publish
echo "Publishing skill..."
echo ""

clawhub publish .

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "✅ Successfully published to ClawHub!"
    echo "========================================="
    echo ""
    echo "The skill should now appear in the Gateway UI when you:"
    echo "  1. Refresh the Skills page"
    echo "  2. Search for 'scrapling'"
    echo ""
    echo "Or install via CLI:"
    echo "  clawhub install scrapling"
else
    echo ""
    echo "❌ Publish failed"
    exit 1
fi
