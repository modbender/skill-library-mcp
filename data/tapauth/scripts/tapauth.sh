#!/usr/bin/env bash
# TapAuth helper — create a grant, show approval URL, poll for token.
# Usage: ./tapauth.sh <provider> <scopes> <agent_name> [base_url]
#
# Example:
#   ./tapauth.sh github "repo,read:user" "My Agent"
#   ./tapauth.sh google "drive.readonly" "Drive Reader"

set -euo pipefail

PROVIDER="${1:?Usage: tapauth.sh <provider> <scopes> <agent_name> [base_url]}"
SCOPES="${2:?Usage: tapauth.sh <provider> <scopes> <agent_name> [base_url]}"
AGENT_NAME="${3:?Usage: tapauth.sh <provider> <scopes> <agent_name> [base_url]}"
BASE_URL="${4:-https://tapauth.ai}"

# Convert comma-separated scopes to JSON array
SCOPES_JSON=$(echo "$SCOPES" | tr ',' '\n' | sed 's/^/"/;s/$/"/' | tr '\n' ',' | sed 's/,$//' | sed 's/^/[/;s/$/]/')

echo "🔐 Creating TapAuth grant..."
echo "   Provider: $PROVIDER"
echo "   Scopes:   $SCOPES"
echo "   Agent:    $AGENT_NAME"
echo ""

# Step 1: Create grant
RESPONSE=$(curl -s -X POST "$BASE_URL/api/grants" \
  -H "Content-Type: application/json" \
  -d "{\"provider\":\"$PROVIDER\",\"scopes\":$SCOPES_JSON,\"agent_name\":\"$AGENT_NAME\"}")

GRANT_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
GRANT_SECRET=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['grant_secret'])" 2>/dev/null)
APPROVAL_URL=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['approval_url'])" 2>/dev/null)

if [ -z "$GRANT_ID" ] || [ -z "$GRANT_SECRET" ]; then
  echo "❌ Failed to create grant:"
  echo "$RESPONSE"
  exit 1
fi

echo "✅ Grant created: $GRANT_ID"
echo ""
echo "👉 Please approve at: $APPROVAL_URL"
echo "   (Link expires in 10 minutes)"
echo ""

# Step 2: Poll for token
echo "⏳ Waiting for approval..."
POLL_INTERVAL=3
MAX_POLLS=200  # ~10 minutes

for i in $(seq 1 $MAX_POLLS); do
  TOKEN_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/grants/$GRANT_ID/token" \
    -H "Content-Type: application/json" \
    -d "{\"grant_secret\":\"$GRANT_SECRET\"}")
  
  HTTP_CODE=$(echo "$TOKEN_RESPONSE" | tail -1)
  BODY=$(echo "$TOKEN_RESPONSE" | sed '$d')
  
  case "$HTTP_CODE" in
    200)
      echo ""
      echo "✅ Token received!"
      echo "$BODY" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"   Provider:     {data.get('provider', 'unknown')}\")
print(f\"   Scope:        {data.get('scope', 'unknown')}\")
print(f\"   Access Token: {data.get('access_token', 'N/A')[:20]}...\")
" 2>/dev/null
      
      # Output just the token for piping
      echo ""
      echo "--- TOKEN (pipe-friendly) ---"
      echo "$BODY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null
      exit 0
      ;;
    202)
      printf "."
      sleep "$POLL_INTERVAL"
      ;;
    410)
      echo ""
      STATUS=$(echo "$BODY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))" 2>/dev/null)
      echo "❌ Grant $STATUS"
      case "$STATUS" in
        link_expired) echo "   The approval link expired. Run this script again to create a new grant." ;;
        denied) echo "   The user denied the request." ;;
        revoked) echo "   The user revoked access." ;;
        *) echo "   $BODY" ;;
      esac
      exit 1
      ;;
    *)
      echo ""
      echo "❌ Unexpected response ($HTTP_CODE): $BODY"
      exit 1
      ;;
  esac
done

echo ""
echo "❌ Timed out waiting for approval."
exit 1
