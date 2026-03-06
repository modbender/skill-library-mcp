#!/bin/bash
# Fetch comments from a Feishu docx document
# Usage: get_comments.sh <doc_token> [comment_id1,comment_id2,...]
# If comment_ids not provided, fetches all comments first, then batch queries them.

set -euo pipefail

DOC_TOKEN="${1:?Usage: get_comments.sh <doc_token> [comment_id1,comment_id2,...]}"
COMMENT_IDS="${2:-}"

# Read credentials from openclaw config
CONFIG_FILE="$HOME/.openclaw/openclaw.json"
APP_ID=$(grep -m1 '"appId"' "$CONFIG_FILE" | head -1 | sed 's/.*: *"\(.*\)".*/\1/')
APP_SECRET=$(grep -m1 '"appSecret"' "$CONFIG_FILE" | head -1 | sed 's/.*: *"\(.*\)".*/\1/')

# Detect domain (feishu vs lark)
DOMAIN=$(grep -m1 '"domain"' "$CONFIG_FILE" | head -1 | sed 's/.*: *"\(.*\)".*/\1/' || echo "feishu")
if [ "$DOMAIN" = "lark" ]; then
  API_BASE="https://open.larksuite.com"
else
  API_BASE="https://open.feishu.cn"
fi

# Get tenant_access_token
TOKEN_RESP=$(curl -s -X POST "${API_BASE}/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"${APP_ID}\",\"app_secret\":\"${APP_SECRET}\"}")

TENANT_TOKEN=$(echo "$TOKEN_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['tenant_access_token'])" 2>/dev/null)

if [ -z "$TENANT_TOKEN" ]; then
  echo "Error: Failed to get tenant_access_token"
  echo "$TOKEN_RESP"
  exit 1
fi

# If no comment_ids provided, list all comments first
if [ -z "$COMMENT_IDS" ]; then
  ALL_COMMENTS=$(curl -s -X GET \
    "${API_BASE}/open-apis/drive/v1/files/${DOC_TOKEN}/comments?file_type=docx&user_id_type=open_id" \
    -H "Authorization: Bearer ${TENANT_TOKEN}")
  
  # Extract comment IDs
  COMMENT_IDS=$(echo "$ALL_COMMENTS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data.get('code') != 0:
    print(json.dumps(data, indent=2, ensure_ascii=False), file=sys.stderr)
    sys.exit(1)
items = data.get('data', {}).get('items', [])
if not items:
    print('No comments found.', file=sys.stderr)
    sys.exit(0)
ids = [item['comment_id'] for item in items]
print(','.join(ids))
" 2>&1)

  # If the output starts with 'No comments' or is an error, print and exit
  if echo "$COMMENT_IDS" | grep -q "^No comments\|^Error\|^{"; then
    echo "$COMMENT_IDS"
    exit 0
  fi
fi

# Convert comma-separated IDs to JSON array
IDS_JSON=$(echo "$COMMENT_IDS" | python3 -c "
import sys
ids = sys.stdin.read().strip().split(',')
import json
print(json.dumps(ids))
")

# Batch query comments
RESULT=$(curl -s -X POST \
  "${API_BASE}/open-apis/drive/v1/files/${DOC_TOKEN}/comments/batch_query?file_type=docx&user_id_type=open_id" \
  -H "Authorization: Bearer ${TENANT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"comment_ids\": ${IDS_JSON}}")

# Pretty print with comment content extraction
echo "$RESULT" | python3 -c "
import sys, json

data = json.load(sys.stdin)
if data.get('code') != 0:
    print(json.dumps(data, indent=2, ensure_ascii=False))
    sys.exit(1)

items = data.get('data', {}).get('items', [])
if not items:
    print('No comments found.')
    sys.exit(0)

for item in items:
    cid = item.get('comment_id', '?')
    is_solved = item.get('is_solved', False)
    is_whole = item.get('is_whole', False)
    quote = item.get('quote', '')
    status = '✅ Resolved' if is_solved else '💬 Open'
    scope = 'Global' if is_whole else 'Local'
    
    print(f'--- Comment {cid} [{status}] ({scope}) ---')
    if quote:
        print(f'  Quote: \"{quote}\"')
    
    replies = item.get('reply_list', {}).get('replies', [])
    for r in replies:
        uid = r.get('user_id', '?')
        elements = r.get('content', {}).get('elements', [])
        text_parts = []
        for el in elements:
            t = el.get('type', '')
            if t == 'text_run':
                text_parts.append(el.get('text_run', {}).get('text', ''))
            elif t == 'person':
                text_parts.append(f'@{el.get(\"person\", {}).get(\"user_id\", \"?\")}')
            elif t == 'docs_link':
                text_parts.append(el.get('docs_link', {}).get('url', ''))
        text = ''.join(text_parts)
        print(f'  [{uid}]: {text}')
    print()
"
