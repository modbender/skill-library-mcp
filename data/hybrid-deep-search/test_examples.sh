#!/bin/bash
# Hybrid Deep Search 测试示例

echo "========================================="
echo "Hybrid Deep Search 测试"
echo "========================================="
echo ""

# 测试路由器
echo "📊 测试 1: 路由器分析"
echo "-----------------------------------------"
cd /tmp/hybrid-deep-search/scripts

echo "简单查询:"
python3 router.py "what is OpenClaw?"
echo ""

echo "复杂查询:"
python3 router.py "compare LangChain vs LlamaIndex in detail"
echo ""

echo "对比查询:"
python3 router.py "Python vs Go for backend"
echo ""

echo "========================================="
echo "测试完成"
echo "========================================="
