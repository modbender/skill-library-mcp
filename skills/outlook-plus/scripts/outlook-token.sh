#!/bin/bash
# Outlook Token Manager
# Usage: outlook-token.sh [--account NAME] [refresh|get|test|list]

BASE_DIR="$HOME/.outlook-mcp"

# Parse --account flag
ACCOUNT="${OUTLOOK_ACCOUNT:-default}"
if [ "$1" = "--account" ] || [ "$1" = "-a" ]; then
    ACCOUNT="$2"
    shift 2
fi

# Handle 'list' command before checking config
if [ "$1" = "list" ]; then
    echo "Configured accounts:"
    for dir in "$BASE_DIR"/*/; do
        if [ -f "$dir/credentials.json" ]; then
            name=$(basename "$dir")
            echo "  - $name"
        fi
    done
    exit 0
fi

# Migrate legacy config (no subdirectory) to "default"
if [ -f "$BASE_DIR/credentials.json" ] && [ ! -d "$BASE_DIR/default" ]; then
    mkdir -p "$BASE_DIR/default"
    mv "$BASE_DIR/config.json" "$BASE_DIR/default/" 2>/dev/null
    mv "$BASE_DIR/credentials.json" "$BASE_DIR/default/" 2>/dev/null
    echo "Migrated existing config to 'default' account"
fi

CONFIG_DIR="$BASE_DIR/$ACCOUNT"
CONFIG_FILE="$CONFIG_DIR/config.json"
CREDS_FILE="$CONFIG_DIR/credentials.json"

# Check if config exists
if [ ! -f "$CONFIG_FILE" ] || [ ! -f "$CREDS_FILE" ]; then
    echo "Error: Account '$ACCOUNT' not configured."
    echo "Run: outlook-setup.sh --account $ACCOUNT"
    echo ""
    echo "Available accounts:"
    for dir in "$BASE_DIR"/*/; do
        [ -f "$dir/credentials.json" ] && echo "  - $(basename "$dir")"
    done
    exit 1
fi

# Load credentials
CLIENT_ID=$(jq -r '.client_id' "$CONFIG_FILE")
CLIENT_SECRET=$(jq -r '.client_secret' "$CONFIG_FILE")
ACCESS_TOKEN=$(jq -r '.access_token' "$CREDS_FILE")
REFRESH_TOKEN=$(jq -r '.refresh_token' "$CREDS_FILE")

case "$1" in
    refresh)
        echo "Refreshing token for '$ACCOUNT'..."
        RESPONSE=$(curl -s -X POST "https://login.microsoftonline.com/common/oauth2/v2.0/token" \
            -H "Content-Type: application/x-www-form-urlencoded" \
            -d "client_id=$CLIENT_ID&client_secret=$CLIENT_SECRET&refresh_token=$REFRESH_TOKEN&grant_type=refresh_token&scope=https://graph.microsoft.com/Mail.ReadWrite https://graph.microsoft.com/Mail.Send https://graph.microsoft.com/Calendars.ReadWrite offline_access")
        
        if echo "$RESPONSE" | jq -e '.access_token' > /dev/null 2>&1; then
            echo "$RESPONSE" > "$CREDS_FILE"
            echo "Token refreshed successfully"
        else
            echo "Error refreshing token:"
            echo "$RESPONSE" | jq '.error_description // .'
            exit 1
        fi
        ;;
    
    get)
        # Require explicit --confirm flag to prevent accidental token exposure
        if [ "$2" != "--confirm" ]; then
            echo "⚠️  This command prints sensitive OAuth access tokens." >&2
            echo "To confirm, run: outlook-token.sh get --confirm" >&2
            exit 1
        fi
        echo "⚠️  WARNING: Access tokens are sensitive credentials. Do not share or log this output." >&2
        echo "$ACCESS_TOKEN"
        ;;
    
    test)
        echo "Testing connection for '$ACCOUNT'..."
        RESULT=$(curl -s "https://graph.microsoft.com/v1.0/me/mailFolders/inbox" \
            -H "Authorization: Bearer $ACCESS_TOKEN")
        
        if echo "$RESULT" | jq -e '.totalItemCount' > /dev/null 2>&1; then
            TOTAL=$(echo "$RESULT" | jq '.totalItemCount')
            UNREAD=$(echo "$RESULT" | jq '.unreadItemCount')
            echo "✓ Connected! Inbox: $TOTAL emails ($UNREAD unread)"
        else
            echo "✗ Connection failed. Try: outlook-token.sh --account $ACCOUNT refresh"
            echo "$RESULT" | jq '.error.message // .'
            exit 1
        fi
        ;;
    
    *)
        echo "Usage: outlook-token.sh [--account NAME] <command>"
        echo ""
        echo "Commands:"
        echo "  refresh - Refresh the access token"
        echo "  get     - Print current access token"
        echo "  test    - Test the connection"
        echo "  list    - List configured accounts"
        echo ""
        echo "Options:"
        echo "  --account, -a NAME  Use specific account (default: 'default')"
        echo "  Or set OUTLOOK_ACCOUNT env var"
        ;;
esac
