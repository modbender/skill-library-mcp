#!/bin/bash
# X OAuth 2.0 PKCE flow for user-context bookmarks access
# Run once to generate your token. Token auto-refreshes after that.

CLIENT_ID="${X_OAUTH_CLIENT_ID:?Set X_OAUTH_CLIENT_ID in env}"
CLIENT_SECRET="${X_OAUTH_CLIENT_SECRET:?Set X_OAUTH_CLIENT_SECRET in env}"
REDIRECT_URI="http://127.0.0.1:1455/auth/callback"
SCOPES="bookmark.read tweet.read users.read offline.access"

# Generate PKCE code verifier and challenge
CODE_VERIFIER=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")
CODE_CHALLENGE=$(echo -n "$CODE_VERIFIER" | openssl dgst -sha256 -binary | base64 | tr '+/' '-_' | tr -d '=')
STATE=$(python3 -c "import secrets; print(secrets.token_hex(16))")

AUTH_URL="https://x.com/i/oauth2/authorize?response_type=code&client_id=${CLIENT_ID}&redirect_uri=${REDIRECT_URI}&scope=${SCOPES// /%20}&state=${STATE}&code_challenge=${CODE_CHALLENGE}&code_challenge_method=S256"

echo "Opening browser for X authorization..."
echo "$AUTH_URL"
open "$AUTH_URL"

# Start listener — catches callback and exchanges code for token
python3 -c "
import http.server, urllib.parse, json, base64, requests, os

CLIENT_ID = '$CLIENT_ID'
CLIENT_SECRET = '$CLIENT_SECRET'
REDIRECT_URI = '$REDIRECT_URI'
CODE_VERIFIER = '$CODE_VERIFIER'
CREDS_DIR = os.path.join(os.path.expanduser('~'), '.openclaw', 'credentials')
TOKEN_FILE = os.path.join(CREDS_DIR, 'x-oauth-token.json')

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if 'code' in params:
            code = params['code'][0]
            print('Got auth code, exchanging for token...')
            auth = base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode()
            resp = requests.post('https://api.x.com/2/oauth2/token',
                headers={'Authorization': f'Basic {auth}', 'Content-Type': 'application/x-www-form-urlencoded'},
                data={
                    'code': code,
                    'grant_type': 'authorization_code',
                    'redirect_uri': REDIRECT_URI,
                    'code_verifier': CODE_VERIFIER
                })
            if resp.status_code == 200:
                token_data = resp.json()
                os.makedirs(CREDS_DIR, exist_ok=True)
                with open(TOKEN_FILE, 'w') as f:
                    json.dump(token_data, f, indent=2)
                os.chmod(TOKEN_FILE, 0o600)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'<h1>Success! Token saved. You can close this tab.</h1>')
                print(f'Token saved to {TOKEN_FILE}')
            else:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f'<h1>Token exchange failed: {resp.text}</h1>'.encode())
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'No code received')
        import threading
        threading.Thread(target=self.server.shutdown).start()
    def log_message(self, format, *args):
        pass

server = http.server.HTTPServer(('127.0.0.1', 1455), Handler)
print('Listening on 127.0.0.1:1455 for callback...')
server.serve_forever()
"
