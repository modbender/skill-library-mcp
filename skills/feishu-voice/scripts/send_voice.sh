#!/bin/bash
# 飞书语音消息发送脚本
# 将文本转换为语音并发送到飞书

set -e

# 配置（从环境变量读取）
APP_ID="${FEISHU_APP_ID}"
APP_SECRET="${FEISHU_APP_SECRET}"
RECEIVER="${FEISHU_RECEIVER}"
VOICE="${FEISHU_VOICE:-tongtong}"
SPEED="${FEISHU_SPEED:-1.0}"

# 参数检查
TEXT="$1"
VOICE_PARAM="$2"
SPEED_PARAM="$3"

if [ -z "$TEXT" ]; then
  echo "❌ 错误：缺少文本参数"
  echo ""
  echo "用法: $0 <文本> [声音] [语速]"
  echo ""
  echo "参数："
  echo "  文本   - 要转换为语音的文字（必需）"
  echo "  声音   - tongtong(默认), chuichui, xiaochen"
  echo "  语速   - 0.5-2.0（默认 1.0）"
  echo ""
  echo "示例："
  echo "  $0 \"你好，这是一条语音消息\""
  echo "  $0 \"你好\" xiaochen 1.2"
  exit 1
fi

# 如果提供了参数，覆盖默认值
[ -n "$VOICE_PARAM" ] && VOICE="$VOICE_PARAM"
[ -n "$SPEED_PARAM" ] && SPEED="$SPEED_PARAM"

# 显示任务信息
echo "🎤 飞书语音消息发送"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 文本: $TEXT"
echo "🎙️  声音: $VOICE"
echo "⚡ 语速: $SPEED"
echo "👤 接收者: ${RECEIVER:0:20}..."
echo ""

# 1. 获取飞书访问令牌
echo "🔑 获取飞书 token..."
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\": \"$APP_ID\", \"app_secret\": \"$APP_SECRET\"}" | jq -r '.tenant_access_token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
  echo "❌ 获取 token 失败"
  exit 1
fi
echo "✅ Token 获取成功"

# 2. 生成 WAV 音频（使用 zhipu-tts）
echo ""
echo "🎙️ 生成 TTS 音频..."
WORKSPACE="/root/.openclaw/workspace"
TTS_SCRIPT="$WORKSPACE/skills/zhipu-tts/scripts/text_to_speech.sh"

if [ ! -f "$TTS_SCRIPT" ]; then
  echo "❌ 错误：找不到 zhipu-tts 脚本"
  echo "   路径: $TTS_SCRIPT"
  exit 1
fi

bash "$TTS_SCRIPT" "$TEXT" "$VOICE" "$SPEED" wav /tmp/feishu-voice-temp.wav > /dev/null 2>&1

if [ ! -f /tmp/feishu-voice-temp.wav ]; then
  echo "❌ TTS 生成失败"
  exit 1
fi
echo "✅ TTS 音频生成完成"

# 3. 转换为 opus 格式
echo ""
echo "🔄 转换为 opus 格式..."
ffmpeg -y -i /tmp/feishu-voice-temp.wav \
  -c:a libopus \
  -b:a 24k \
  /tmp/feishu-voice.opus > /dev/null 2>&1

if [ ! -f /tmp/feishu-voice.opus ]; then
  echo "❌ 格式转换失败"
  exit 1
fi
echo "✅ 格式转换完成"

# 4. 读取音频时长并转换为毫秒
echo ""
echo "⏱️  读取音频时长..."
EXACT_DURATION=$(ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 /tmp/feishu-voice.opus)

if [ -z "$EXACT_DURATION" ]; then
  echo "❌ 无法读取时长"
  exit 1
fi

# 转换为毫秒（飞书 API 要求）
DURATION_MS=$(awk "BEGIN {printf \"%.0f\", $EXACT_DURATION * 1000}")

echo "✅ 时长: ${EXACT_DURATION}秒 (${DURATION_MS}毫秒)"

# 5. 上传文件到飞书（duration 用毫秒）
echo ""
echo "📤 上传到飞书服务器..."
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
  exit 1
fi

FILE_KEY=$(echo "$UPLOAD_RESPONSE" | jq -r '.data.file_key')
echo "✅ 文件上传成功 (file_key: ${FILE_KEY:0:30}...)"

# 6. 发送音频消息（duration 用毫秒）
echo ""
echo "📨 发送音频消息..."
SEND_RESPONSE=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"receive_id\": \"$RECEIVER\",
    \"msg_type\": \"audio\",
    \"content\": \"{\\\"file_key\\\": \\\"$FILE_KEY\\\", \\\"duration\\\": $DURATION_MS}\"
  }")

SEND_CODE=$(echo "$SEND_RESPONSE" | jq -r '.code')
if [ "$SEND_CODE" != "0" ]; then
  echo "❌ 发送失败"
  echo "$SEND_RESPONSE" | jq .
  exit 1
fi

# 7. 清理临时文件
rm -f /tmp/feishu-voice-temp.wav /tmp/feishu-voice.opus

# 8. 完成
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 语音消息发送成功！"
echo ""
echo "📊 统计信息："
echo "   • 文本长度: ${#TEXT} 字符"
DUR_SEC=$(awk "BEGIN {printf \"%.1f\", $DURATION_MS / 1000}")
echo "   • 音频时长: ${DUR_SEC} 秒"
echo "   • 使用声音: $VOICE"
echo "   • 语速: $SPEED"
echo ""
