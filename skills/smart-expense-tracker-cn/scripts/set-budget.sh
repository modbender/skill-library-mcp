#!/bin/bash
# 设置预算
# 用法: set-budget.sh 金额 [用户ID]

BUDGET="$1"
USER_ID="${2:-default}"
DATA_DIR="$HOME/.expense-tracker"
CONFIG_FILE="$DATA_DIR/config.json"

if [ -z "$BUDGET" ]; then
    echo '{"error": "请输入预算金额"}'
    exit 1
fi

# 验证金额
if ! [[ "$BUDGET" =~ ^[0-9]+\.?[0-9]*$ ]]; then
    echo '{"error": "金额格式不正确"}'
    exit 1
fi

# 创建目录
mkdir -p "$DATA_DIR"

# 更新或创建配置
if [ -f "$CONFIG_FILE" ]; then
    # 更新现有配置
    TMP_FILE=$(mktemp)
    jq ".monthlyBudget = $BUDGET" "$CONFIG_FILE" > "$TMP_FILE" && mv "$TMP_FILE" "$CONFIG_FILE"
else
    # 创建新配置
    cat > "$CONFIG_FILE" << EOF
{
  "monthlyBudget": $BUDGET,
  "categories": {
    "food": "餐饮",
    "transport": "交通",
    "shopping": "购物",
    "entertainment": "娱乐",
    "medical": "医疗",
    "education": "教育",
    "other": "其他"
  }
}
EOF
fi

echo "{\"success\": true, \"monthlyBudget\": $BUDGET, \"message\": \"月预算已设置为 ¥$BUDGET\"}"
