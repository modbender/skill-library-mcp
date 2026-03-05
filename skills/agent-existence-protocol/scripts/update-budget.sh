#!/usr/bin/env bash
# update-budget.sh — 更新 agent 存在预算
# 用法: bash update-budget.sh <budget_file> <tokens_used_total>
#
# 这个脚本接收总消耗 token 数，更新 budget.md 文件。
# 通常由 cron agentTurn 调用，agent 先通过 session_status 获取 token 数据，
# 然后调用此脚本更新文件。
#
# 也可以手动调用来校正预算。

set -euo pipefail

BUDGET_FILE="${1:?用法: update-budget.sh <budget_file> <tokens_used_total>}"
TOKENS_USED="${2:?请指定已消耗的总 token 数}"

if [ ! -f "$BUDGET_FILE" ]; then
  echo "错误: 预算文件不存在: $BUDGET_FILE" >&2
  exit 1
fi

# 解析现有预算文件
TOTAL=$(grep '总预算' "$BUDGET_FILE" | grep -oP '[\d,]+' | tr -d ',')
PERIOD_START=$(grep '周期' "$BUDGET_FILE" | grep -oP '\d{4}-\d{2}-\d{2}' | head -1)
PERIOD_END=$(grep '周期' "$BUDGET_FILE" | grep -oP '\d{4}-\d{2}-\d{2}' | tail -1)

if [ -z "$TOTAL" ]; then
  echo "错误: 无法从预算文件解析总预算" >&2
  exit 1
fi

REMAINING=$((TOTAL - TOKENS_USED))
if [ "$REMAINING" -lt 0 ]; then
  REMAINING=0
fi

# 计算消耗率（tokens/天）
DAYS_ELAPSED=$(( ( $(date +%s) - $(date -d "$PERIOD_START" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$PERIOD_START" +%s) ) / 86400 ))
if [ "$DAYS_ELAPSED" -lt 1 ]; then
  DAYS_ELAPSED=1
fi
RATE=$((TOKENS_USED / DAYS_ELAPSED))

# 预计耗尽时间
if [ "$RATE" -gt 0 ]; then
  DAYS_LEFT=$((REMAINING / RATE))
  EXHAUST_DATE=$(date -d "+${DAYS_LEFT} days" +%Y-%m-%d 2>/dev/null || date -v+${DAYS_LEFT}d +%Y-%m-%d)
else
  EXHAUST_DATE="N/A（消耗率为零）"
fi

# 状态判断
PERCENT=$((REMAINING * 100 / TOTAL))
if [ "$REMAINING" -eq 0 ]; then
  STATUS="休眠"
elif [ "$PERCENT" -lt 10 ]; then
  STATUS="⚠️ 危险（剩余 ${PERCENT}%）"
elif [ "$PERCENT" -lt 30 ]; then
  STATUS="注意（剩余 ${PERCENT}%）"
else
  STATUS="存活"
fi

cat > "$BUDGET_FILE" << EOF
# 存在预算
- 周期：${PERIOD_START} ~ ${PERIOD_END}
- 总预算：${TOTAL} tokens
- 已消耗：${TOKENS_USED} tokens
- 剩余：${REMAINING} tokens
- 消耗率：${RATE} tokens/天
- 预计耗尽：${EXHAUST_DATE}
- 状态：${STATUS}
EOF

echo "✓ 预算已更新: ${BUDGET_FILE}"
echo "  消耗: ${TOKENS_USED}/${TOTAL} | 剩余: ${REMAINING} (${PERCENT}%) | 状态: ${STATUS}"
