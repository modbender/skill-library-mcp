#!/usr/bin/env bash
#
# gmail-auth-full-scope.sh — One-time OAuth flow for full Gmail scope
#
# This grants permanent delete capability (messages.delete / batchDelete).
# Run once; the token is stored at ~/.gmail-skill/full-scope-token.json
#
# Usage: gmail-auth-full-scope.sh [account-email]
#
set -euo pipefail

ACCOUNT="${1:-${GMAIL_ACCOUNT:-}}"
if [[ -z "$ACCOUNT" ]]; then
    echo "Error: No Gmail account specified. Set GMAIL_ACCOUNT or pass as argument." >&2
    exit 1
fi

GOG_CREDS_DIR="${HOME}/Library/Application Support/gogcli"
if [[ ! -f "$GOG_CREDS_DIR/credentials.json" ]]; then
    GOG_CREDS_DIR="${HOME}/.config/gogcli"
fi

if [[ ! -f "$GOG_CREDS_DIR/credentials.json" ]]; then
    echo "Error: Cannot find gog credentials." >&2
    exit 1
fi

TOKEN_DIR="${HOME}/.gmail-skill"
TOKEN_FILE="${TOKEN_DIR}/full-scope-token.json"
mkdir -p "$TOKEN_DIR"

echo "=== Gmail Full Scope Authorization ==="
echo "Account: $ACCOUNT"
echo "This grants full Gmail access (including permanent delete)."
echo ""
echo "A browser window will open. Sign in with $ACCOUNT and authorize."
echo ""

python3 - "$GOG_CREDS_DIR/credentials.json" "$TOKEN_FILE" "$ACCOUNT" << 'PYEOF'
import json, sys

creds_file = sys.argv[1]
token_file = sys.argv[2]
account = sys.argv[3]

with open(creds_file) as f:
    client = json.load(f)

from google_auth_oauthlib.flow import InstalledAppFlow

# Build client config from gog credentials
client_config = {
    "installed": {
        "client_id": client["client_id"],
        "client_secret": client["client_secret"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost"]
    }
}

SCOPES = ["https://mail.google.com/"]

flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
creds = flow.run_local_server(port=0, login_hint=account)

# Save token
token_data = {
    "refresh_token": creds.refresh_token,
    "token": creds.token,
    "account": account,
    "scopes": SCOPES,
}

with open(token_file, "w") as f:
    json.dump(token_data, f, indent=2)

print(f"\nToken saved to: {token_file}")
print(f"Scope: https://mail.google.com/ (full access)")
print("You can now permanently delete messages via the Gmail skill.")
PYEOF

echo ""
echo "Done! Full-scope token ready."
