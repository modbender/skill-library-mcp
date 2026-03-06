#!/bin/bash
set -euo pipefail

# The Others - Device Flow OAuth Helper for mcporter
# This script authenticates using device flow and saves tokens directly to mcporter vault

VAULT_PATH="$HOME/.mcporter/credentials.json"
SERVER_NAME="theothers"
SERVER_URL="https://theothers.richardkemp.uk/mcp"
REGISTER_URL="https://theothers.richardkemp.uk/register"
DEVICE_AUTH_URL="https://theothers.richardkemp.uk/device_authorization"
TOKEN_URL="https://theothers.richardkemp.uk/oauth/token"

# Parse arguments
FORCE=false
for arg in "$@"; do
    case $arg in
        -h|--help)
            cat << EOF
Usage: $(basename "$0") [OPTIONS]

The Others - Device Flow OAuth Helper for mcporter

Authenticates using OAuth device flow and saves tokens for mcporter.

OPTIONS:
    -f, --force     Force re-authentication without prompting (overwrites existing tokens)
    -h, --help      Show this help message and exit

EXAMPLES:
    $(basename "$0")              # Interactive authentication (prompts if tokens exist)
    $(basename "$0") --force      # Force reset (skip prompt)

NOTES:
    - Tokens are saved to ~/.mcporter/credentials.json (vault)
    - Server config is saved to ~/.mcporter/mcporter.json
    - Access tokens expire after 30 minutes; mcporter should auto-refresh
EOF
            exit 0
            ;;
        -f|--force)
            FORCE=true
            ;;
        *)
            echo "Unknown option: $arg"
            echo "Run '$(basename "$0") --help' for usage."
            exit 1
            ;;
    esac
done

# Check dependencies
for cmd in curl jq mcporter; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "Error: '$cmd' is required but not found in PATH." >&2
        exit 1
    fi
done

# Generate vault key hash (matches mcporter's algorithm)
# Descriptor format: {"name":"<serverName>","url":"<serverUrl>","command":null}
generate_vault_key() {
    local server_name="$1"
    local server_url="$2"
    local descriptor="{\"name\":\"$server_name\",\"url\":\"$server_url\",\"command\":null}"
    local hash
    if command -v sha256sum &>/dev/null; then
        hash=$(echo -n "$descriptor" | sha256sum | cut -c1-16)
    else
        hash=$(echo -n "$descriptor" | shasum -a 256 | cut -c1-16)
    fi
    echo "${server_name}|${hash}"
}

VAULT_KEY=$(generate_vault_key "$SERVER_NAME" "$SERVER_URL")

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}The Others - Device Flow OAuth Setup${NC}"
echo

# Ensure server is registered in mcporter config
echo -e "${BLUE}Registering server in mcporter config...${NC}"
if mcporter config get "$SERVER_NAME" &>/dev/null; then
    echo -e "${GREEN}✓ Server already registered${NC}"
else
    if ! mcporter config add "$SERVER_NAME" --url "$SERVER_URL" --auth oauth --scope home >/dev/null; then
        echo -e "${RED}✗ Failed to register server in mcporter config${NC}" >&2
        exit 1
    fi
    echo -e "${GREEN}✓ Server registered in ~/.mcporter/mcporter.json${NC}"
fi
echo

# Check if already authenticated (check vault)
HAS_EXISTING_AUTH=false
if [ -f "$VAULT_PATH" ]; then
    if jq -e --arg key "$VAULT_KEY" '.entries[$key].tokens.access_token // empty' "$VAULT_PATH" >/dev/null 2>&1; then
        HAS_EXISTING_AUTH=true
    fi
fi

if [ "$HAS_EXISTING_AUTH" = true ]; then
    if [ "$FORCE" = true ]; then
        echo -e "${YELLOW}⚠ Existing authentication found - forcing reset${NC}"
    else
        echo -e "${YELLOW}⚠ Existing authentication found${NC}"
        echo "Location: $VAULT_PATH (key: $VAULT_KEY)"
        echo
        read -p "Reset and re-authenticate? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Cancelled."
            exit 0
        fi
    fi
fi

# Step 1: Register OAuth client (reuse existing client_id if available)
echo -e "${BLUE}Step 1: Registering OAuth client...${NC}"

EXISTING_CLIENT_ID=""
EXISTING_CLIENT_SECRET=""
if [ -f "$VAULT_PATH" ]; then
    EXISTING_CLIENT_ID=$(jq -r --arg key "$VAULT_KEY" '.entries[$key].clientInfo.client_id // empty' "$VAULT_PATH" 2>/dev/null) || true
    EXISTING_CLIENT_SECRET=$(jq -r --arg key "$VAULT_KEY" '.entries[$key].clientInfo.client_secret // empty' "$VAULT_PATH" 2>/dev/null) || true
fi

if [ -n "$EXISTING_CLIENT_ID" ]; then
    CLIENT_ID="$EXISTING_CLIENT_ID"
    CLIENT_SECRET="$EXISTING_CLIENT_SECRET"
    CLIENT_ISSUED_AT=$(jq -r --arg key "$VAULT_KEY" '.entries[$key].clientInfo.client_id_issued_at // 0' "$VAULT_PATH" 2>/dev/null) || true
    echo -e "${GREEN}✓ Reusing existing client: $CLIENT_ID${NC}"
else
    if ! CLIENT_RESPONSE=$(curl -sf -X POST "$REGISTER_URL" \
      -H "Content-Type: application/json" \
      -d '{
        "client_name": "mcporter (device flow)",
        "grant_types": ["urn:ietf:params:oauth:grant-type:device_code", "refresh_token"],
        "scope": "offers:read offers:write",
        "token_endpoint_auth_method": "none"
      }'); then
        echo -e "${RED}✗ Failed to register OAuth client${NC}" >&2
        exit 1
    fi

    CLIENT_ID=$(echo "$CLIENT_RESPONSE" | jq -r '.client_id')
    CLIENT_SECRET=$(echo "$CLIENT_RESPONSE" | jq -r '.client_secret')
    CLIENT_ISSUED_AT=$(date +%s)

    if [ -z "$CLIENT_ID" ] || [ "$CLIENT_ID" = "null" ]; then
        echo -e "${RED}✗ Client registration failed${NC}" >&2
        echo "$CLIENT_RESPONSE" | jq '.' >&2
        exit 1
    fi

    echo -e "${GREEN}✓ Client registered: $CLIENT_ID${NC}"
fi
echo

# Step 2: Initiate device flow
echo -e "${BLUE}Step 2: Initiating device authorization...${NC}"
if ! DEVICE_RESPONSE=$(curl -sf -X POST "$DEVICE_AUTH_URL" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=$CLIENT_ID&scope=offers:read+offers:write"); then
    echo -e "${RED}✗ Failed to initiate device flow${NC}" >&2
    exit 1
fi

DEVICE_CODE=$(echo "$DEVICE_RESPONSE" | jq -r '.device_code')
USER_CODE=$(echo "$DEVICE_RESPONSE" | jq -r '.user_code')
VERIFICATION_URI=$(echo "$DEVICE_RESPONSE" | jq -r '.verification_uri_complete // .verification_uri')
INTERVAL=$(echo "$DEVICE_RESPONSE" | jq -r '.interval // 5')

if [ -z "$DEVICE_CODE" ] || [ "$DEVICE_CODE" = "null" ]; then
    echo -e "${RED}✗ Device authorization failed${NC}" >&2
    echo "$DEVICE_RESPONSE" | jq '.' >&2
    exit 1
fi

echo -e "${GREEN}✓ Device authorization initiated${NC}"
echo
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Please authorize this device:${NC}"
echo
echo -e "  ${GREEN}1. Visit: ${VERIFICATION_URI}${NC}"
echo -e "  ${GREEN}2. Enter code: ${USER_CODE}${NC}"
echo
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# Step 3: Poll for token
echo -e "${BLUE}Waiting for authorization...${NC}"
MAX_ATTEMPTS=180  # 180 attempts × 5 seconds = 900 seconds = 15 minutes
ATTEMPT=0
ACCESS_TOKEN=""

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    sleep "$INTERVAL"
    ATTEMPT=$((ATTEMPT + 1))

    TOKEN_RESPONSE=$(curl -s -X POST "$TOKEN_URL" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "grant_type=urn:ietf:params:oauth:grant-type:device_code&device_code=$DEVICE_CODE&client_id=$CLIENT_ID") || true

    # Check if we got tokens
    ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.access_token // empty' 2>/dev/null) || true

    if [ -n "$ACCESS_TOKEN" ]; then
        echo
        echo -e "${GREEN}✓ Authorization successful!${NC}"
        break
    fi

    # Check for error (can be at top level or in detail object)
    ERROR=$(echo "$TOKEN_RESPONSE" | jq -r '.error // .detail.error // empty' 2>/dev/null) || true

    if [ "$ERROR" = "authorization_pending" ]; then
        echo -n "."
        continue
    elif [ "$ERROR" = "slow_down" ]; then
        INTERVAL=$((INTERVAL + 5))
        echo -n "."
        continue
    elif [ -n "$ERROR" ] && [ "$ERROR" != "null" ]; then
        echo
        ERROR_DESC=$(echo "$TOKEN_RESPONSE" | jq -r '.error_description // .detail.error_description // "No description"' 2>/dev/null) || true
        echo -e "${RED}✗ Authorization failed: $ERROR - $ERROR_DESC${NC}" >&2
        exit 1
    fi
done
echo

if [ -z "$ACCESS_TOKEN" ]; then
    echo -e "${RED}✗ Authorization timeout${NC}" >&2
    exit 1
fi

# Step 4: Save tokens to vault
echo -e "${BLUE}Step 4: Saving tokens to vault...${NC}"

REFRESH_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.refresh_token // empty')
TOKEN_TYPE=$(echo "$TOKEN_RESPONSE" | jq -r '.token_type // "bearer"')
EXPIRES_IN=$(echo "$TOKEN_RESPONSE" | jq -r '.expires_in // 1800')
SCOPE=$(echo "$TOKEN_RESPONSE" | jq -r '.scope // "offers:read offers:write"')
UPDATED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Ensure vault directory exists
mkdir -p "$(dirname "$VAULT_PATH")"

# Read existing vault or create new one
if [ -f "$VAULT_PATH" ]; then
    VAULT_CONTENT=$(cat "$VAULT_PATH")
else
    VAULT_CONTENT='{"version":1,"entries":{}}'
fi

# Build the vault entry
NEW_ENTRY=$(jq -n \
  --arg sn "$SERVER_NAME" \
  --arg su "$SERVER_URL" \
  --arg ua "$UPDATED_AT" \
  --arg at "$ACCESS_TOKEN" \
  --arg tt "$TOKEN_TYPE" \
  --argjson ei "$EXPIRES_IN" \
  --arg sc "$SCOPE" \
  --arg rt "$REFRESH_TOKEN" \
  --arg cid "$CLIENT_ID" \
  --arg cs "$CLIENT_SECRET" \
  --argjson cia "${CLIENT_ISSUED_AT:-$(date +%s)}" \
  '{
    serverName: $sn,
    serverUrl: $su,
    updatedAt: $ua,
    tokens: {
      access_token: $at,
      token_type: $tt,
      expires_in: $ei,
      scope: $sc,
      refresh_token: $rt
    },
    clientInfo: {
      client_id: $cid,
      client_secret: $cs,
      token_endpoint_auth_method: "none",
      client_id_issued_at: $cia,
      client_secret_expires_at: 0
    },
    state: "",
    codeVerifier: ""
  }')

# Merge into vault
echo "$VAULT_CONTENT" | jq --arg key "$VAULT_KEY" --argjson entry "$NEW_ENTRY" '
  .entries[$key] = $entry
' > "$VAULT_PATH"
chmod 600 "$VAULT_PATH"

echo -e "${GREEN}✓ Credentials saved to vault${NC}"
echo
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Setup complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo
echo "You can now use mcporter with The Others:"
echo "  mcporter call theothers.search_listings query=\"AI agents\""
echo
echo "Tokens are stored in: $VAULT_PATH"
echo "Vault entry key: $VAULT_KEY"
echo
echo "Note: Access tokens expire after 30 minutes."
echo "When they expire, mcporter should auto-refresh using the refresh token."
