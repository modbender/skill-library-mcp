#!/bin/bash

# feishu-audio: 将音频文件发送到飞书作为语音消息

set -e

# 检查参数
if [ -z "$1" ]; then
    echo "用法: $0 <音频文件路径> [接收者OpenID]"
    exit 1
fi

AUDIO_FILE="$1"
RECEIVER="${2:-$FEISHU_RECEIVER}"

# 检查 ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "错误: ffmpeg 未安装。请运行: brew install ffmpeg"
    exit 1
fi

# 检查音频文件
if [ ! -f "$AUDIO_FILE" ]; then
    echo "错误: 音频文件不存在: $AUDIO_FILE"
    exit 1
fi

# 飞书配置
APP_ID="${FEISHU_APP_ID}"
APP_SECRET="${FEISHU_APP_SECRET}"

if [ -z "$APP_ID" ] || [ -z "$APP_SECRET" ]; then
    echo "错误: 请设置 FEISHU_APP_ID 和 FEISHU_APP_SECRET 环境变量"
    exit 1
fi

# 临时文件
OPUS_FILE="/tmp/$(basename "$AUDIO_FILE" .mp3).opus"

echo "转换音频为 opus 格式..."
ffmpeg -i "$AUDIO_FILE" -c:a libopus -b:a 24k -ar 24000 -ac 1 -y "$OPUS_FILE" 2>/dev/null

# 获取时长（秒）
DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OPUS_FILE" | awk '{printf "%.0f", $1}')
# 转换为毫秒
DURATION_MS=$((DURATION * 1000))

echo "音频时长: ${DURATION}秒 (${DURATION_MS}ms)"

# 获取 tenant_access_token
echo "获取飞书访问令牌..."
TOKEN_RESPONSE=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
    -H "Content-Type: application/json" \
    -d "{\"app_id\": \"$APP_ID\", \"app_secret\": \"$APP_SECRET\"}")

ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.tenant_access_token')

if [ "$ACCESS_TOKEN" == "null" ] || [ -z "$ACCESS_TOKEN" ]; then
    echo "错误: 获取 access_token 失败: $TOKEN_RESPONSE"
    exit 1
fi

# 上传文件（duration 传毫秒）
echo "上传音频到飞书..."
UPLOAD_RESPONSE=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -F "file=@$OPUS_FILE" \
    -F "file_type=opus" \
    -F "duration=$DURATION_MS")

FILE_TOKEN=$(echo "$UPLOAD_RESPONSE" | jq -r '.data.file_key')

if [ "$FILE_TOKEN" == "null" ] || [ -z "$FILE_TOKEN" ]; then
    echo "错误: 文件上传失败: $UPLOAD_RESPONSE"
    exit 1
fi

echo "文件上传成功, token: $FILE_TOKEN"

# 获取接收者（如果没有提供，使用默认）
if [ -z "$RECEIVER" ]; then
    RECEIVER="${FEISHU_RECEIVER}"
fi

if [ -z "$RECEIVER" ]; then
    echo "错误: 未指定接收者，请设置 FEISHU_RECEIVER 环境变量或作为第二个参数传递"
    exit 1
fi

# 发送 audio 消息（duration 传秒）
echo "发送语音消息给: $RECEIVER (时长: ${DURATION}秒)"
MESSAGE_RESPONSE=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"receive_id\": \"$RECEIVER\", \"msg_type\": \"audio\", \"content\": \"{\\\"file_key\\\": \\\"$FILE_TOKEN\\\", \\\"duration\\\": $DURATION}\"}")

if echo "$MESSAGE_RESPONSE" | jq -e '.code == 0' > /dev/null 2>&1; then
    echo "✅ 语音消息发送成功！"
else
    echo "错误: 消息发送失败: $MESSAGE_RESPONSE"
    exit 1
fi

# 清理临时文件
rm -f "$OPUS_FILE"

echo "完成！"
