#!/bin/bash
# Send voice message to Feishu/Lark
# Usage: send_feishu_voice.sh <ogg_file> <receive_id> <tenant_access_token> [receive_id_type]
# receive_id_type: open_id (default), chat_id, user_id, union_id, email

set -e

OGG_FILE="$1"
RECEIVE_ID="$2"
TOKEN="$3"
ID_TYPE="${4:-open_id}"
API_BASE="https://open.feishu.cn/open-apis"

if [ -z "$OGG_FILE" ] || [ -z "$RECEIVE_ID" ] || [ -z "$TOKEN" ]; then
  echo "Usage: send_feishu_voice.sh <ogg_file> <receive_id> <token> [receive_id_type]"
  exit 1
fi

# 1. Get duration in milliseconds
DURATION_SEC=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OGG_FILE")
DURATION_MS=$(python3 -c "print(int(float('$DURATION_SEC') * 1000))")

# 2. Upload file to Feishu
UPLOAD_RESP=$(curl -s -X POST "$API_BASE/im/v1/files" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file_type=opus" \
  -F "file_name=voice.ogg" \
  -F "duration=$DURATION_MS" \
  -F "file=@$OGG_FILE")

FILE_KEY=$(echo "$UPLOAD_RESP" | python3 -c "import json,sys; print(json.load(sys.stdin).get('data',{}).get('file_key',''))")

if [ -z "$FILE_KEY" ]; then
  echo "Upload failed: $UPLOAD_RESP"
  exit 1
fi

echo "Uploaded: file_key=$FILE_KEY"

# 3. Send audio message
SEND_RESP=$(curl -s -X POST "$API_BASE/im/v1/messages?receive_id_type=$ID_TYPE" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"receive_id\":\"$RECEIVE_ID\",\"msg_type\":\"audio\",\"content\":\"{\\\"file_key\\\":\\\"$FILE_KEY\\\"}\"}")

echo "Send result: $SEND_RESP"
