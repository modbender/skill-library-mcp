#!/bin/bash
# Granola MCP OAuth token refresh script
# Reads granola_oauth.json, refreshes the token, updates mcporter.json
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_DIR="$SCRIPT_DIR/../config"
OAUTH_FILE="$CONFIG_DIR/granola_oauth.json"
MCPORTER_FILE="$CONFIG_DIR/mcporter.json"

CLIENT_ID=$(python3 -c "import json; print(json.load(open('$OAUTH_FILE'))['client_id'])")
REFRESH_TOKEN=$(python3 -c "import json; print(json.load(open('$OAUTH_FILE'))['refresh_token'])")
TOKEN_ENDPOINT=$(python3 -c "import json; print(json.load(open('$OAUTH_FILE'))['token_endpoint'])")

RESPONSE=$(curl -s -X POST "$TOKEN_ENDPOINT" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token&refresh_token=${REFRESH_TOKEN}&client_id=${CLIENT_ID}")

# Check for error
ERROR=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('error',''))" 2>/dev/null)
if [ -n "$ERROR" ]; then
  echo "ERROR: Token refresh failed: $ERROR"
  echo "$RESPONSE"
  exit 1
fi

# Extract new tokens
NEW_ACCESS=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
NEW_REFRESH=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('refresh_token', ''))")
EXPIRES_IN=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('expires_in', 21600))")

# Update oauth file
python3 -c "
import json
data = json.load(open('$OAUTH_FILE'))
data['access_token'] = '$NEW_ACCESS'
if '$NEW_REFRESH':
    data['refresh_token'] = '$NEW_REFRESH'
data['expires_in'] = $EXPIRES_IN
json.dump(data, open('$OAUTH_FILE', 'w'), indent=2)
"

# Update mcporter.json
python3 -c "
import json
mc = json.load(open('$MCPORTER_FILE'))
mc['mcpServers']['granola']['headers']['Authorization'] = 'Bearer $NEW_ACCESS'
json.dump(mc, open('$MCPORTER_FILE', 'w'), indent=2)
"

echo "OK: Token refreshed, expires in ${EXPIRES_IN}s"
