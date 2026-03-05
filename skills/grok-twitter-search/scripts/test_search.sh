#!/bin/bash
# Grok Twitter Search 双模态测试脚本 (基于 uv 环境)

# 检查环境变量
if [ -z "$GROK_API_KEY" ]; then
    echo "❌ 错误：GROK_API_KEY 环境变量未设置"
    echo ""
    echo "请先运行配置向导："
    echo "  uv run scripts/setup_interactive.py"
    echo "或手动设置："
    echo "  export GROK_API_KEY=\"your_api_key_here\""
    exit 1
fi

# 默认 API 配置
API_BASE="${GROK_API_BASE:-https://api.x.ai/v1}"
PROXY="${SOCKS5_PROXY:-socks5://127.0.0.1:40000}"

echo "🔍 Grok Twitter Search 双引擎连通性测试"
echo "========================================"
echo "API Base : $API_BASE"
echo "API Key  : ${GROK_API_KEY:0:8}******${GROK_API_KEY: -6}"
echo "当前代理 : $PROXY"
echo "运行环境 : uv (虚拟环境隔离)"
echo "========================================"
echo ""

QUERY="elon musk latest tweets"
echo "搜索关键词：'$QUERY'"
echo ""

# 测试 1：极速检索模式 (grok-4-1-fast)
echo "▶️ [测试 1/2] 执行极速检索 (默认模式, 极低 Token 消耗)..."
uv run scripts/search_twitter.py \
    --query "$QUERY" \
    --max-results 2 \
    --api-key "$GROK_API_KEY" \
    --api-base "$API_BASE" \
    --proxy "$PROXY"
echo -e "\n----------------------------------------\n"

# 测试 2：深度推理模式 (grok-4-1-fast-reasoning)
echo "▶️ [测试 2/2] 执行深度舆情分析 (启用 --analyze 推理模式)..."
uv run scripts/search_twitter.py \
    --query "$QUERY" \
    --max-results 2 \
    --api-key "$GROK_API_KEY" \
    --api-base "$API_BASE" \
    --proxy "$PROXY" \
    --analyze

echo -e "\n✅ 测试完成！请对比上方两次调用的 usage 字段，确认 Token 消耗差异。"