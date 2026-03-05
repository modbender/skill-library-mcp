#!/bin/bash

# Auto Rollback 脚本（使用 launchd）
# 用法:
#   ./auto-rollback.sh start  [--reason "说明"]  # 设置回滚
#   ./auto-rollback.sh cancel                     # 手动取消回滚
#   ./auto-rollback.sh status                     # 查看状态

STATE_FILE="$HOME/.openclaw/state/rollback-pending.json"
BACKUP_DIR="$HOME/.openclaw"
LOG_FILE="$HOME/.openclaw/logs/rollback.log"
LAUNCHD_LABEL="ai.openclaw.rollback"
OPENCLAW_CMD="/opt/homebrew/bin/openclaw"

# 确保目录存在
mkdir -p "$BACKUP_DIR" "$(dirname "$STATE_FILE")" "$(dirname "$LOG_FILE")"

log() {
    local msg="[$(date -Iseconds)] $1"
    echo "$msg" >> "$LOG_FILE"
    echo "$1"
}

cmd_start() {
    local REASON="手动修改配置"

    # Parse args: start [--reason "..."]
    while [ $# -gt 0 ]; do
        case "$1" in
            --reason)
                shift
                if [ -n "$1" ]; then
                    REASON="$1"
                    shift
                fi
                ;;
            *)
                # Backward-compat: allow passing reason as first positional arg
                if [ "$REASON" = "手动修改配置" ] && [ -n "$1" ]; then
                    REASON="$1"
                fi
                shift
                ;;
        esac
    done
    local BACKUP_FILE="$BACKUP_DIR/openclaw.json.$(date +%Y%m%d-%H%M%S)"
    
    # 1. 备份配置
    cp "$HOME/.openclaw/openclaw.json" "$BACKUP_FILE"
    if [ $? -ne 0 ]; then
        log "❌ 备份失败"
        exit 1
    fi
    log "✅ 配置已备份：$BACKUP_FILE"
    
    # 2. 创建 launchd plist（10 分钟后执行一次）
    local PLIST_FILE="$HOME/.openclaw/$LAUNCHD_LABEL.plist"
    local ROLLBACK_TIME=$(date -v+10M '+%Y-%m-%d %H:%M:%S +0800')
    local ROLLBACK_MIN=$(date -v+10M '+%M')
    local ROLLBACK_HOUR=$(date -v+10M '+%H')
    local ROLLBACK_DAY=$(date -v+10M '+%d')
    local ROLLBACK_MONTH=$(date -v+10M '+%m')
    local ROLLBACK_YEAR=$(date -v+10M '+%Y')
    
    # 创建回滚脚本
    local ROLLBACK_SCRIPT="$HOME/.openclaw/.rollback_execute.sh"
    cat > "$ROLLBACK_SCRIPT" << ROLLBACK_EOF
#!/bin/bash
echo "[$(date -Iseconds)] 🚨 回滚任务开始执行" >> "$LOG_FILE"
echo "[$(date -Iseconds)] 📥 恢复配置：$BACKUP_FILE" >> "$LOG_FILE"
cp "$BACKUP_FILE" "$HOME/.openclaw/openclaw.json"
if [ \$? -eq 0 ]; then
    echo "[$(date -Iseconds)] ✅ 配置已恢复" >> "$LOG_FILE"
    echo "[$(date -Iseconds)] 🔄 重启 Gateway..." >> "$LOG_FILE"
    $OPENCLAW_CMD gateway restart
    if [ \$? -eq 0 ]; then
        echo "[$(date -Iseconds)] ✅ Gateway 已重启" >> "$LOG_FILE"
        echo "[$(date -Iseconds)] 🎉 回滚成功" >> "$LOG_FILE"
    else
        echo "[$(date -Iseconds)] ❌ Gateway 重启失败" >> "$LOG_FILE"
    fi
else
    echo "[$(date -Iseconds)] ❌ 配置恢复失败" >> "$LOG_FILE"
fi
ROLLBACK_EOF
    chmod +x "$ROLLBACK_SCRIPT"
    
    cat > "$PLIST_FILE" << PLIST_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$LAUNCHD_LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$ROLLBACK_SCRIPT</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Minute</key>
        <integer>$ROLLBACK_MIN</integer>
        <key>Hour</key>
        <integer>$ROLLBACK_HOUR</integer>
        <key>Day</key>
        <integer>$ROLLBACK_DAY</integer>
        <key>Month</key>
        <integer>$ROLLBACK_MONTH</integer>
        <key>Year</key>
        <integer>$ROLLBACK_YEAR</integer>
    </dict>
    <key>RunAtLoad</key>
    <false/>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
        <key>HOME</key>
        <string>$HOME</string>
    </dict>
</dict>
</plist>
PLIST_EOF
    
    log "✅ launchd 任务已创建：$PLIST_FILE"
    log "⏰ 回滚时间：$ROLLBACK_TIME"
    
    # 3. 加载 launchd 任务
    launchctl load "$PLIST_FILE" 2>/dev/null
    if [ $? -eq 0 ]; then
        log "✅ launchd 任务已加载"
    else
        log "⚠️ launchd 任务加载失败（可能已存在）"
    fi
    
    # 4. 写状态文件
    cat > "$STATE_FILE" <<STATE_EOF
{
  "backup_file": "$BACKUP_FILE",
  "launchd_label": "$LAUNCHD_LABEL",
  "created_at": "$(date -Iseconds)",
  "rollback_at": "$ROLLBACK_TIME",
  "reason": "$REASON"
}
STATE_EOF
    log "✅ 状态文件已写入：$STATE_FILE"
    
    log "📋 下一步：重启 Gateway ($OPENCLAW_CMD gateway restart)"
    log "⚠️ 如果 Gateway 启动失败，10 分钟后自动回滚"
    log "✅ 如果 Gateway 启动成功，回滚会在下次 Gateway 成功启动时通过 BOOT.md 自动取消（也可手动 cancel）"
}

cmd_cancel() {
    if [ ! -f "$STATE_FILE" ]; then
        log "ℹ️  没有待处理的回滚任务"
        exit 0
    fi
    
    local LAUNCHD_LABEL=$(jq -r '.launchd_label' "$STATE_FILE")
    local PLIST_FILE="$HOME/.openclaw/$LAUNCHD_LABEL.plist"
    
    # 卸载 launchd 任务
    launchctl unload "$PLIST_FILE" 2>/dev/null
    if [ $? -eq 0 ]; then
        log "✅ launchd 任务已卸载"
    else
        log "⚠️ launchd 任务卸载失败（可能已执行或不存在）"
    fi
    
    # 删除 plist 文件
    rm -f "$PLIST_FILE"
    
    # 删除回滚脚本
    rm -f "$HOME/.openclaw/.rollback_execute.sh"
    
    # 删除状态文件
    rm -f "$STATE_FILE"
    
    log "✅ 回滚任务已手动取消"
}

cmd_status() {
    if [ ! -f "$STATE_FILE" ]; then
        echo "ℹ️  没有待处理的回滚任务"
        exit 0
    fi
    
    echo "📋 待处理回滚任务:"
    jq '.' "$STATE_FILE"
    
    echo ""
    echo "⏰ 回滚时间：$(jq -r '.rollback_at' "$STATE_FILE")"
    echo "📝 原因：$(jq -r '.reason' "$STATE_FILE")"
    
    # 检查 launchd 任务是否存在
    if launchctl list | grep -q "$(jq -r '.launchd_label' "$STATE_FILE")"; then
        echo "✅ launchd 任务：已加载"
    else
        echo "⚠️ launchd 任务：未加载（可能已执行）"
    fi
}

# 主入口
case "$1" in
    start)
        shift
        cmd_start "$@"
        ;;
    cancel)
        cmd_cancel
        ;;
    status)
        cmd_status
        ;;
    *)
        echo "用法：$0 {start|cancel|status} [reason]"
        echo ""
        echo "命令:"
        echo "  start   设置回滚任务（修改配置前调用）"
        echo "  cancel  手动取消回滚任务"
        echo "  status  查看回滚状态"
        exit 1
        ;;
esac
