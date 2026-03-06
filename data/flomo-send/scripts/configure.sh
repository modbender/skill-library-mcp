#!/bin/bash
#
# configure.sh - Interactive setup for flomo-send skill
#
# This script runs during skill installation to configure user preferences.
#

set -e

echo "📝 Flomo Skill Configuration"
echo "============================"
echo ""

# Check if running in interactive mode
if [ ! -t 0 ]; then
    echo "Note: Non-interactive mode detected. Skipping configuration."
    echo "To configure later, run: ./scripts/configure.sh"
    exit 0
fi

# Ask if user has flomo PRO account
echo "Do you have a flomo PRO account? (y/n)"
read -r HAS_PRO

case "$HAS_PRO" in
    [Yy]*)
        echo ""
        echo "✅ PRO account selected"
        echo ""
        echo "Please enter your flomo webhook token."
        echo "You can find it at: https://flomoapp.com/mine?source=incoming_webhook"
        echo ""
        read -rp "Webhook token (or full URL): " WEBHOOK_INPUT
        
        if [ -z "$WEBHOOK_INPUT" ]; then
            echo "⚠️  No webhook provided. You can configure it later by running this script again."
            exit 0
        fi
        
        # Detect if user pasted full URL or just token
        if echo "$WEBHOOK_INPUT" | grep -q "^https://flomoapp.com/iwh/"; then
            # Full URL provided
            WEBHOOK_URL="$WEBHOOK_INPUT"
            WEBHOOK_TOKEN=$(echo "$WEBHOOK_URL" | sed 's|https://flomoapp.com/iwh/||')
            echo ""
            echo "✅ Webhook URL configured"
        else
            # Just token provided
            WEBHOOK_TOKEN="$WEBHOOK_INPUT"
            WEBHOOK_URL="https://flomoapp.com/iwh/$WEBHOOK_TOKEN"
            echo ""
            echo "✅ Webhook token configured"
        fi
        
        # Determine shell config file for display
        SHELL_CONFIG=""
        if [ -n "$ZSH_VERSION" ] || [ -f "$HOME/.zshrc" ]; then
            SHELL_CONFIG="$HOME/.zshrc"
        elif [ -n "$BASH_VERSION" ]; then
            if [ -f "$HOME/.bash_profile" ]; then
                SHELL_CONFIG="$HOME/.bash_profile"
            else
                SHELL_CONFIG="$HOME/.bashrc"
            fi
        fi
        
        echo ""
        echo "Where would you like to save the configuration?"
        echo "1) Create a local .env file in skill directory (default - recommended)"
        echo "2) Shell config file ($SHELL_CONFIG)"
        read -rp "Choice [1-2] (default: 1): " CONFIG_CHOICE
        
        # Default to option 1 if empty
        CONFIG_CHOICE=${CONFIG_CHOICE:-1}
        
        case "$CONFIG_CHOICE" in
            2)
                # Save to shell config
                if [ -n "$SHELL_CONFIG" ]; then
                    echo "" >> "$SHELL_CONFIG"
                    echo "# Flomo Skill Configuration" >> "$SHELL_CONFIG"
                    echo "export FLOMO_WEBHOOK_TOKEN=$WEBHOOK_TOKEN" >> "$SHELL_CONFIG"
                    echo ""
                    echo "✅ Configuration saved to: $SHELL_CONFIG"
                    echo "   Please run: source $SHELL_CONFIG"
                else
                    echo "⚠️  Could not detect shell config file."
                    echo "   Please manually add to your shell config:"
                    echo "   export FLOMO_WEBHOOK_TOKEN=$WEBHOOK_TOKEN"
                fi
                ;;
            *)
                # Save to .env file (default)
                ENV_FILE="$(dirname "$0")/../.env"
                echo "# Flomo Skill Configuration" > "$ENV_FILE"
                echo "FLOMO_WEBHOOK_TOKEN=$WEBHOOK_TOKEN" >> "$ENV_FILE"
                echo "# FLOMO_WEBHOOK_URL=$WEBHOOK_URL" >> "$ENV_FILE"
                chmod 600 "$ENV_FILE"
                echo ""
                echo "✅ Configuration saved to: $ENV_FILE"
                echo "   The .env file has been created with restricted permissions (600)"
                echo "   This is the recommended option - keeps config isolated to this skill."
                ;;
        esac
        
        echo ""
        echo "🎉 Configuration complete!"
        echo "   You can now use the flomo_send.sh script with webhook fallback."
        ;;
    
    [Nn]*)
        echo ""
        echo "✅ Free account selected"
        echo "   The skill will use URL Scheme only (requires flomo app on macOS)."
        echo "   If you upgrade to PRO later, run: ./scripts/configure.sh"
        ;;
    
    *)
        echo ""
        echo "⚠️  Invalid input. Skipping configuration."
        echo "   You can run this script later to configure: ./scripts/configure.sh"
        exit 0
        ;;
esac

echo ""
echo "📖 Quick start:"
echo "   ./scripts/flomo_send.sh \"Your note\" \"#tag1 #tag2\""
