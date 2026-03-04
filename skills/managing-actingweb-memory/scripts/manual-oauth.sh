#!/usr/bin/env bash
# manual-oauth.sh — Manual PKCE OAuth flow for ActingWeb MCP
# Use this when `mcporter auth actingweb` fails in headless/GUI-less environments.
#
# Usage:
#   bash scripts/manual-oauth.sh
#
# What it does:
#   1. Registers a dynamic OAuth client
#   2. Starts a local callback server
#   3. Prints an auth URL for you to open in a browser
#   4. Exchanges the returned code for tokens
#   5. Writes the tokens into mcporter's credentials vault
#
# Requirements: curl, python3, node, openssl, mcporter (npm install -g mcporter)

set -euo pipefail

AUTH_SERVER="https://ai.actingweb.io"
TOKEN_URL="${AUTH_SERVER}/oauth/token"
REGISTER_URL="${AUTH_SERVER}/oauth/register"
MCP_URL="${AUTH_SERVER}/mcp"
CALLBACK_PORT=18850
REDIRECT_URI="http://127.0.0.1:${CALLBACK_PORT}/callback"
SCOPE="mcp"
STATE=$(openssl rand -hex 16)

# --- PKCE ---
CODE_VERIFIER=$(openssl rand -base64 48 | tr -d '=+/' | tr -dc 'A-Za-z0-9' | head -c 64)
CODE_CHALLENGE=$(printf '%s' "$CODE_VERIFIER" | openssl dgst -sha256 -binary | openssl base64 | tr '+/' '-_' | tr -d '=')

echo ""
echo "==> Registering dynamic OAuth client..."
REG=$(curl -sf -X POST "$REGISTER_URL" \
  -H "Content-Type: application/json" \
  -d "{\"client_name\":\"mcporter-cli\",\"redirect_uris\":[\"$REDIRECT_URI\"],\"grant_types\":[\"authorization_code\",\"refresh_token\"],\"response_types\":[\"code\"],\"token_endpoint_auth_method\":\"client_secret_post\"}")

CLIENT_ID=$(echo "$REG" | python3 -c "import sys,json; print(json.load(sys.stdin)['client_id'])")
CLIENT_SECRET=$(echo "$REG" | python3 -c "import sys,json; print(json.load(sys.stdin).get('client_secret',''))")
echo "    client_id: $CLIENT_ID"

# --- Build auth URL ---
ENCODED_REDIRECT=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$REDIRECT_URI'))")
ENCODED_RESOURCE=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$MCP_URL'))")
AUTH_URL="${AUTH_SERVER}/oauth/authorize?response_type=code&client_id=${CLIENT_ID}&code_challenge=${CODE_CHALLENGE}&code_challenge_method=S256&redirect_uri=${ENCODED_REDIRECT}&state=${STATE}&scope=${SCOPE}&resource=${ENCODED_RESOURCE}"

echo ""
echo "==> Open this URL in your browser and sign in with Google:"
echo ""
echo "    $AUTH_URL"
echo ""
echo "==> Waiting for callback on port ${CALLBACK_PORT}..."

# --- Start callback server and capture code ---
CALLBACK_OUTPUT=$(python3 - <<PYEOF
import http.server, urllib.parse, threading, sys

code = None

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global code
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        returned_state = params.get('state', [None])[0]
        if returned_state != '${STATE}':
            self.send_response(403)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body><h2>Error: state mismatch (possible CSRF). Try again.</h2></body></html>')
            threading.Thread(target=server.shutdown, daemon=True).start()
            return
        code = params.get('code', [None])[0]
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<html><body><h2>Authorized! You can close this tab.</h2></body></html>')
        threading.Thread(target=server.shutdown, daemon=True).start()
    def log_message(self, *args): pass

server = http.server.HTTPServer(('127.0.0.1', ${CALLBACK_PORT}), Handler)
server.serve_forever()
print(code or '')
PYEOF
)

OAUTH_CODE="${CALLBACK_OUTPUT}"
if [ -z "$OAUTH_CODE" ]; then
  echo "ERROR: No authorization code received. Did you complete the sign-in?" >&2
  exit 1
fi
echo "==> Authorization code received."

# --- Exchange code for tokens ---
echo "==> Exchanging code for tokens..."
TOKEN_RESPONSE=$(curl -sf -X POST "$TOKEN_URL" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code&code=${OAUTH_CODE}&redirect_uri=${REDIRECT_URI}&client_id=${CLIENT_ID}&client_secret=${CLIENT_SECRET}&code_verifier=${CODE_VERIFIER}")

ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
REFRESH_TOKEN=$(echo "$TOKEN_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('refresh_token',''))")
EMAIL=$(echo "$TOKEN_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('email',''))")
echo "    email: $EMAIL"

# --- Write into mcporter vault ---
echo "==> Saving tokens to mcporter vault..."
node - <<JSEOF
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const os = require('os');

const VAULT_PATH = path.join(os.homedir(), '.mcporter', 'credentials.json');

const descriptor = { name: 'actingweb', url: '${MCP_URL}', command: null };
const hash = crypto.createHash('sha256').update(JSON.stringify(descriptor)).digest('hex').slice(0, 16);
const key = 'actingweb|' + hash;

let vault = { version: 1, entries: {} };
try {
  const raw = JSON.parse(fs.readFileSync(VAULT_PATH, 'utf8'));
  if (raw.version === 1) vault = raw;
} catch (e) {}

vault.entries[key] = {
  serverName: 'actingweb',
  serverUrl: '${MCP_URL}',
  updatedAt: new Date().toISOString(),
  tokens: {
    access_token: '${ACCESS_TOKEN}',
    token_type: 'Bearer',
    expires_in: 3600,
    refresh_token: '${REFRESH_TOKEN}',
    scope: 'mcp',
  },
  clientInfo: {
    client_id: '${CLIENT_ID}',
    client_secret: '${CLIENT_SECRET}',
    redirect_uris: ['${REDIRECT_URI}'],
    grant_types: ['authorization_code', 'refresh_token'],
    token_endpoint_auth_method: 'client_secret_post',
  },
};

fs.mkdirSync(path.dirname(VAULT_PATH), { recursive: true });
fs.writeFileSync(VAULT_PATH, JSON.stringify(vault, null, 2));
console.log('    vault written to', VAULT_PATH);
JSEOF

echo ""
echo "✅ Done! Verify with: mcporter list actingweb --schema"
echo ""
