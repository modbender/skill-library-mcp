#!/usr/bin/env bash
# feishu-voice-send.sh — Generate TTS audio and send as Feishu voice message
# Usage: feishu-voice-send.sh <text> <receive_id> [receive_id_type] [speed]
#
# Required env:
#   ELEVENLABS_API_KEY    — ElevenLabs API key
#   FEISHU_APP_ID         — Feishu app ID
#   FEISHU_APP_SECRET     — Feishu app secret
#   ELEVENLABS_VOICE_ID   — ElevenLabs voice ID
#   ELEVENLABS_MODEL_ID   — ElevenLabs model ID
#
# Optional env:
#   ELEVENLABS_SPEED      — Speech speed multiplier (default: 1.0, range: 0.5-2.0)

set -euo pipefail

TEXT="${1:?Usage: feishu-voice-send.sh <text> <receive_id> [receive_id_type] [speed]}"
RECEIVE_ID="${2:?Missing receive_id}"
RECEIVE_ID_TYPE="${3:-open_id}"
SPEED="${4:-${ELEVENLABS_SPEED:-1.0}}"

: "${ELEVENLABS_API_KEY:?Set ELEVENLABS_API_KEY}"
: "${FEISHU_APP_ID:?Set FEISHU_APP_ID}"
: "${FEISHU_APP_SECRET:?Set FEISHU_APP_SECRET}"
: "${ELEVENLABS_VOICE_ID:?Set ELEVENLABS_VOICE_ID}"
: "${ELEVENLABS_MODEL_ID:?Set ELEVENLABS_MODEL_ID}"

TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

MP3="$TMPDIR/voice.mp3"
OPUS="$TMPDIR/voice.opus"

# Step 1: TTS via sag
sag speak --no-speaker-boost --play=false --lang zh \
  --model-id "$ELEVENLABS_MODEL_ID" -v "$ELEVENLABS_VOICE_ID" \
  --speed "$SPEED" -o "$MP3" "$TEXT" >/dev/null 2>&1

# Step 2: Convert to opus
ffmpeg -y -i "$MP3" -c:a libopus -b:a 32k "$OPUS" >/dev/null 2>&1

# Step 3: Get duration
DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OPUS" | cut -d. -f1)
[ -z "$DURATION" ] && DURATION=1

# Step 4: Get tenant_access_token
TOKEN=$(curl -sf -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d "{\"app_id\":\"$FEISHU_APP_ID\",\"app_secret\":\"$FEISHU_APP_SECRET\"}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['tenant_access_token'])")

# Step 5: Upload opus
FILE_KEY=$(curl -sf -X POST 'https://open.feishu.cn/open-apis/im/v1/files' \
  -H "Authorization: Bearer $TOKEN" \
  -F 'file_type=opus' \
  -F 'file_name=voice.opus' \
  -F "file=@$OPUS" \
  -F "duration=$DURATION" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['file_key'])")

# Step 6: Send audio message
RESULT=$(curl -sf -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=$RECEIVE_ID_TYPE" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{\"receive_id\":\"$RECEIVE_ID\",\"msg_type\":\"audio\",\"content\":\"{\\\"file_key\\\":\\\"$FILE_KEY\\\"}\"}")

echo "$RESULT" | python3 -c "
import sys,json
d=json.load(sys.stdin)
if d['code']==0:
    print(f\"OK | message_id={d['data']['message_id']}\")
else:
    print(f\"ERROR | code={d['code']} msg={d['msg']}\")
    sys.exit(1)
"
