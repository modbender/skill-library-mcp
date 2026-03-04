#!/bin/bash
# 飞书语音消息发送脚本（智能语速版本）
# 根据要说的内容自动调整语速

set -e

# 配置
APP_ID="${FEISHU_APP_ID}"
APP_SECRET="${FEISHU_APP_SECRET}"
RECEIVER="${FEISHU_RECEIVER}"
DEFAULT_VOICE="${FEISHU_VOICE:-tongtong}"
DEFAULT_SPEED="${FEISHU_SPEED:-1.2}"  # 默认 1.2 倍速

# 参数
TEXT="$1"
VOICE_PARAM="$2"
SPEED_PARAM="$3"

if [ -z "$TEXT" ]; then
  echo "❌ 错误：缺少文本参数"
  exit 1
fi

# 智能语速计算
TEXT_LENGTH=${#TEXT}
if [ -n "$SPEED_PARAM" ]; then
  # 用户手动指定了语速
  SPEED="$SPEED_PARAM"
else
  # 根据文本长度自动调整语速
  if [ "$TEXT_LENGTH" -lt 20 ]; then
    SPEED="1.0"  # 短文本，正常语速
  elif [ "$TEXT_LENGTH" -lt 50 ]; then
    SPEED="1.2"  # 中等文本，稍快
  elif [ "$TEXT_LENGTH" -lt 100 ]; then
    SPEED="1.3"  # 长文本，较快
  else
    SPEED="1.5"  # 超长文本，快速阅读
  fi
fi

VOICE="${VOICE_PARAM:-$DEFAULT_VOICE}"

# 显示任务信息
echo "🎤 飞书语音消息发送（智能语速）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 文本: $TEXT"
echo "📏 长度: $TEXT_LENGTH 字符"
echo "🎙️  声音: $VOICE"
echo "⚡ 语速: $SPEED (自动调整)"
echo "👤 接收者: ${RECEIVER:0:20}..."
echo ""

# 获取 token
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\": \"$APP_ID\", \"app_secret\": \"$APP_SECRET\"}" | jq -r '.tenant_access_token')

# 生成 WAV 音频
echo "🎙️ 生成 TTS 音频..."
WORKSPACE="/root/.openclaw/workspace"
bash "$WORKSPACE/skills/zhipu-tts/scripts/text_to_speech.sh" "$TEXT" "$VOICE" "$SPEED" wav /tmp/feishu-voice-temp.wav > /dev/null 2>&1

# 转换为 opus
echo "🔄 转换为 opus 格式..."
ffmpeg -y -i /tmp/feishu-voice-temp.wav -c:a libopus -b:a 24k /tmp/feishu-voice.opus > /dev/null 2>&1

# 读取时长（毫秒）
EXACT_DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 /tmp/feishu-voice.opus)
DURATION_MS=$(awk "BEGIN {printf \"%.0f\", $EXACT_DURATION * 1000}")

echo "⏱️  时长: $(awk "BEGIN {printf \"%.1f\", $DURATION_MS / 1000}") 秒"

# 上传
UPLOAD_RESPONSE=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/feishu-voice.opus" \
  -F "file_type=opus" \
  -F "file_name=voice.opus" \
  -F "duration=$DURATION_MS")

UPLOAD_CODE=$(echo "$UPLOAD_RESPONSE" | jq -r '.code')
if [ "$UPLOAD_CODE" != "0" ]; then
  echo "❌ 上传失败"
  echo "$UPLOAD_RESPONSE" | jq .
  rm -f /tmp/feishu-voice-temp.wav /tmp/feishu-voice.opus
  exit 1
fi

FILE_KEY=$(echo "$UPLOAD_RESPONSE" | jq -r '.data.file_key')

# 发送消息
SEND_RESPONSE=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"receive_id\": \"$RECEIVER\",
    \"msg_type\": \"audio\",
    \"content\": \"{\\\"file_key\\\": \\\"$FILE_KEY\\\", \\\"duration\\\": $DURATION_MS\"
  }")

SEND_CODE=$(echo "$SEND_RESPONSE" | jq -r '.code')
if [ "$SEND_CODE" != "0" ]; then
  echo "❌ 发送失败"
  echo "$SEND_RESPONSE" | jq .
  rm -f /tmp/feishu-voice-temp.wav /tmp/feishu-voice.opus
  exit 1
fi

# 清理
rm -f /tmp/feishu-voice-temp.wav /tmp/feishu-voice.opus

# 完成
echo "📨 发送完成"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 语音消息发送成功！"
echo ""
echo "📊 本次统计："
echo "   • 文本长度: $TEXT_LENGTH 字符"
echo "   • 音频时长: $(awk "BEGIN {printf \"%.1f\", $DURATION_MS / 1000}") 秒"
echo "   • 使用语速: $SPEED"
echo "   • 使用声音: $VOICE"
echo ""
