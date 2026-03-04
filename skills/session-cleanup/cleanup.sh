#!/bin/bash
# Session Cleanup - 会话过期评估与清理

LOG_FILE="/tmp/session-cleanup-$(date +%Y%m%d).log"
WORKSPACE="/root/.openclaw"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========== 开始会话清理 =========="

# 1. 清理 cron runs (超过3天)
log "检查 cron/runs 目录..."
find "$WORKSPACE/cron/runs" -name "*.jsonl" -mtime +3 -type f 2>/dev/null | while read f; do
    log "删除过期 cron run: $(basename "$f")"
    rm -f "$f"
done

# 2. 清理 delivery-queue (超过1天)
log "检查 delivery-queue 目录..."
find "$WORKSPACE/delivery-queue" -name "*.json" -mtime +1 -type f 2>/dev/null | while read f; do
    log "删除过期投递: $(basename "$f")"
    rm -f "$f"
done

# 3. 清理 telegram 会话 (超过7天)
log "检查 telegram 目录..."
if [ -d "$WORKSPACE/telegram" ]; then
    find "$WORKSPACE/telegram" -type f -mtime +7 2>/dev/null | while read f; do
        log "删除过期 telegram 文件: $(basename "$f")"
        rm -f "$f"
    done
fi

# 4. 清理 subagents (超过7天)
log "检查 subagents 目录..."
if [ -d "$WORKSPACE/subagents" ]; then
    find "$WORKSPACE/subagents" -type f -mtime +7 2>/dev/null | while read f; do
        log "删除过期 subagent 文件: $(basename "$f")"
        rm -f "$f"
    done
fi

# 5. 清理临时备份文件
log "清理临时备份文件..."
find "$WORKSPACE" -name "*.bak*" -mtime +3 -type f 2>/dev/null | while read f; do
    log "删除过期备份: $f"
    rm -f "$f"
done

# 6. 清理 memory 临时文件
log "清理 memory 临时文件..."
find "$WORKSPACE/memory" -name "*.tmp-*" -type f 2>/dev/null | while read f; do
    log "删除临时文件: $(basename "$f")"
    rm -f "$f"
done

# 统计
CRON_COUNT=$(find "$WORKSPACE/cron/runs" -name "*.jsonl" 2>/dev/null | wc -l)
QUEUE_COUNT=$(find "$WORKSPACE/delivery-queue" -name "*.json" 2>/dev/null | wc -l)

log "========== 清理完成 =========="
log "剩余 cron runs: $CRON_COUNT"
log "剩余 delivery-queue: $QUEUE_COUNT"
log "日志: $LOG_FILE"
