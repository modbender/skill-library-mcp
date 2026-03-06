#!/bin/bash
# 停止Notion定时同步

SCRIPT_DIR="$(dirname "$0")"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$SKILL_DIR/sync_timer.pid"
LOG_FILE="$SKILL_DIR/sync_timer.log"

# 获取当前时间
TIMEZONE="Asia/Shanghai"
STOP_TIME=$(TZ="$TIMEZONE" date '+%Y-%m-%d %H:%M:%S')

echo "🛑 停止Notion定时同步..."
echo "停止时间: $STOP_TIME"

# 检查PID文件
if [ ! -f "$PID_FILE" ]; then
    echo "📭 没有找到PID文件，定时同步可能未运行"
    echo "   使用 ./scripts/status_timer.sh 查看状态"
    exit 0
fi

# 读取PID
PID=$(cat "$PID_FILE")

# 检查进程是否存在
if ps -p "$PID" > /dev/null 2>&1; then
    echo "🔍 找到运行进程: PID $PID"
    
    # 停止进程
    echo "⏹️  停止进程..."
    kill "$PID"
    
    # 等待进程停止
    sleep 2
    
    # 检查是否已停止
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "⚠️  进程仍在运行，强制停止..."
        kill -9 "$PID"
        sleep 1
    fi
    
    # 最终检查
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "❌ 无法停止进程 $PID"
        echo "   请手动检查: ps -p $PID"
        exit 1
    else
        echo "✅ 停止进程: $PID"
        
        # 清理PID文件
        rm -f "$PID_FILE"
        
        # 记录停止日志
        echo "[$STOP_TIME] 🛑 定时同步已停止" >> "$LOG_FILE"
        
        echo "✅ 定时同步已停止 - $STOP_TIME"
    fi
else
    echo "📭 进程 $PID 不存在，清理PID文件"
    rm -f "$PID_FILE"
    echo "✅ 已清理"
fi