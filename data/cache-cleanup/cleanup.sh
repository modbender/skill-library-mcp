#!/bin/bash
# Cache Cleanup - 缓存清理

LOG_FILE="/tmp/cache-cleanup-$(date +%Y%m%d).log"
WORKSPACE="/root/.openclaw"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_disk() {
    DF=$(df -h "$WORKSPACE" | tail -1 | awk '{print $5}' | sed 's/%//')
    log "当前磁盘使用率: ${DF}%"
    if [ "$DF" -gt 80 ]; then
        log "⚠️ 磁盘使用率超过 80%，增强清理"
    fi
}

cleanup_dir() {
    local dir=$1
    local days=$2
    local desc=$3
    
    if [ -d "$dir" ]; then
        count=$(find "$dir" -type f -mtime +$days 2>/dev/null | wc -l)
        size=$(find "$dir" -type f -mtime +$days -exec du -ch {} + 2>/dev/null | tail -1 | cut -f1)
        if [ "$count" -gt 0 ]; then
            log "清理 $desc (>$days天): $count 个文件, $size"
            find "$dir" -type f -mtime +$days -delete 2>/dev/null
        else
            log "无 $desc 需要清理"
        fi
    fi
}

log "========== 开始缓存清理 =========="

# 检查磁盘使用率
check_disk

# 1. 清理日志文件 (14天)
log "检查日志文件..."
cleanup_dir "$WORKSPACE/logs" 14 "日志"

# 2. 清理浏览器缓存 (3天)
log "检查浏览器缓存..."
cleanup_dir "$WORKSPACE/browser" 3 "浏览器缓存"

# 3. 清理 Canvas 缓存 (3天)
log "检查 Canvas 缓存..."
cleanup_dir "$WORKSPACE/canvas" 3 "Canvas缓存"

# 4. 清理 sandbox (7天)
log "检查沙箱..."
cleanup_dir "$WORKSPACE/sandbox" 7 "沙箱"
cleanup_dir "$WORKSPACE/sandbox-neko" 7 "猫娘沙箱"

# 5. 清理 tmp 目录 (1天)
log "检查临时目录..."
if [ -d "/tmp" ]; then
    # 清理 openclaw 相关临时文件
    count=$(find /tmp -name "openclaw*" -type f -mtime +1 2>/dev/null | wc -l)
    if [ "$count" -gt 0 ]; then
        log "清理临时文件: $count 个"
        find /tmp -name "openclaw*" -type f -mtime +1 -delete 2>/dev/null
    fi
fi

# 6. 清理 cron tmp 文件
log "检查 cron 临时文件..."
find "$WORKSPACE/cron" -name "*.tmp" -type f -delete 2>/dev/null

# 7. 清理 projects 缓存 (如果有)
log "检查项目缓存..."
if [ -d "$WORKSPACE/projects" ]; then
    find "$WORKSPACE/projects" -name "node_modules" -type d -empty -delete 2>/dev/null
    find "$WORKSPACE/projects" -name ".cache" -type d -mtime +7 -exec rm -rf {} + 2>/dev/null
fi

# 最终磁盘使用率
log "========== 清理完成 =========="
check_disk
log "日志: $LOG_FILE"
