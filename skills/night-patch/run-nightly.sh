#!/bin/bash
# NightPatch 夜间自动运行脚本

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SKILL_DIR/logs/nightly-run-$(date +%Y%m%d).log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "========================================" >> "$LOG_FILE"
echo "NightPatch 夜间运行 - $TIMESTAMP" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# 检查是否应该运行（避免生产环境）
if [ "$NODE_ENV" = "production" ]; then
    echo "⚠️  生产环境，跳过夜间修补" >> "$LOG_FILE"
    exit 0
fi

# 运行夜间修补
cd "$SKILL_DIR"
echo "开始运行夜间修补..." >> "$LOG_FILE"

# 检查是否在测试环境，如果是则使用dry-run
if [ "$NODE_ENV" = "production" ]; then
    echo "⚠️  生产环境，跳过执行" >> "$LOG_FILE"
    exit 0
fi

# 默认使用dry-run模式（只检测不执行）
# 如需实际执行，请修改为：./start.sh run
if ./start.sh dry-run >> "$LOG_FILE" 2>&1; then
    echo "✅ 夜间修补检测完成（dry-run模式）" >> "$LOG_FILE"
    echo "   如需实际执行，请手动运行: ./start.sh run" >> "$LOG_FILE"
else
    echo "❌ 夜间修补检测失败" >> "$LOG_FILE"
    # 发送错误通知（可以扩展）
    echo "错误详情请查看日志: $LOG_FILE" >> "$LOG_FILE"
fi

echo "运行完成时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
