#!/bin/bash
# 狗蛋核心层备份脚本 - 文件修改时触发
# 监控文件: SOUL.md, AGENTS.md, IDENTITY.md, USER.md, TOOLS.md

WORKSPACE="/root/.openclaw/workspace"
BACKUP_DIR="/root/.openclaw/backup"
ONEDRIVE="OneDrive:/备份/OpenClaw"
LOG_FILE="$BACKUP_DIR/core-backup.log"

log() {
    echo "[$(date)] $1" | tee -a $LOG_FILE
}

backup_core() {
    DATE=$(date +%Y%m%d-%H%M%S)
    log "检测到核心文件变化，开始备份..."
    
    # 打包核心层
    tar -czf $BACKUP_DIR/temp/goudan-core-$DATE.tar.gz \
        -C $WORKSPACE \
        SOUL.md AGENTS.md IDENTITY.md USER.md TOOLS.md 2>/dev/null || true
    
    # 同步到 OneDrive
    log "同步到 OneDrive..."
    if rclone copy $BACKUP_DIR/temp/ $ONEDRIVE/ --progress 2>&1 | tee -a $LOG_FILE; then
        log "✅ 核心层备份同步完成"
    else
        log "❌ 核心层备份同步失败"
    fi
    
    # 清理临时文件
    rm -rf $BACKUP_DIR/temp/*
}

# 创建临时目录
mkdir -p $BACKUP_DIR/temp

# 监控核心层文件
log "开始监控核心层文件..."
inotifywait -m -e modify,create,move \
    $WORKSPACE/SOUL.md \
    $WORKSPACE/AGENTS.md \
    $WORKSPACE/IDENTITY.md \
    $WORKSPACE/USER.md \
    $WORKSPACE/TOOLS.md 2>/dev/null | while read event; do
    backup_core
done
