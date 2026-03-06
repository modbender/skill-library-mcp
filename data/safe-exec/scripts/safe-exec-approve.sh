#!/bin/bash
# safe-exec-approve - 批准待执行的命令

REQUEST_ID="$1"
SAFE_EXEC_DIR="$HOME/.openclaw/safe-exec"
PENDING_DIR="$SAFE_EXEC_DIR/pending"

if [[ -z "$REQUEST_ID" ]]; then
    echo "用法: safe-exec-approve <request_id>"
    echo ""
    echo "查看待处理的请求:"
    echo "  ls ~/.openclaw/safe-exec/pending/"
    exit 1
fi

REQUEST_FILE="$PENDING_DIR/$REQUEST_ID.json"

if [[ ! -f "$REQUEST_FILE" ]]; then
    echo "❌ 请求 $REQUEST_ID 不存在"
    exit 1
fi

# 读取请求信息
COMMAND=$(jq -r '.command' "$REQUEST_FILE")
RISK=$(jq -r '.risk' "$REQUEST_FILE")

# 检测运行环境
IS_INTERACTIVE=false
if [[ -t 0 ]]; then
    # 检查 stdin 是否是终端
    IS_INTERACTIVE=true
fi

# 检查是否由 OpenClaw Agent 调用
if [[ -n "$OPENCLAW_AGENT_CALL" ]] || [[ -n "$SAFE_EXEC_AUTO_CONFIRM" ]]; then
    IS_INTERACTIVE=false
fi

echo "⚠️  即将执行以下命令："
echo ""
echo "风险等级: ${RISK^^}"
echo "命令: $COMMAND"
echo ""

# 请求确认（仅在交互式环境）
if [[ "$IS_INTERACTIVE" == "true" ]]; then
    read -p "确认执行？(yes/no): " confirm
    if [[ "$confirm" != "yes" ]]; then
        echo "❌ 已取消"
        exit 0
    fi
    echo "✅ 已确认"
else
    echo "🤖 非交互式环境 - 自动跳过确认"
fi

# 标记为已批准并执行
jq '.status = "approved"' "$REQUEST_FILE" > "$REQUEST_FILE.tmp" && mv "$REQUEST_FILE.tmp" "$REQUEST_FILE"

echo "✅ 执行中..."
eval "$COMMAND"
exit_code=$?

# 清理已处理的请求
rm "$REQUEST_FILE"

if [[ $exit_code -eq 0 ]]; then
    echo "✅ 命令执行成功"
else
    echo "⚠️  命令执行失败（退出码: $exit_code）"
fi

exit $exit_code
