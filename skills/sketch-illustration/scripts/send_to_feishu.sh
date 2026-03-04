#!/bin/bash
# Upload an image and send it to Feishu DM
# Usage: bash send_to_feishu.sh <image_path> <open_id>

IMAGE_PATH="$1"
OPEN_ID="${2:-ou_22f2eefd5abe63e0cd67f4882cec06d4}"

if [ -z "$IMAGE_PATH" ]; then
  echo "Usage: $0 <image_path> [open_id]"
  exit 1
fi

APP_ID="cli_a9f5877b3378dbd8"
APP_SECRET=$(cat ~/.openclaw/openclaw.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['channels']['feishu']['appSecret'])")

# Get token
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}" | python3 -c "import json,sys; print(json.load(sys.stdin)['tenant_access_token'])")

# Upload image
IMG_KEY=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/images" \
  -H "Authorization: Bearer $TOKEN" \
  -F "image_type=message" \
  -F "image=@$IMAGE_PATH" | python3 -c "import json,sys; r=json.load(sys.stdin); print(r.get('data',{}).get('image_key','ERROR: '+str(r)))")

echo "Uploaded image_key: $IMG_KEY"

if [[ "$IMG_KEY" == ERROR* ]]; then
  echo "Upload failed!"
  exit 1
fi

# Send message
RESULT=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"receive_id\":\"$OPEN_ID\",\"msg_type\":\"image\",\"content\":\"{\\\"image_key\\\":\\\"$IMG_KEY\\\"}\"}")

CODE=$(echo $RESULT | python3 -c "import json,sys; print(json.load(sys.stdin).get('code','?'))")
if [ "$CODE" = "0" ]; then
  echo "✅ Image sent successfully!"
else
  echo "❌ Send failed: $RESULT"
  exit 1
fi
