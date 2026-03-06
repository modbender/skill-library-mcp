#!/bin/bash
# HomePod TTS 播放脚本（隐私脱敏版）
# 用法: ./play-tts.sh "要播放的文字" [-e/--emotion 情绪]
#
# 依赖环境变量（请在 .env 中配置）：
# - HASS_URL: Home Assistant URL
# - HASS_TOKEN: Home Assistant 访问令牌
# - HASS_ENTITY_ID: HomePod 实体 ID
# - HTTP_PORT: 本地 HTTP 服务端口
# - LOCAL_IP: 本机 IP 地址
# - CONDA_ENV_NAME: Conda 环境名
# - TTS_DIR: TTS 脚本所在目录

set -e

# ========== 默认配置 ==========
TEXT="$1"
OUTPUT_FILE="lumi_homepod.wav"
DEFAULT_CONDA_ENV="qwen-tts"
DEFAULT_HTTP_PORT=8080

# ========== 加载配置 ==========
# 优先使用环境变量，未设置则使用默认值
if [ -f ".env" ]; then
    source .env
fi

HA_URL="${HASS_URL:-http://homeassistant.local:8123}"
HA_TOKEN="${HASS_TOKEN}"
ENTITY_ID="${HASS_ENTITY_ID:-media_player.ci_wo}"
HTTP_PORT="${HTTP_PORT:-$DEFAULT_HTTP_PORT}"
LOCAL_IP="${LOCAL_IP}"
CONDA_ENV_NAME="${CONDA_ENV_NAME:-$DEFAULT_CONDA_ENV}"
TTS_DIR="${TTS_DIR:-$(pwd)/../tts}"

# ========== 验证配置 ==========
if [ -z "$HA_TOKEN" ]; then
    echo "❌ 错误: 未配置 HASS_TOKEN"
    echo "请在 .env 文件中配置 HASS_TOKEN 或设置环境变量"
    exit 1
fi

if [ -z "$LOCAL_IP" ]; then
    echo "❌ 错误: 未配置 LOCAL_IP"
    echo "请在 .env 文件中配置 LOCAL_IP"
    exit 1
fi

if [ -z "$TEXT" ]; then
    echo "用法: ./play-tts.sh \"要播放的文字\" [-e/--emotion 情绪]"
    echo ""
    echo "可选情绪: default, happy, excited, sad, angry, surprised, scared, serious, gentle, calm, funny, tired, nervous"
    exit 1
fi

TTS_SCRIPT="$TTS_DIR/tts_dongxuelian_emotion.py"
if [ ! -f "$TTS_SCRIPT" ]; then
    echo "❌ 错误: 未找到 TTS 脚本: $TTS_SCRIPT"
    echo "请确保 TTS 脚本已放置在正确目录"
    exit 1
fi

echo "✨ 开始生成 TTS 语音..."

# ========== 激活 conda 环境并生成音频 ==========
cd "$TTS_DIR"

# 尝试激活 conda 环境
if command -v conda &> /dev/null; then
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate "$CONDA_ENV_NAME" 2>/dev/null || true
fi

# 生成音频并获取时长
TTS_OUTPUT=$(python3 "$TTS_SCRIPT" -t "$TEXT" -o "$OUTPUT_FILE" 2>&1)

if [ $? -ne 0 ]; then
    echo "❌ TTS 生成失败"
    echo "$TTS_OUTPUT"
    exit 1
fi

echo "$TTS_OUTPUT"

# 提取音频时长
AUDIO_DURATION=$(echo "$TTS_OUTPUT" | grep -oP 'AUDIO_DURATION:\K[0-9.]+' || echo "5")
WAIT_SECONDS=$(echo "$AUDIO_DURATION + 1" | bc)

echo "📏 音频时长: ${AUDIO_DURATION}秒，等待: ${WAIT_SECONDS}秒"

# ========== 启动 HTTP 服务 ==========
if ! lsof -i:$HTTP_PORT > /dev/null 2>&1; then
    echo "🚀 启动 HTTP 服务 (端口: $HTTP_PORT)..."
    python3 -m http.server $HTTP_PORT > /dev/null 2>&1 &
    sleep 2
fi

# ========== 音量控制 ==========
echo "🔊 获取当前音量..."
CURRENT_VOLUME=$(curl -s -X GET "$HA_URL/api/states/$ENTITY_ID" \
  -H "Authorization: Bearer $HA_TOKEN" | grep -oP '"volume_level":\s*\K[0-9.]+' || echo "")

echo "📌 当前音量: ${CURRENT_VOLUME:-未知}"

echo "🔈 设置音量为 40%..."
curl -s -X POST "$HA_URL/api/services/media_player/volume_set" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"entity_id\": \"$ENTITY_ID\", \"volume_level\": 0.4}"

# ========== 播放音频 ==========
echo "📡 发送到 HomePod 播放..."

curl -s -X POST "$HA_URL/api/services/media_player/play_media" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"entity_id\": \"$ENTITY_ID\", \"media_content_id\": \"http://$LOCAL_IP:$HTTP_PORT/$OUTPUT_FILE\", \"media_content_type\": \"music\"}"

echo ""
echo "🎵 正在播放...（等待 ${WAIT_SECONDS} 秒后恢复音量）"

# 等待播放完成
sleep $WAIT_SECONDS

# ========== 恢复音量 ==========
echo "🔁 恢复原音量..."
if [ -n "$CURRENT_VOLUME" ]; then
    curl -s -X POST "$HA_URL/api/services/media_player/volume_set" \
      -H "Authorization: Bearer $HA_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"entity_id\": \"$ENTITY_ID\", \"volume_level\": $CURRENT_VOLUME}"
    echo "✅ 音量已恢复为: $CURRENT_VOLUME"
else
    echo "⚠️ 无法获取原音量，跳过恢复"
fi

echo ""
echo "🎉 完成！"
