#!/bin/bash
# kroger.sh — Kroger API CLI for OpenClaw
# Usage:
#   kroger.sh auth                      - OAuth login flow
#   kroger.sh token                     - Check token status
#   kroger.sh search <term>             - Search products
#   kroger.sh add <productId> [qty]     - Add item to cart
#   kroger.sh cart                      - View cart (if supported)
#   kroger.sh locations <zipcode>       - Find nearby stores
#
# Env vars (required):
#   KROGER_CLIENT_ID
#   KROGER_CLIENT_SECRET
#
# Env vars (optional):
#   KROGER_TOKEN_FILE  - Path to token storage (default: ~/.kroger-tokens.json)
#   KROGER_LOCATION_ID - Store location ID for product availability
#   KROGER_REDIRECT_URI - OAuth redirect URI (default: http://localhost:8888/callback)

set -euo pipefail

: "${KROGER_CLIENT_ID:?Set KROGER_CLIENT_ID}"
: "${KROGER_CLIENT_SECRET:?Set KROGER_CLIENT_SECRET}"
TOKEN_FILE="${KROGER_TOKEN_FILE:-$HOME/.kroger-tokens.json}"
REDIRECT_URI="${KROGER_REDIRECT_URI:-http://localhost:8888/callback}"
LOCATION_ID="${KROGER_LOCATION_ID:-}"
API="https://api.kroger.com/v1"

# --- Token helpers ---

get_client_token() {
  local resp
  resp=$(curl -sf -X POST "$API/connect/oauth2/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -u "$KROGER_CLIENT_ID:$KROGER_CLIENT_SECRET" \
    -d "grant_type=client_credentials&scope=product.compact")
  echo "$resp" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])"
}

get_user_token() {
  if [ ! -f "$TOKEN_FILE" ]; then
    echo "ERROR: Not logged in. Run: kroger.sh auth" >&2
    return 1
  fi

  python3 -c "
import json, time, subprocess, sys, os

tf = os.environ['TOKEN_FILE']
d = json.load(open(tf))
now = int(time.time())

if now < d.get('expires_at', 0):
    print(d['access_token'])
    sys.exit(0)

# Refresh
r = subprocess.run([
    'curl', '-sf', '-X', 'POST',
    '$API/connect/oauth2/token',
    '-H', 'Content-Type: application/x-www-form-urlencoded',
    '-u', os.environ['KROGER_CLIENT_ID'] + ':' + os.environ['KROGER_CLIENT_SECRET'],
    '-d', 'grant_type=refresh_token&refresh_token=' + d['refresh_token']
], capture_output=True, text=True)

if r.returncode != 0:
    print('ERROR: Refresh failed. Run: kroger.sh auth', file=sys.stderr)
    sys.exit(1)

data = json.loads(r.stdout)
if 'error' in data:
    print(f'ERROR: {data[\"error\"]}. Run: kroger.sh auth', file=sys.stderr)
    sys.exit(1)

data['expires_at'] = int(time.time()) + data.get('expires_in', 1800) - 60
json.dump(data, open(tf, 'w'), indent=2)
print(data['access_token'])
" 2>&1
}

save_user_token() {
  local response="$1"
  python3 -c "
import json, time, os
data = json.loads('''$response''')
if 'error' in data:
    print(f'ERROR: {data}')
    exit(1)
data['expires_at'] = int(time.time()) + data.get('expires_in', 1800) - 60
json.dump(data, open(os.environ['TOKEN_FILE'], 'w'), indent=2)
print('Logged in to Kroger successfully!')
"
}

# --- Commands ---

cmd_auth() {
  local scope="cart.basic:write+product.compact"
  local encoded_uri
  encoded_uri=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$REDIRECT_URI'))")
  local auth_url="$API/connect/oauth2/authorize?client_id=$KROGER_CLIENT_ID&redirect_uri=$encoded_uri&response_type=code&scope=$scope"

  echo "AUTH_URL:$auth_url"
  echo "Open the URL above, log in, then provide the redirect URL or code."
  echo ""
  echo "If using localhost callback, starting listener..."

  # Try to start local listener if redirect is localhost
  if [[ "$REDIRECT_URI" == *localhost* ]]; then
    local port
    port=$(echo "$REDIRECT_URI" | grep -oE ':[0-9]+' | tr -d ':')
    python3 -c "
import http.server, urllib.parse, sys, threading

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        code = q.get('code', [None])[0]
        if code:
            self.send_response(200)
            self.send_header('Content-Type','text/html')
            self.end_headers()
            self.wfile.write(b'<h1>Success! Close this tab.</h1>')
            print(f'CODE:{code}')
        else:
            self.send_response(400)
            self.end_headers()
            print('ERROR:no_code')
        sys.stdout.flush()
        threading.Thread(target=self.server.shutdown).start()
    def log_message(self, *a): pass

s = http.server.HTTPServer(('localhost', $port), H)
print(f'Listening on port $port...')
sys.stdout.flush()
s.handle_request()
" 2>&1 | while IFS= read -r line; do
      if [[ "$line" == CODE:* ]]; then
        code="${line#CODE:}"
        response=$(curl -sf -X POST "$API/connect/oauth2/token" \
          -H "Content-Type: application/x-www-form-urlencoded" \
          -u "$KROGER_CLIENT_ID:$KROGER_CLIENT_SECRET" \
          -d "grant_type=authorization_code&code=$code&redirect_uri=$REDIRECT_URI")
        save_user_token "$response"
      else
        echo "$line"
      fi
    done
  fi
}

cmd_exchange() {
  # Exchange a code manually: kroger.sh exchange <code>
  local code="$1"
  local response
  response=$(curl -sf -X POST "$API/connect/oauth2/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -u "$KROGER_CLIENT_ID:$KROGER_CLIENT_SECRET" \
    -d "grant_type=authorization_code&code=$code&redirect_uri=$REDIRECT_URI")
  save_user_token "$response"
}

cmd_search() {
  local term="$1"
  if [ -z "$term" ]; then
    echo "Usage: kroger.sh search <term>" >&2; return 1
  fi

  local token
  token=$(get_client_token)
  local encoded
  encoded=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$term'))")

  local location_param=""
  [ -n "$LOCATION_ID" ] && location_param="&filter.locationId=$LOCATION_ID"

  curl -sf "$API/products?filter.term=$encoded&filter.limit=5$location_param" \
    -H "Authorization: Bearer $token" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for i, p in enumerate(data.get('data', []), 1):
    desc = p.get('description', 'Unknown')
    pid = p.get('productId', '')
    brand = p.get('brand', '')
    print(f'{i}. [{pid}] {desc} ({brand})')
if not data.get('data'):
    print('No products found.')
"
}

cmd_add() {
  local product_id="$1"
  local qty="${2:-1}"
  if [ -z "$product_id" ]; then
    echo "Usage: kroger.sh add <productId> [qty]" >&2; return 1
  fi

  local token
  token=$(get_user_token) || return 1

  local status
  status=$(curl -s -o /dev/null -w "%{http_code}" -X PUT "$API/cart/add" \
    -H "Authorization: Bearer $token" \
    -H "Content-Type: application/json" \
    -d "{\"items\":[{\"upc\":\"$product_id\",\"quantity\":$qty}]}")

  if [ "$status" -ge 200 ] && [ "$status" -lt 300 ]; then
    echo "Added to cart! (qty: $qty)"
  else
    echo "ERROR: Failed to add to cart (HTTP $status)" >&2
    return 1
  fi
}

cmd_locations() {
  local zip="$1"
  if [ -z "$zip" ]; then
    echo "Usage: kroger.sh locations <zipcode>" >&2; return 1
  fi

  local token
  token=$(get_client_token)

  curl -sf "$API/locations?filter.zipCode.near=$zip&filter.limit=5" \
    -H "Authorization: Bearer $token" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for loc in data.get('data', []):
    lid = loc.get('locationId', '')
    name = loc.get('name', '')
    addr = loc.get('address', {})
    line = addr.get('addressLine1', '')
    city = addr.get('city', '')
    state = addr.get('state', '')
    print(f'[{lid}] {name} — {line}, {city}, {state}')
if not data.get('data'):
    print('No locations found.')
"
}

cmd_token() {
  if [ ! -f "$TOKEN_FILE" ]; then
    echo "Not logged in. Run: kroger.sh auth"; return
  fi
  python3 -c "
import json, time, os
d = json.load(open(os.environ['TOKEN_FILE']))
exp = d.get('expires_at', 0)
now = time.time()
if now < exp:
    print(f'Logged in. Token valid for {int((exp-now)/60)} more minutes.')
else:
    print('Token expired. Will auto-refresh on next use.')
"
}

# --- Main ---
case "${1:-help}" in
  auth)      cmd_auth ;;
  exchange)  cmd_exchange "${2:-}" ;;
  search)    cmd_search "${2:-}" ;;
  add)       cmd_add "${2:-}" "${3:-1}" ;;
  locations) cmd_locations "${2:-}" ;;
  token)     cmd_token ;;
  help|*)
    echo "Kroger CLI for OpenClaw"
    echo "Usage: kroger.sh <command> [args]"
    echo ""
    echo "Commands:"
    echo "  auth                  - OAuth login flow"
    echo "  exchange <code>       - Exchange auth code for token"
    echo "  search <term>         - Search products"
    echo "  add <productId> [qty] - Add item to cart"
    echo "  locations <zipcode>   - Find nearby stores"
    echo "  token                 - Check token status"
    echo ""
    echo "Env vars: KROGER_CLIENT_ID, KROGER_CLIENT_SECRET (required)"
    echo "Optional: KROGER_TOKEN_FILE, KROGER_LOCATION_ID, KROGER_REDIRECT_URI"
    ;;
esac
