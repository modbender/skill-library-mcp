#!/bin/bash
# Outlook Token Management - Delegate Version
# Usage: outlook-token.sh <command>
#
# Uses tenant-specific endpoints (not /common)
# Supports auto-detection of tenant_id during setup

CONFIG_DIR="$HOME/.outlook-mcp"
CONFIG_FILE="$CONFIG_DIR/config.json"
CREDS_FILE="$CONFIG_DIR/credentials.json"

# Ensure config directory exists with secure permissions
ensure_config_dir() {
    if [ ! -d "$CONFIG_DIR" ]; then
        mkdir -p "$CONFIG_DIR"
    fi
    chmod 700 "$CONFIG_DIR"
}

# Secure write to credentials file
write_credentials() {
    local CONTENT="$1"
    ensure_config_dir
    echo "$CONTENT" > "$CREDS_FILE"
    chmod 600 "$CREDS_FILE"
}

# Load config
CLIENT_ID=$(jq -r '.client_id' "$CONFIG_FILE" 2>/dev/null)
CLIENT_SECRET=$(jq -r '.client_secret' "$CONFIG_FILE" 2>/dev/null)
TENANT_ID=$(jq -r '.tenant_id' "$CONFIG_FILE" 2>/dev/null)
OWNER_EMAIL=$(jq -r '.owner_email' "$CONFIG_FILE" 2>/dev/null)
DELEGATE_EMAIL=$(jq -r '.delegate_email' "$CONFIG_FILE" 2>/dev/null)
TIMEZONE=$(jq -r '.timezone // "UTC"' "$CONFIG_FILE" 2>/dev/null)
REFRESH_TOKEN=$(jq -r '.refresh_token' "$CREDS_FILE" 2>/dev/null)

# Validate tenant_id
if [ -z "$TENANT_ID" ] || [ "$TENANT_ID" = "null" ]; then
    echo '{"error": "No tenant_id in config.json. Add your Microsoft Entra tenant ID."}'
    exit 1
fi

# Token endpoint (tenant-specific, not /common)
TOKEN_URL="https://login.microsoftonline.com/$TENANT_ID/oauth2/v2.0/token"

SCOPE="offline_access User.Read Mail.ReadWrite Mail.Send Mail.ReadWrite.Shared Mail.Send.Shared Calendars.ReadWrite Calendars.ReadWrite.Shared"

case "$1" in
    refresh)
        if [ -z "$REFRESH_TOKEN" ] || [ "$REFRESH_TOKEN" = "null" ]; then
            echo '{"error": "No refresh token. Complete the authorization flow first."}'
            exit 1
        fi
        
        if [ -z "$CLIENT_ID" ] || [ "$CLIENT_ID" = "null" ]; then
            echo '{"error": "No client_id in config.json"}'
            exit 1
        fi
        
        if [ -z "$CLIENT_SECRET" ] || [ "$CLIENT_SECRET" = "null" ]; then
            echo '{"error": "No client_secret in config.json"}'
            exit 1
        fi
        
        # Refresh token using tenant-specific endpoint
        # POST data sent via stdin to avoid exposing secrets in process list
        RESPONSE=$(printf 'client_id=%s&client_secret=%s&refresh_token=%s&grant_type=refresh_token&scope=%s' \
            "$CLIENT_ID" "$CLIENT_SECRET" "$REFRESH_TOKEN" "$SCOPE" | \
            curl -s -X POST "$TOKEN_URL" --data @-)
        
        if echo "$RESPONSE" | jq -e '.access_token' > /dev/null 2>&1; then
            write_credentials "$RESPONSE"
            EXPIRES=$(echo "$RESPONSE" | jq '.expires_in')
            echo "{\"status\": \"token refreshed\", \"expires_in\": $EXPIRES, \"tenant\": \"$TENANT_ID\"}"
        else
            echo "$RESPONSE" | jq '{error: .error_description // .error // "Unknown error"}'
        fi
        ;;
    
    test)
        ACCESS_TOKEN=$(jq -r '.access_token' "$CREDS_FILE" 2>/dev/null)
        
        if [ -z "$ACCESS_TOKEN" ] || [ "$ACCESS_TOKEN" = "null" ]; then
            echo '{"error": "No access token. Run refresh or complete setup."}'
            exit 1
        fi
        
        # Secure auth header file
        AUTH_HEADER_FILE=$(mktemp)
        chmod 600 "$AUTH_HEADER_FILE"
        printf 'header "Authorization: Bearer %s"' "$ACCESS_TOKEN" > "$AUTH_HEADER_FILE"
        
        echo "Testing delegate access..."
        echo "Tenant: $TENANT_ID"
        echo ""
        
        # Test 1: Delegate's own identity
        echo "1. Delegate identity (who is authenticated):"
        DELEGATE_INFO=$(curl -s "https://graph.microsoft.com/v1.0/me" \
            -K "$AUTH_HEADER_FILE")
        
        if echo "$DELEGATE_INFO" | jq -e '.error' > /dev/null 2>&1; then
            echo "$DELEGATE_INFO" | jq '{error: .error.message, code: .error.code}'
            echo ""
            echo "⚠️  Token may be expired. Run: outlook-token.sh refresh"
        else
            echo "$DELEGATE_INFO" | jq '{authenticated_as: .userPrincipalName, display_name: .displayName}'
        fi
        
        echo ""
        
        # Test 2: Access to owner's mailbox
        echo "2. Owner mailbox access ($OWNER_EMAIL):"
        OWNER_INBOX=$(curl -s "https://graph.microsoft.com/v1.0/users/$OWNER_EMAIL/mailFolders/inbox" \
            -K "$AUTH_HEADER_FILE")
        
        if echo "$OWNER_INBOX" | jq -e '.error' > /dev/null 2>&1; then
            echo "$OWNER_INBOX" | jq '{error: .error.message, code: .error.code}'
            echo ""
            echo "⚠️  Cannot access owner's mailbox. Check delegate permissions."
        else
            echo "$OWNER_INBOX" | jq '{status: "OK", folder: .displayName, unread: .unreadItemCount, total: .totalItemCount}'
        fi
        
        echo ""
        
        # Test 3: Access to owner's calendar
        echo "3. Owner calendar access ($OWNER_EMAIL):"
        OWNER_CAL=$(curl -s "https://graph.microsoft.com/v1.0/users/$OWNER_EMAIL/calendar" \
            -K "$AUTH_HEADER_FILE")
        
        if echo "$OWNER_CAL" | jq -e '.error' > /dev/null 2>&1; then
            echo "$OWNER_CAL" | jq '{error: .error.message, code: .error.code}'
            echo ""
            echo "⚠️  Cannot access owner's calendar. Check delegate permissions."
        else
            echo "$OWNER_CAL" | jq '{status: "OK", calendar: .name, canEdit: .canEdit}'
        fi
        
        echo ""
        echo "4. Timezone configured: $TIMEZONE"
        echo ""
        echo "Summary:"
        echo "  Tenant:   $TENANT_ID"
        echo "  Delegate: $DELEGATE_EMAIL"
        echo "  Owner:    $OWNER_EMAIL"
        echo "  Timezone: $TIMEZONE"
        echo "  Mode:     Delegate Access"
        rm -f "$AUTH_HEADER_FILE"
        ;;
    
    get)
        ACCESS_TOKEN=$(jq -r '.access_token' "$CREDS_FILE" 2>/dev/null)
        if [ -z "$ACCESS_TOKEN" ] || [ "$ACCESS_TOKEN" = "null" ]; then
            echo '{"error": "No access token"}'
            exit 1
        fi
        echo "$ACCESS_TOKEN"
        ;;
    
    info)
        OWNER_NAME=$(jq -r '.owner_name // "not set"' "$CONFIG_FILE" 2>/dev/null)
        DELEGATE_NAME=$(jq -r '.delegate_name // "not set"' "$CONFIG_FILE" 2>/dev/null)
        
        echo "Delegate Configuration:"
        echo "  Config dir:     $CONFIG_DIR"
        echo "  Tenant ID:      $TENANT_ID"
        echo "  Client ID:      ${CLIENT_ID:0:8}..."
        echo ""
        echo "  Delegate email: $DELEGATE_EMAIL"
        echo "  Delegate name:  $DELEGATE_NAME"
        echo ""
        echo "  Owner email:    $OWNER_EMAIL"
        echo "  Owner name:     $OWNER_NAME"
        echo ""
        echo "  Timezone:       $TIMEZONE"
        echo ""
        
        if [ -f "$CREDS_FILE" ]; then
            EXPIRES=$(jq -r '.expires_in // "unknown"' "$CREDS_FILE")
            HAS_REFRESH=$(jq -r 'if .refresh_token then "yes" else "no" end' "$CREDS_FILE")
            echo "  Token exists:   yes"
            echo "  Expires in:     $EXPIRES seconds (from last refresh)"
            echo "  Refresh token:  $HAS_REFRESH"
        else
            echo "  Token exists:   no"
        fi
        ;;
    
    auth-url)
        # Generate authorization URL for initial setup
        if [ -z "$CLIENT_ID" ] || [ "$CLIENT_ID" = "null" ]; then
            echo '{"error": "No client_id in config.json"}'
            exit 1
        fi
        
        REDIRECT="http://localhost:8400/callback"
        SCOPE_ENCODED="offline_access%20User.Read%20Mail.ReadWrite%20Mail.Send%20Mail.ReadWrite.Shared%20Mail.Send.Shared%20Calendars.ReadWrite%20Calendars.ReadWrite.Shared"
        
        # Use tenant-specific auth endpoint
        AUTH_URL="https://login.microsoftonline.com/$TENANT_ID/oauth2/v2.0/authorize?client_id=$CLIENT_ID&response_type=code&redirect_uri=$REDIRECT&scope=$SCOPE_ENCODED"
        
        echo "Authorization URL (tenant-specific):"
        echo ""
        echo "$AUTH_URL"
        echo ""
        echo "1. Open this URL in a browser"
        echo "2. Sign in as the DELEGATE account ($DELEGATE_EMAIL)"
        echo "3. Copy the 'code' parameter from the redirect URL"
        echo "4. Run: outlook-token.sh exchange <code>"
        ;;
    
    exchange)
        # Exchange authorization code for tokens
        CODE="$2"
        
        if [ -z "$CODE" ]; then
            echo "Usage: outlook-token.sh exchange <authorization-code>"
            echo ""
            echo "Get the code by running: outlook-token.sh auth-url"
            exit 1
        fi
        
        if [ -z "$CLIENT_ID" ] || [ "$CLIENT_ID" = "null" ]; then
            echo '{"error": "No client_id in config.json"}'
            exit 1
        fi
        
        if [ -z "$CLIENT_SECRET" ] || [ "$CLIENT_SECRET" = "null" ]; then
            echo '{"error": "No client_secret in config.json"}'
            exit 1
        fi
        
        REDIRECT="http://localhost:8400/callback"
        
        # Exchange code using tenant-specific endpoint
        # POST data sent via stdin to avoid exposing secrets in process list
        RESPONSE=$(printf 'client_id=%s&client_secret=%s&code=%s&redirect_uri=%s&grant_type=authorization_code&scope=%s' \
            "$CLIENT_ID" "$CLIENT_SECRET" "$CODE" "$REDIRECT" "$SCOPE" | \
            curl -s -X POST "$TOKEN_URL" --data @-)
        
        if echo "$RESPONSE" | jq -e '.access_token' > /dev/null 2>&1; then
            write_credentials "$RESPONSE"
            
            EXPIRES=$(echo "$RESPONSE" | jq '.expires_in')
            echo "{\"status\": \"authorized\", \"expires_in\": $EXPIRES}"
            echo ""
            echo "Credentials saved to $CREDS_FILE"
            echo "Run 'outlook-token.sh test' to verify access"
        else
            echo "$RESPONSE" | jq '{error: .error_description // .error // "Unknown error"}'
        fi
        ;;
    
    detect-tenant)
        # Auto-detect tenant ID from current token
        ACCESS_TOKEN=$(jq -r '.access_token' "$CREDS_FILE" 2>/dev/null)
        
        if [ -z "$ACCESS_TOKEN" ] || [ "$ACCESS_TOKEN" = "null" ]; then
            echo '{"error": "No access token. Cannot detect tenant."}'
            exit 1
        fi
        
        AUTH_HEADER_FILE=$(mktemp)
        chmod 600 "$AUTH_HEADER_FILE"
        printf 'header "Authorization: Bearer %s"' "$ACCESS_TOKEN" > "$AUTH_HEADER_FILE"
        
        # Get organization info
        ORG_INFO=$(curl -s "https://graph.microsoft.com/v1.0/organization" \
            -K "$AUTH_HEADER_FILE")
        
        if echo "$ORG_INFO" | jq -e '.error' > /dev/null 2>&1; then
            echo '{"error": "Cannot detect tenant. Check token permissions."}'
            exit 1
        fi
        
        DETECTED_TENANT=$(echo "$ORG_INFO" | jq -r '.value[0].id')
        TENANT_NAME=$(echo "$ORG_INFO" | jq -r '.value[0].displayName')
        
        echo "{\"tenant_id\": \"$DETECTED_TENANT\", \"tenant_name\": \"$TENANT_NAME\"}"
        echo ""
        echo "To update config.json, add:"
        echo "  \"tenant_id\": \"$DETECTED_TENANT\""
        rm -f "$AUTH_HEADER_FILE"
        ;;
    
    *)
        echo "Outlook Token Management - Delegate Version"
        echo "Tenant: $TENANT_ID"
        echo ""
        echo "Usage: outlook-token.sh <command>"
        echo ""
        echo "AUTHORIZATION:"
        echo "  auth-url            - Generate authorization URL"
        echo "  exchange <code>     - Exchange auth code for tokens"
        echo ""
        echo "TOKEN MANAGEMENT:"
        echo "  refresh             - Refresh access token"
        echo "  get                 - Print current access token"
        echo "  test                - Test connection to both accounts"
        echo "  info                - Show configuration info"
        echo ""
        echo "UTILITIES:"
        echo "  detect-tenant       - Auto-detect tenant ID from token"
        ;;
esac
