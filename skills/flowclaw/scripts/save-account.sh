#!/bin/bash
# FlowClaw Account Setup — Save Claude Code CLI OAuth token for multi-account monitoring
# Supports up to 4+ accounts. Run 'claude login', then this script to save the token.

set -euo pipefail

TOKEN_DIR="${TOKEN_DIR:-$HOME/.openclaw/usage-tokens}"
mkdir -p "$TOKEN_DIR"

echo "🧠 FlowClaw — Add Account"
echo ""

# Check for Claude Code CLI
if ! command -v claude >/dev/null 2>&1; then
  echo "❌ Claude Code CLI not found."
  echo "   Install: npm install -g @anthropic-ai/claude-code"
  exit 1
fi

# Read current keychain credential
CREDS=$(security find-generic-password -s "Claude Code-credentials" -w 2>/dev/null || echo "")
if [ -z "$CREDS" ]; then
  echo "❌ No Claude Code credentials found in Keychain."
  echo "   Run 'claude login' first, then try again."
  exit 1
fi

# Parse token
PARSED=$(python3 << 'PYEOF'
import json, sys
creds = json.loads(sys.argv[1] if len(sys.argv) > 1 else input())
oauth = creds.get("claudeAiOauth", {})
if not oauth.get("accessToken"):
    print("ERROR: No access token found")
    sys.exit(1)
scopes = oauth.get("scopes", [])
if "user:profile" not in scopes:
    print(f"WARNING: Token missing 'user:profile' scope. Has: {scopes}")
sub = oauth.get("subscriptionType", "unknown")
tier = oauth.get("rateLimitTier", "unknown")
print(f"OK|{sub}|{tier}")
PYEOF
<<< "$CREDS")

if [[ "$PARSED" == ERROR* ]]; then
  echo "❌ $PARSED"
  exit 1
fi

if [[ "$PARSED" == WARNING* ]]; then
  echo "⚠️  $PARSED"
  echo "   The token may not work for usage monitoring."
  echo "   Try: claude logout && claude login"
  exit 1
fi

SUB_TYPE=$(echo "$PARSED" | cut -d'|' -f2)
TIER=$(echo "$PARSED" | cut -d'|' -f3)

# Ask for label
EXISTING=$(ls "$TOKEN_DIR"/account-*.json 2>/dev/null | wc -l | tr -d ' ')
echo "📊 Found token: $SUB_TYPE ($TIER)"
echo "📁 Existing accounts: $EXISTING"
echo ""

read -p "Account label (e.g., 'work', 'personal', 'main'): " LABEL
if [ -z "$LABEL" ]; then
  echo "❌ Label required."
  exit 1
fi

read -p "Email for this account: " EMAIL
if [ -z "$EMAIL" ]; then
  echo "❌ Email required."
  exit 1
fi

# Check for duplicate labels
for f in "$TOKEN_DIR"/account-*.json; do
  [ -f "$f" ] || continue
  EXISTING_LABEL=$(python3 -c "import json; print(json.load(open('$f')).get('label',''))")
  if [ "$EXISTING_LABEL" = "$LABEL" ]; then
    read -p "⚠️  Account '$LABEL' already exists. Overwrite? (y/N): " OVERWRITE
    if [ "${OVERWRITE,,}" != "y" ]; then
      echo "Aborted."
      exit 0
    fi
    # Remove old one, will be recreated
    rm "$f"
    EXISTING=$((EXISTING - 1))
    break
  fi
done

# Determine account number
ACCT_NUM=$((EXISTING + 1))
ACCT_FILE="$TOKEN_DIR/account-${ACCT_NUM}.json"

# Save token
python3 << PYEOF
import json
creds = json.loads('''$CREDS''')
oauth = creds["claudeAiOauth"]
account = {
    "label": "$LABEL",
    "email": "$EMAIL",
    "accessToken": oauth["accessToken"],
    "refreshToken": oauth["refreshToken"],
    "expiresAt": oauth["expiresAt"],
    "subscriptionType": oauth.get("subscriptionType"),
    "rateLimitTier": oauth.get("rateLimitTier"),
    "scopes": oauth.get("scopes", []),
}
with open("$ACCT_FILE", "w") as f:
    json.dump(account, f, indent=2)
PYEOF

chmod 600 "$ACCT_FILE"

echo ""
echo "✅ Account saved: $ACCT_FILE"
echo "   Label: $LABEL"
echo "   Email: $EMAIL"
echo "   Type: $SUB_TYPE ($TIER)"
echo ""

# Test it
echo "🔍 Testing usage API..."
RESULT=$(python3 << PYEOF
import json, urllib.request
d = json.load(open("$ACCT_FILE"))
req = urllib.request.Request("https://api.anthropic.com/api/oauth/usage",
    headers={"Authorization": f"Bearer {d['accessToken']}", "anthropic-beta": "oauth-2025-04-20"})
try:
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())
    fh = data.get("five_hour", {})
    sd = data.get("seven_day", {})
    print(f"OK|5h: {fh.get('utilization',0)}%|7d: {sd.get('utilization',0)}%")
except Exception as e:
    print(f"ERROR|{e}")
PYEOF
)

if [[ "$RESULT" == OK* ]]; then
  echo "   ✅ API working: $(echo "$RESULT" | cut -d'|' -f2-)"
else
  echo "   ❌ API error: $(echo "$RESULT" | cut -d'|' -f2)"
fi

echo ""
TOTAL=$(ls "$TOKEN_DIR"/account-*.json 2>/dev/null | wc -l | tr -d ' ')
echo "📊 Total accounts configured: $TOTAL"
echo "   Run 'flowclaw status --fresh' to see all accounts."
