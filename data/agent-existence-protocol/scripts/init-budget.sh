#!/usr/bin/env bash
# init-budget.sh — 初始化 agent 存在预算文件
# 用法: bash init-budget.sh <agent_id> <weekly_tokens> <workspace_path>

set -euo pipefail

AGENT_ID="${1:?用法: init-budget.sh <agent_id> <weekly_tokens> <workspace_path>}"
WEEKLY_TOKENS="${2:?请指定周 token 预算（如 500000）}"
WORKSPACE="${3:?请指定 workspace 路径}"

EXISTENCE_DIR="$WORKSPACE/existence"
mkdir -p "$EXISTENCE_DIR"

PERIOD_START=$(date +%Y-%m-%d)
PERIOD_END=$(date -d "+7 days" +%Y-%m-%d 2>/dev/null || date -v+7d +%Y-%m-%d)

cat > "$EXISTENCE_DIR/budget.md" << EOF
# 存在预算
- 周期：${PERIOD_START} ~ ${PERIOD_END}
- 总预算：${WEEKLY_TOKENS} tokens
- 已消耗：0 tokens
- 剩余：${WEEKLY_TOKENS} tokens
- 消耗率：0 tokens/天
- 预计耗尽：N/A
- 状态：存活
EOF

echo "✓ 预算文件已创建: $EXISTENCE_DIR/budget.md"
echo "  agent: $AGENT_ID | 预算: $WEEKLY_TOKENS tokens/周"
