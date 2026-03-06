#!/bin/bash
# 查看Notion定时同步状态

SCRIPT_DIR="$(dirname "$0")"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$SKILL_DIR/sync_timer.pid"
LOG_FILE="$SKILL_DIR/sync_timer.log"
CONFIG_FILE="$SKILL_DIR/config.json"

# 获取当前时间
TIMEZONE="Asia/Shanghai"
CHECK_TIME=$(TZ="$TIMEZONE" date '+%Y-%m-%d %H:%M:%S')

echo "📊 Notion定时同步状态检查"
echo "检查时间: $CHECK_TIME"
echo "时区: $TIMEZONE"
echo "========================================"

# 检查配置文件
if [ -f "$CONFIG_FILE" ]; then
    echo "📁 配置文件: $CONFIG_FILE"
    
    # 读取配置信息
    CHECK_INTERVAL=$(grep -o '"check_interval_minutes":[^,}]*' "$CONFIG_FILE" | grep -o '[0-9]*')
    QUIET_START=$(grep -o '"quiet_hours_start": "[^"]*' "$CONFIG_FILE" 2>/dev/null | cut -d'"' -f4)
    QUIET_END=$(grep -o '"quiet_hours_end": "[^"]*' "$CONFIG_FILE" 2>/dev/null | cut -d'"' -f4)
    OBSIDIAN_ROOT=$(grep -o '"root_dir": "[^"]*' "$CONFIG_FILE" 2>/dev/null | cut -d'"' -f4)
    
    [ -z "$CHECK_INTERVAL" ] && CHECK_INTERVAL=15
    [ -z "$QUIET_START" ] && QUIET_START="00:00"
    [ -z "$QUIET_END" ] && QUIET_END="08:30"
    [ -z "$OBSIDIAN_ROOT" ] && OBSIDIAN_ROOT="/path/to/your/obsidian"
    
    echo "⏰ 检查间隔: $CHECK_INTERVAL 分钟"
    echo "🤫 安静时段: $QUIET_START - $QUIET_END"
    echo "📁 Obsidian目录: $OBSIDIAN_ROOT/notion/"
else
    echo "⚠️  配置文件不存在: $CONFIG_FILE"
fi

echo ""

# 检查进程状态
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    
    if ps -p "$PID" > /dev/null 2>&1; then
        # 获取进程运行时间
        START_TIME=$(ps -o lstart= -p "$PID" 2>/dev/null | xargs)
        if [ -n "$START_TIME" ]; then
            START_EPOCH=$(date -d "$START_TIME" +%s 2>/dev/null || echo 0)
            CURRENT_EPOCH=$(date +%s)
            RUN_SECONDS=$((CURRENT_EPOCH - START_EPOCH))
            
            # 转换为可读格式
            RUN_DAYS=$((RUN_SECONDS / 86400))
            RUN_HOURS=$(( (RUN_SECONDS % 86400) / 3600 ))
            RUN_MINUTES=$(( (RUN_SECONDS % 3600) / 60 ))
            RUN_SECONDS=$((RUN_SECONDS % 60))
            
            RUN_TIME=""
            [ $RUN_DAYS -gt 0 ] && RUN_TIME="${RUN_TIME}${RUN_DAYS}天 "
            [ $RUN_HOURS -gt 0 ] && RUN_TIME="${RUN_TIME}${RUN_HOURS}小时 "
            [ $RUN_MINUTES -gt 0 ] && RUN_TIME="${RUN_TIME}${RUN_MINUTES}分钟 "
            RUN_TIME="${RUN_TIME}${RUN_SECONDS}秒"
        else
            RUN_TIME="未知"
        fi
        
        echo "🟢 状态: 运行中"
        echo "进程PID: $PID"
        echo "运行时间: $RUN_TIME"
    else
        echo "🔴 状态: PID文件存在但进程未运行"
        echo "进程PID: $PID (进程不存在)"
        echo "⚠️  建议清理: rm -f $PID_FILE"
    fi
else
    echo "🔴 状态: 未运行"
    echo "进程PID: 无"
fi

echo ""

# 检查日志文件
if [ -f "$LOG_FILE" ]; then
    echo "📋 日志信息:"
    echo "日志文件: $LOG_FILE"
    
    # 统计日志行数
    LOG_LINES=$(wc -l < "$LOG_FILE" 2>/dev/null || echo 0)
    echo "日志行数: $LOG_LINES"
    
    # 获取日志大小
    LOG_SIZE=$(du -h "$LOG_FILE" 2>/dev/null | cut -f1)
    echo "日志大小: $LOG_SIZE"
    
    echo ""
    echo "最近5条记录:"
    echo ""
    tail -n 10 "$LOG_FILE" | while IFS= read -r line; do
        echo "  $line"
    done
else
    echo "📭 日志文件不存在"
fi

echo ""

# 检查导出目录
if [ -f "$CONFIG_FILE" ] && [ -n "$OBSIDIAN_ROOT" ] && [ "$OBSIDIAN_ROOT" != "/path/to/your/obsidian" ]; then
    NOTION_DIR="$OBSIDIAN_ROOT/notion"
    
    if [ -d "$NOTION_DIR" ]; then
        echo "📁 目录状态:"
        echo "文章目录: $NOTION_DIR"
        
        # 统计文章数量
        ARTICLE_COUNT=$(find "$NOTION_DIR" -name "*.md" -type f 2>/dev/null | wc -l)
        echo "文章数量: $ARTICLE_COUNT"
        
        # 获取最新文章
        echo ""
        echo "最新3篇文章:"
        find "$NOTION_DIR" -name "*.md" -type f -exec ls -lt --time-style="+%b %d %H:%M" {} + 2>/dev/null | head -3 | while read -r line; do
            # 提取文件名和修改时间
            FILE_INFO=$(echo "$line" | awk '{print $6, $7, $8}')
            FILE_PATH=$(echo "$line" | awk '{print $9}')
            FILE_NAME=$(basename "$FILE_PATH")
            
            echo "  $FILE_INFO $FILE_NAME"
        done
    else
        echo "📁 目录状态:"
        echo "文章目录: $NOTION_DIR (不存在)"
    fi
fi

echo ""

# 计算下次检查时间（如果正在运行）
if [ -f "$PID_FILE" ] && ps -p "$(cat "$PID_FILE")" > /dev/null 2>&1 && [ -n "$CHECK_INTERVAL" ]; then
    NEXT_CHECK=$(TZ="$TIMEZONE" date -d "+$CHECK_INTERVAL minutes" '+%H:%M')
    echo "⏰ 下次检查时间:"
    echo "   $NEXT_CHECK (${CHECK_INTERVAL}分钟后)"
fi

echo ""
echo "========================================"
echo "📋 管理命令:"
echo "  启动: ./scripts/start_timer.sh"
echo "  停止: ./scripts/stop_timer.sh"
echo "  状态: ./scripts/status_timer.sh"
echo "  手动检查: FORCE_CHECK=1 ./scripts/simple_checker.sh"
echo "========================================"