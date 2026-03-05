#!/bin/bash
# 03-first-time-auth.sh
# Guides user through first-time Claude Code authentication

set -e

CLAUDE_BIN="${HOME}/.local/bin/claude"

echo "🔐 Claude Code First-Time Authentication"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check installation
if [[ ! -f "$CLAUDE_BIN" ]]; then
    echo "❌ Claude Code not installed!"
    echo "Run: ./02-install-claude-code.sh first"
    exit 1
fi

# Check existing auth
echo "🔍 Checking current auth status..."
if $CLAUDE_BIN auth status &>/dev/null; then
    echo "✅ Already authenticated!"
    $CLAUDE_BIN auth status
    echo ""
    read -p "Re-authenticate? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

echo ""
echo "📋 Authentication Options:"
echo ""
echo "1. Browser Login (recommended)"
echo "   - Opens browser to authenticate with your Anthropic account"
echo "   - Works with personal and team accounts"
echo ""
echo "2. API Key"
echo "   - Use an API key from console.anthropic.com"
echo "   - Good for CI/CD or headless environments"
echo ""

read -p "Choose method (1 or 2): " -n 1 -r METHOD
echo ""
echo ""

case $METHOD in
    1)
        echo "🌐 Starting browser authentication..."
        echo ""
        echo "A browser window will open. Log in with your Anthropic account."
        echo "If the browser doesn't open, copy the URL shown and open it manually."
        echo ""
        read -p "Press Enter to continue..."
        $CLAUDE_BIN auth login
        ;;
    2)
        echo "🔑 API Key Authentication"
        echo ""
        echo "Get your API key from: https://console.anthropic.com/settings/keys"
        echo ""
        read -p "Enter your API key: " -s API_KEY
        echo ""
        
        if [[ -z "$API_KEY" ]]; then
            echo "❌ No API key provided"
            exit 1
        fi
        
        # Set API key
        export ANTHROPIC_API_KEY="$API_KEY"
        
        # Test it
        echo "Testing API key..."
        if $CLAUDE_BIN --version &>/dev/null; then
            echo "✅ API key works!"
            echo ""
            echo "Add to your shell config to persist:"
            echo "export ANTHROPIC_API_KEY=\"$API_KEY\""
        else
            echo "❌ API key test failed"
            exit 1
        fi
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Verifying authentication..."

if $CLAUDE_BIN auth status &>/dev/null; then
    echo "✅ Authentication successful!"
    echo ""
    $CLAUDE_BIN auth status
else
    echo "⚠️  Could not verify auth status"
    echo "Try running: claude auth status"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Run: ./04-install-subagents.sh (install dev team)"
echo "2. Run: ./05-setup-claude-mem.sh (optional memory)"
echo "3. Start coding: cd your-project && claude"
