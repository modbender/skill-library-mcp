#!/usr/bin/env bash
# Remote OAuth flow for Xpoz MCP (headless servers)
#
# Usage:
#   oauth-remote.sh get-url          → prints auth URL + saves PKCE state
#   oauth-remote.sh exchange <code>  → exchanges code for token, configures mcporter
#
# Security: tokens are never printed to stdout. State files use restricted
# permissions and are cleaned up after exchange.

set -euo pipefail

STATE_DIR="${HOME}/.cache/xpoz-oauth"
STATE_FILE="${STATE_DIR}/state.json"
MCP_URL="https://mcp.xpoz.ai"
REDIRECT_URI="https://www.xpoz.ai/oauth/openclaw"

# Ensure state directory exists with restricted permissions
mkdir -p "$STATE_DIR"
chmod 700 "$STATE_DIR"

case "${1:-}" in
  get-url)
    python3 -c "
import secrets, hashlib, base64, urllib.parse, json, urllib.request, os

# PKCE
verifier = secrets.token_urlsafe(64)
challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b'=').decode()
state = secrets.token_urlsafe(32)

# Dynamic client registration
reg_req = urllib.request.Request(
    '${MCP_URL}/oauth/register',
    data=json.dumps({
        'client_name': 'OpenClaw Agent',
        'redirect_uris': ['${REDIRECT_URI}'],
        'grant_types': ['authorization_code'],
        'response_types': ['code'],
        'token_endpoint_auth_method': 'none',
    }).encode(),
    headers={'Content-Type': 'application/json'},
)
reg_resp = json.loads(urllib.request.urlopen(reg_req).read())

params = urllib.parse.urlencode({
    'response_type': 'code',
    'client_id': reg_resp['client_id'],
    'code_challenge': challenge,
    'code_challenge_method': 'S256',
    'redirect_uri': '${REDIRECT_URI}',
    'state': state,
    'scope': 'mcp:tools',
    'resource': '${MCP_URL}/',
})

# Save state with restricted permissions
state_data = {
    'verifier': verifier,
    'state': state,
    'client_id': reg_resp['client_id'],
    'redirect_uri': '${REDIRECT_URI}',
}
fd = os.open('${STATE_FILE}', os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
with os.fdopen(fd, 'w') as f:
    json.dump(state_data, f)

print('${MCP_URL}/oauth/authorize?' + params)
"
    ;;

  exchange)
    CODE="${2:?Usage: oauth-remote.sh exchange <code>}"
    python3 -c "
import json, urllib.request, urllib.parse, subprocess, os, sys

with open('${STATE_FILE}') as f:
    oauth = json.load(f)

data = urllib.parse.urlencode({
    'grant_type': 'authorization_code',
    'code': '${CODE}',
    'redirect_uri': oauth['redirect_uri'],
    'client_id': oauth['client_id'],
    'code_verifier': oauth['verifier'],
}).encode()

req = urllib.request.Request(
    '${MCP_URL}/oauth/token',
    data=data,
    headers={'Content-Type': 'application/x-www-form-urlencoded'},
)
resp = json.loads(urllib.request.urlopen(req).read())

token = resp.get('access_token', '')
if not token:
    print('ERROR: No access token received', file=sys.stderr)
    sys.exit(1)

# Configure mcporter directly — never print the token
subprocess.run(['mcporter', 'config', 'remove', 'xpoz'], capture_output=True)
result = subprocess.run(
    ['mcporter', 'config', 'add', 'xpoz', '${MCP_URL}/mcp',
     '--header', f'Authorization=Bearer {token}'],
    capture_output=True, text=True
)

if result.returncode == 0:
    print('OK: Xpoz configured successfully')
else:
    print(f'ERROR: mcporter config failed: {result.stderr}', file=sys.stderr)
    sys.exit(1)
"
    # Clean up state file
    rm -f "$STATE_FILE"
    ;;

  *)
    echo "Usage: oauth-remote.sh <get-url|exchange <code>>"
    exit 1
    ;;
esac
