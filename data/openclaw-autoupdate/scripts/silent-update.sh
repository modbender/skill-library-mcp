#!/bin/bash
#
# OpenClaw 静默更新脚本
#

set -e

LOG_DIR="${HOME}/.openclaw/logs"
LOG_FILE="${LOG_DIR}/autoupdate.log"

mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "=== OpenClaw 更新开始 ==="

# 检查版本
CURRENT=$(openclaw --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "unknown")
log "当前版本: ${CURRENT}"

LATEST=$(npm view openclaw version 2>/dev/null || echo "unknown")
log "最新版本: ${LATEST}"

if [ "$CURRENT" = "$LATEST" ]; then
    log "已是最新版本"
    exit 0
fi

# 更新
if command -v pnpm &> /dev/null; then
    pnpm add -g openclaw@latest 2>&1 | tee -a "$LOG_FILE"
elif command -v npm &> /dev/null; then  
    npm i -g openclaw@latest 2>&1 | tee -a "$LOG_FILE"
fi

# 重启
openclaw gateway restart 2>&1 | tee -a "$LOG_FILE" || true
sleep 3

# 验证
if openclaw gateway status &> /dev/null; then
    log "更新成功"
else
    log "请检查服务状态"
fi

log "=== 完成 ==="
