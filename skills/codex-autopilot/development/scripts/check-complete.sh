#!/bin/bash
# 检查 task_plan.md 中所有阶段是否完成
# 完成返回 0，未完成返回 1
# 可用于验证任务是否完成

PLAN_FILE="${1:-task_plan.md}"

if [ ! -f "$PLAN_FILE" ]; then
    echo "错误: 未找到 $PLAN_FILE"
    echo "无法验证完成状态（没有任务计划）"
    exit 1
fi

echo "=== 任务完成检查 ==="
echo ""

# 统计各状态的阶段数量 (使用 -F 进行固定字符串匹配)
TOTAL=$(grep -c "### Phase" "$PLAN_FILE" 2>/dev/null | tr -d '\n' || echo 0)
COMPLETE=$(grep -cF "**Status:** complete" "$PLAN_FILE" 2>/dev/null | tr -d '\n' || echo 0)
IN_PROGRESS=$(grep -cF "**Status:** in_progress" "$PLAN_FILE" 2>/dev/null | tr -d '\n' || echo 0)
PENDING=$(grep -cF "**Status:** pending" "$PLAN_FILE" 2>/dev/null | tr -d '\n' || echo 0)

# 确保变量为有效整数
TOTAL=${TOTAL:-0}
COMPLETE=${COMPLETE:-0}
IN_PROGRESS=${IN_PROGRESS:-0}
PENDING=${PENDING:-0}

echo "总阶段数:   $TOTAL"
echo "已完成:     $COMPLETE"
echo "进行中:     $IN_PROGRESS"
echo "待开始:     $PENDING"
echo ""

# 计算完成百分比
if [ "$TOTAL" -gt 0 ]; then
    PERCENT=$((COMPLETE * 100 / TOTAL))
    echo "完成进度:   $PERCENT%"
    echo ""
fi

# 检查是否全部完成
if [ "$COMPLETE" -eq "$TOTAL" ] && [ "$TOTAL" -gt 0 ]; then
    echo "[OK] 所有阶段已完成"
    exit 0
else
    echo "[!] 任务未完成"
    echo ""
    if [ "$IN_PROGRESS" -gt 0 ]; then
        echo "当前进行中的阶段:"
        grep -B1 "in_progress" "$PLAN_FILE" 2>/dev/null | grep "### Phase" || true
    fi
    echo ""
    echo "请继续完成剩余阶段后再结束任务。"
    exit 1
fi
