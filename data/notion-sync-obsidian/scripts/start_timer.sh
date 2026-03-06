#!/bin/bash
# 启动Notion定时同步

SCRIPT_DIR="$(dirname "$0")"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$SKILL_DIR/sync_timer.pid"
LOG_FILE="$SKILL_DIR/sync_timer.log"

# 检查是否已经在运行
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "⚠️  定时同步已经在运行 (PID: $PID)"
        echo "   使用 ./scripts/stop_timer.sh 停止"
        echo "   使用 ./scripts/status_timer.sh 查看状态"
        exit 1
    else
        echo "🔄 清理旧的PID文件..."
        rm -f "$PID_FILE"
    fi
fi

# 从配置读取检查间隔
CONFIG_FILE="$SKILL_DIR/config.json"
if [ -f "$CONFIG_FILE" ]; then
    CHECK_INTERVAL=$(grep -o '"check_interval_minutes":[^,}]*' "$CONFIG_FILE" | grep -o '[0-9]*')
    [ -z "$CHECK_INTERVAL" ] && CHECK_INTERVAL=15
else
    CHECK_INTERVAL=15
fi

# 获取当前时间
TIMEZONE="Asia/Shanghai"
START_TIME=$(TZ="$TIMEZONE" date '+%Y-%m-%d %H:%M:%S')

echo "🚀 启动Notion定时同步..."
echo "启动时间: $START_TIME"
echo "时区: $TIMEZONE"
echo "检查间隔: $CHECK_INTERVAL 分钟"
echo "日志文件: $LOG_FILE"

# 启动定时检查器
cd "$SKILL_DIR"
nohup bash "$SCRIPT_DIR/timer_checker.sh" > "$LOG_FILE" 2>&1 &
TIMER_PID=$!

# 保存PID
echo "$TIMER_PID" > "$PID_FILE"

# 等待进程启动
sleep 2

# 检查是否启动成功
if ps -p "$TIMER_PID" > /dev/null 2>&1; then
    echo "✅ 定时同步已启动"
    echo "📋 定时进程PID: $TIMER_PID"
    echo ""
    echo "📋 使用以下命令管理:"
    echo "   查看日志: tail -f $LOG_FILE"
    echo "   停止同步: ./scripts/stop_timer.sh"
    echo "   查看状态: ./scripts/status_timer.sh"
    echo "   手动检查: FORCE_CHECK=1 ./scripts/simple_checker.sh"
else
    echo "❌ 定时同步启动失败"
    rm -f "$PID_FILE"
    exit 1
fi