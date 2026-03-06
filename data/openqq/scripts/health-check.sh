#!/bin/bash

# QQ Bot 健康检查脚本

LOG_DIR="$HOME/.openclaw/workspace/logs/qq-bot"
TODAY=$(date +%Y-%m-%d)
LOG_FILE="$LOG_DIR/qq-bot-$TODAY.log"

echo "🔍 QQ Bot 健康检查"
echo "=================="

# 检查进程
if pgrep -f "node qq-bot.js" > /dev/null; then
  echo "✅ 进程状态：运行中"
else
  echo "❌ 进程状态：未运行"
  exit 1
fi

# 检查日志文件
if [ -f "$LOG_FILE" ]; then
  echo "✅ 日志文件：存在"
  
  # 检查最近 5 分钟是否有日志
  if find "$LOG_FILE" -mmin -5 2>/dev/null | grep -q .; then
    echo "✅ 日志更新：正常"
  else
    echo "⚠️  日志更新：可能停滞"
  fi
  
  # 检查最近的错误
  ERRORS=$(tail -100 "$LOG_FILE" 2>/dev/null | grep -c "ERROR" || true)
  ERRORS=${ERRORS:-0}
  if [ "$ERRORS" -gt 0 ] 2>/dev/null; then
    echo "⚠️  最近错误：$ERRORS 条"
  else
    echo "✅ 最近错误：无"
  fi
else
  echo "❌ 日志文件：不存在"
fi

# 检查配置文件
CONFIG_FILE="$HOME/.openclaw/workspace/open-qq-config.json"
if [ -f "$CONFIG_FILE" ]; then
  echo "✅ 配置文件：存在"
else
  echo "❌ 配置文件：不存在"
  exit 1
fi

echo "=================="
echo "✅ 健康检查完成"
