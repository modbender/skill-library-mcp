#!/bin/bash

CONFIG_FILE="$HOME/.openclaw/workspace/open-qq-config.json"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "❌ 配置文件不存在：$CONFIG_FILE"
  exit 1
fi

cd /root/.openclaw/workspace/skills/openqq
echo "🚀 Starting QQ Bot..."
node qq-bot.js
