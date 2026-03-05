#!/bin/bash
# notify_bot.sh - 向指定 bot 发送任务通知
# 用法：notify_bot.sh <bot_name> <group_id> <topic_id> <message>
#       notify_bot.sh "bot1,bot2,bot3" <group_id> <topic_id> <message>

set -e

if [ $# -lt 4 ]; then
  echo "用法: $0 <bot_name|bot1,bot2> <group_id> <topic_id> <message>"
  echo "示例: $0 imagebot -1003870994840 11 '生成32x32宝箱图标'"
  echo "示例: $0 'imagebot,godot' -1003870994840 3 '任务通知'"
  exit 1
fi

BOT_NAMES="$1"
GROUP_ID="$2"
TOPIC_ID="$3"
MESSAGE="$4"

# 分割 bot 名称（逗号分隔）
IFS=',' read -ra BOTS <<< "$BOT_NAMES"

echo "📢 通知 bot: ${BOTS[@]} (群 $GROUP_ID topic $TOPIC_ID)"

for bot_name in "${BOTS[@]}"; do
  bot_name=$(echo "$bot_name" | xargs)  # trim 空格
  
  # vision 的 key 是 openclaw.telegram.vision.token，其他是 .bot_token
  if [ "$bot_name" = "vision" ]; then
    TOKEN=$(~/.openclaw/tools/keychain.sh get "openclaw.telegram.vision.token" 2>/dev/null || echo "")
  else
    TOKEN=$(~/.openclaw/tools/keychain.sh get "openclaw.telegram.${bot_name}.bot_token" 2>/dev/null || echo "")
  fi
  
  if [ -z "$TOKEN" ]; then
    echo "❌ $bot_name: token 不存在"
    continue
  fi
  
  # 发送任务消息
  RESULT=$(curl -s -X POST "https://api.telegram.org/bot$TOKEN/sendMessage" \
    -d "chat_id=$GROUP_ID" \
    -d "message_thread_id=$TOPIC_ID" \
    -d "text=$MESSAGE")
  
  MSG_ID=$(echo "$RESULT" | jq -r '.result.message_id // empty')
  
  if [ -n "$MSG_ID" ]; then
    echo "✅ $bot_name 已通知 (msg_id: $MSG_ID)"
  else
    ERROR=$(echo "$RESULT" | jq -r '.description // "unknown error"')
    echo "❌ $bot_name 通知失败: $ERROR"
  fi
  
  sleep 0.2
done

echo "✅ 通知完成"
