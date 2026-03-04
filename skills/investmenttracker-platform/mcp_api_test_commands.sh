#!/bin/bash
# InvestmentTracker MCP API 测试命令
# 用于验证MCP API的实际响应

echo "🔧 InvestmentTracker MCP API 测试命令"
echo "=========================================="

# API配置
API_URL="https://investmenttracker-ingest-production.up.railway.app/mcp"
API_KEY="it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"

echo "API URL: $API_URL"
echo "API Key: $API_KEY"
echo ""

# 1. 测试 tools/list - 获取工具列表
echo "1. 测试 tools/list - 获取可用工具列表"
echo "------------------------------------------"
cat << EOF
curl -v -X POST '$API_URL' \\
  -H 'X-API-Key: $API_KEY' \\
  -H 'Content-Type: application/json' \\
  -H 'Accept: application/json' \\
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 1
  }'
EOF
echo ""

# 2. 测试 tools/call whoami_v1 - 获取用户信息
echo "2. 测试 whoami_v1 - 获取用户信息"
echo "------------------------------------------"
cat << EOF
curl -v -X POST '$API_URL' \\
  -H 'X-API-Key: $API_KEY' \\
  -H 'Content-Type: application/json' \\
  -H 'Accept: application/json' \\
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "whoami_v1",
      "arguments": {}
    },
    "id": 2
  }'
EOF
echo ""

# 3. 测试 tools/call positions_list_v1 - 获取持仓列表
echo "3. 测试 positions_list_v1 - 获取持仓列表"
echo "------------------------------------------"
cat << EOF
curl -v -X POST '$API_URL' \\
  -H 'X-API-Key: $API_KEY' \\
  -H 'Content-Type: application/json' \\
  -H 'Accept: application/json' \\
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "positions_list_v1",
      "arguments": {
        "status": "POSITION",
        "limit": 10
      }
    },
    "id": 3
  }'
EOF
echo ""

# 4. 测试 tools/call methodology_get_v1 - 获取投资方法论
echo "4. 测试 methodology_get_v1 - 获取投资方法论"
echo "------------------------------------------"
cat << EOF
curl -v -X POST '$API_URL' \\
  -H 'X-API-Key: $API_KEY' \\
  -H 'Content-Type: application/json' \\
  -H 'Accept: application/json' \\
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "methodology_get_v1",
      "arguments": {}
    },
    "id": 4
  }'
EOF
echo ""

# 5. 测试 tools/call stats_quick_v1 - 获取快速统计
echo "5. 测试 stats_quick_v1 - 获取快速统计"
echo "------------------------------------------"
cat << EOF
curl -v -X POST '$API_URL' \\
  -H 'X-API-Key: $API_KEY' \\
  -H 'Content-Type: application/json' \\
  -H 'Accept: application/json' \\
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "stats_quick_v1",
      "arguments": {}
    },
    "id": 5
  }'
EOF
echo ""

# 6. 测试 resources/list - 获取资源列表
echo "6. 测试 resources/list - 获取资源列表"
echo "------------------------------------------"
cat << EOF
curl -v -X POST '$API_URL' \\
  -H 'X-API-Key: $API_KEY' \\
  -H 'Content-Type: application/json' \\
  -H 'Accept: application/json' \\
  -d '{
    "jsonrpc": "2.0",
    "method": "resources/list",
    "params": {},
    "id": 6
  }'
EOF
echo ""

# 7. 简化测试命令（只显示响应体）
echo "7. 简化测试命令（只显示响应体）"
echo "------------------------------------------"
cat << EOF
# 测试工具列表
curl -s -X POST '$API_URL' \\
  -H 'X-API-Key: $API_KEY' \\
  -H 'Content-Type: application/json' \\
  -H 'Accept: application/json' \\
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}'

# 测试持仓数据
curl -s -X POST '$API_URL' \\
  -H 'X-API-Key: $API_KEY' \\
  -H 'Content-Type: application/json' \\
  -H 'Accept: application/json' \\
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"positions_list_v1","arguments":{"status":"POSITION","limit":10}},"id":2}'
EOF
echo ""

# 8. 使用SSE模式测试（如果API需要）
echo "8. 使用SSE模式测试（Server-Sent Events）"
echo "------------------------------------------"
cat << EOF
# 使用SSE模式
curl -s -N -X POST '$API_URL' \\
  -H 'X-API-Key: $API_KEY' \\
  -H 'Content-Type: application/json' \\
  -H 'Accept: text/event-stream' \\
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}'

# 使用SSE模式获取持仓
curl -s -N -X POST '$API_URL' \\
  -H 'X-API-Key: $API_KEY' \\
  -H 'Content-Type: application/json' \\
  -H 'Accept: text/event-stream' \\
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"positions_list_v1","arguments":{"status":"POSITION","limit":10}},"id":2}'
EOF
echo ""

echo "🔍 调试建议："
echo "1. 先运行第7部分的简化命令，查看是否有响应"
echo "2. 如果没有响应，尝试第8部分的SSE模式"
echo "3. 使用-v参数查看详细的HTTP请求/响应"
echo "4. 检查API密钥是否正确"
echo "5. 检查网络连接是否正常"
echo ""
echo "📝 将curl命令的输出结果发给我，我可以帮你分析问题。"