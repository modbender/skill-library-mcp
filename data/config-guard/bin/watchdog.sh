#!/bin/bash
# OpenClaw Gateway 守卫脚本 (watchdog.sh)
# 功能：检测 Gateway 是否运行，若连接失败则自动回滚最新的备份配置并重启

CONFIG_DIR="$HOME/.openclaw"
CONFIG_FILE="$CONFIG_DIR/openclaw.json"
BACKUP_DIR="$CONFIG_DIR/backups"
LOG_FILE="/tmp/openclaw-watchdog.log"

echo "[$(date)] Watchdog starting..." >> "$LOG_FILE"

# 1. 探测 Gateway 状态
# 尝试使用 openclaw status --probe 进行深探测
if ! openclaw gateway status --json | grep -q '"state": "active"'; then
    echo "[$(date)] ⚠️ Gateway detected as DOWN or UNREACHABLE." >> "$LOG_FILE"
    
    # 2. 查找最新的有效备份
    LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/openclaw-*.json 2>/dev/null | head -n 1)
    
    if [ -n "$LATEST_BACKUP" ]; then
        echo "[$(date)] 🔄 Attempting recovery using backup: $LATEST_BACKUP" >> "$LOG_FILE"
        
        # 3. 执行回滚 (先备份坏掉的，以防万一)
        cp "$CONFIG_FILE" "$BACKUP_DIR/failed-config-$(date +%Y%m%d-%H%M%S).json"
        cp "$LATEST_BACKUP" "$CONFIG_FILE"
        
        # 4. 重启 Gateway
        echo "[$(date)] 🚀 Restarting Gateway..." >> "$LOG_FILE"
        openclaw gateway restart --force
        
        # 5. 验证重启
        sleep 5
        if openclaw gateway status --json | grep -q '"state": "active"'; then
            echo "[$(date)] ✅ Recovery SUCCESSFUL." >> "$LOG_FILE"
            # 这里可以根据需要添加通知逻辑 (如 pushbullet 或 imessage)
        else
            echo "[$(date)] ❌ Recovery FAILED. Manual intervention required." >> "$LOG_FILE"
        fi
    else
        echo "[$(date)] ❌ No backup files found in $BACKUP_DIR. Cannot recover." >> "$LOG_FILE"
    fi
else
    # echo "[$(date)] Gateway is healthy." >> "$LOG_FILE"
    exit 0
fi
