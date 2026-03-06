#!/bin/bash
# 定时检查器 - 管理定时同步任务

SCRIPT_DIR="$(dirname "$0")"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$SKILL_DIR/config.json"
LOG_FILE="$SKILL_DIR/sync_timer.log"
PID_FILE="$SKILL_DIR/sync_timer.pid"

# 加载配置
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 配置文件不存在: $CONFIG_FILE"
    exit 1
fi

# 从配置读取参数
CHECK_INTERVAL=$(grep -o '"check_interval_minutes":[^,}]*' "$CONFIG_FILE" | grep -o '[0-9]*')
QUIET_START=$(grep -o '"quiet_hours_start": "[^"]*' "$CONFIG_FILE" 2>/dev/null | cut -d'"' -f4)
QUIET_END=$(grep -o '"quiet_hours_end": "[^"]*' "$CONFIG_FILE" 2>/dev/null | cut -d'"' -f4)
TIMEZONE=$(grep -o '"timezone": "[^"]*' "$CONFIG_FILE" 2>/dev/null | cut -d'"' -f4)

# 设置默认值
[ -z "$CHECK_INTERVAL" ] && CHECK_INTERVAL=15
[ -z "$QUIET_START" ] && QUIET_START="00:00"
[ -z "$QUIET_END" ] && QUIET_END="08:30"
[ -z "$TIMEZONE" ] && TIMEZONE="Asia/Shanghai"

# 计算检查间隔（秒）
CHECK_INTERVAL_SECONDS=$((CHECK_INTERVAL * 60))

echo "⏰ Notion定时同步检查器启动"
echo "========================================"
echo "时区: $TIMEZONE"
echo "检查间隔: $CHECK_INTERVAL 分钟"
echo "安静时段: $QUIET_START - $QUIET_END"
echo "日志文件: $LOG_FILE"
echo "========================================"
echo ""

# 记录启动时间
START_TIME=$(TZ="$TIMEZONE" date '+%Y-%m-%d %H:%M:%S')
echo "[$START_TIME] 🔄 定时同步启动" >> "$LOG_FILE"
echo "[$START_TIME] ⏰ 检查间隔: $CHECK_INTERVAL 分钟" >> "$LOG_FILE"
echo "[$START_TIME] 🤫 安静时段: $QUIET_START - $QUIET_END" >> "$LOG_FILE"

# 主循环
while true; do
    CURRENT_DATETIME=$(TZ="$TIMEZONE" date '+%Y-%m-%d %H:%M:%S')
    CURRENT_TIME=$(TZ="$TIMEZONE" date '+%H:%M')
    
    # 检查是否在安静时段
    IN_QUIET_HOURS=0
    if [[ "$CURRENT_TIME" > "$QUIET_START" ]] && [[ "$CURRENT_TIME" < "$QUIET_END" ]]; then
        IN_QUIET_HOURS=1
    fi
    
    # 检查强制检查标志
    FORCE_CHECK=${FORCE_CHECK:-0}
    
    echo "[$CURRENT_DATETIME] 🔍 检查时间..." | tee -a "$LOG_FILE"
    
    if [ "$IN_QUIET_HOURS" -eq 1 ] && [ "$FORCE_CHECK" -eq 0 ]; then
        echo "[$CURRENT_DATETIME] 🤫 安静时段 ($QUIET_START-$QUIET_END)，跳过检查" | tee -a "$LOG_FILE"
    else
        if [ "$FORCE_CHECK" -eq 1 ]; then
            echo "[$CURRENT_DATETIME] ⚡ 强制检查模式，忽略安静时段" | tee -a "$LOG_FILE"
        fi
        
        # 选择检查脚本
        CHECK_SCRIPT="$SCRIPT_DIR/real_notion_checker.py"
        
        # 运行检查脚本
        if [ -f "$CHECK_SCRIPT" ]; then
            echo "[$CURRENT_DATETIME] 🚀 运行检查脚本..." | tee -a "$LOG_FILE"
            
            # 运行Python检查器
            OUTPUT=$(cd "$SCRIPT_DIR" && python3 "$CHECK_SCRIPT" 2>&1)
            echo "$OUTPUT" >> "$LOG_FILE"
            
            # 检查是否有更新
            if echo "$OUTPUT" | grep -q "✅ 保存:"; then
                echo "[$CURRENT_DATETIME] 📱 发现更新，已导出" | tee -a "$LOG_FILE"
                
                # 提取更新的文章标题
                UPDATED_ARTICLES=$(echo "$OUTPUT" | grep "✅ 保存:" | sed 's/✅ 保存: //' | head -3)
                if [ -n "$UPDATED_ARTICLES" ]; then
                    echo "[$CURRENT_DATETIME] 📄 更新文章:" | tee -a "$LOG_FILE"
                    echo "$UPDATED_ARTICLES" | while read -r article; do
                        echo "[$CURRENT_DATETIME]   - $article" | tee -a "$LOG_FILE"
                    done
                fi
            elif echo "$OUTPUT" | grep -q "📭 没有发现新的文章更新"; then
                echo "[$CURRENT_DATETIME] 📭 没有发现新的文章更新" | tee -a "$LOG_FILE"
            else
                echo "[$CURRENT_DATETIME] ⚠️  检查完成，但可能遇到问题" | tee -a "$LOG_FILE"
            fi
        else
            echo "[$CURRENT_DATETIME] ❌ 检查脚本不存在: $CHECK_SCRIPT" | tee -a "$LOG_FILE"
        fi
        
        # 重置强制检查标志
        FORCE_CHECK=0
    fi
    
    # 计算下次检查时间
    NEXT_CHECK=$(TZ="$TIMEZONE" date -d "+$CHECK_INTERVAL minutes" '+%H:%M')
    echo "[$CURRENT_DATETIME] ⏳ 等待 $CHECK_INTERVAL 分钟..." | tee -a "$LOG_FILE"
    echo "[$CURRENT_DATETIME] 🕐 下次检查: $NEXT_CHECK" | tee -a "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    
    # 等待下次检查
    sleep "$CHECK_INTERVAL_SECONDS"
done