#!/bin/bash
# Feishu Message Reaction Tool
# Usage: feishu-reaction.sh <message_id> <emoji_type> [remove]
# Adds or removes an emoji reaction on a Feishu message.

set -euo pipefail

MSG_ID="${1:?Usage: $0 <message_id> <emoji_type> [remove]}"
EMOJI_TYPE="${2:-THUMBSUP}"
ACTION="${3:-add}"

# Locate openclaw config
CONFIG="${OPENCLAW_CONFIG:-$HOME/.openclaw/openclaw.json}"
if [ ! -f "$CONFIG" ]; then
  echo "Error: openclaw.json not found at $CONFIG" >&2
  exit 1
fi

# Extract Feishu credentials
APP_ID=$(python3 -c "import json;print(json.load(open('$CONFIG'))['channels']['feishu']['appId'])")
APP_SECRET=$(python3 -c "import json;print(json.load(open('$CONFIG'))['channels']['feishu']['appSecret'])")

# Get tenant access token
TOKEN=$(curl -sf 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}" \
  | python3 -c "import json,sys;print(json.load(sys.stdin)['tenant_access_token'])")

if [ "$ACTION" = "remove" ]; then
  # Find the bot's reaction_id for this emoji, then delete it
  REACTION_ID=$(curl -sf "https://open.feishu.cn/open-apis/im/v1/messages/${MSG_ID}/reactions?reaction_type=${EMOJI_TYPE}" \
    -H "Authorization: Bearer $TOKEN" \
    | python3 -c "
import json,sys
d=json.load(sys.stdin)
for item in d.get('data',{}).get('items',[]):
    if item.get('reaction_type',{}).get('emoji_type')=='${EMOJI_TYPE}':
        if item.get('operator',{}).get('operator_type')=='app':
            print(item['reaction_id']); break
" 2>/dev/null)

  if [ -n "$REACTION_ID" ]; then
    curl -sf -X DELETE "https://open.feishu.cn/open-apis/im/v1/messages/${MSG_ID}/reactions/${REACTION_ID}" \
      -H "Authorization: Bearer $TOKEN" \
      | python3 -c "import json,sys;d=json.load(sys.stdin);print(f'code={d[\"code\"]}, msg={d[\"msg\"]}')"
  else
    echo "No matching reaction found to remove"
  fi
else
  # Add reaction
  curl -sf -X POST "https://open.feishu.cn/open-apis/im/v1/messages/${MSG_ID}/reactions" \
    -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' \
    -d "{\"reaction_type\":{\"emoji_type\":\"${EMOJI_TYPE}\"}}" \
    | python3 -c "import json,sys;d=json.load(sys.stdin);print(f'code={d[\"code\"]}, msg={d[\"msg\"]}')"
fi
