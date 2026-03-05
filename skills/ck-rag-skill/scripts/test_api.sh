#!/bin/bash
# RAGFlow API测试脚本

echo "=== RAGFlow API 连接测试 ==="
echo ""

# 测试1: 检查API是否可达
echo "测试1: API连接性"
curl -I http://172.28.20.46:30001/v1/conversation/completion --connect-timeout 5 -s -o /dev/null -w "HTTP状态码: %{http_code}\n"
echo ""

# 测试2: 检查网络延迟
echo "测试2: 网络延迟"
ping -c 3 172.28.20.46
echo ""

# 测试3: 快速查询（简单问题）
echo "测试3: 快速查询 - '你好'"
python3 /home/onestack/.openclaw/workspace/ragflow-kb/scripts/query_ragflow.py "你好"
echo ""
echo "=== 测试完成 ==="
