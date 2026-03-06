#!/bin/bash
# 狗蛋记忆层备份脚本 - 每周一次
# 备份 memory/ 目录

WORKSPACE="/root/.openclaw/workspace"
BACKUP_DIR="/root/.openclaw/backup"
ONEDRIVE="OneDrive:/备份/OpenClaw"
LOG_FILE="$BACKUP_DIR/memory-backup.log"

log() {
    echo "[$(date)] $1" | tee -a $LOG_FILE
}

DATE=$(date +%Y%m%d)
log "开始记忆层备份..."

# 创建临时目录
mkdir -p $BACKUP_DIR/temp

# 打包记忆层
tar -czf $BACKUP_DIR/temp/goudan-memory-$DATE.tar.gz \
    -C $WORKSPACE \
    memory/ 2>/dev/null || true

# 同步到 OneDrive
log "同步到 OneDrive..."
if rclone copy $BACKUP_DIR/temp/ $ONEDRIVE/ --progress 2>&1 | tee -a $LOG_FILE; then
    log "✅ 记忆层备份同步完成"
else
    log "❌ 记忆层备份同步失败"
fi

# 清理临时文件
rm -rf $BACKUP_DIR/temp/*

# 保留本地最近 30 天
find $BACKUP_DIR -name "goudan-memory-*.tar.gz" -mtime +30 -delete 2>/dev/null || true
