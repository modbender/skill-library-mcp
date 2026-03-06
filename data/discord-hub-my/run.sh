#!/data/data/com.termux/files/usr/bin/bash
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"

# 读取 .env
if [ -f "$DIR/.env" ]; then
  set -a
  . "$DIR/.env"
  set +a
fi

# 默认消息
MSG="${1:-OpenClaw test ✅}"

# 调用你之前做的发送脚本
"$DIR/discord_send.sh" "$MSG"
