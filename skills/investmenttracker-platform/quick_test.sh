#!/bin/bash
# InvestmentTracker MCP API 快速测试脚本

echo "=========================================="
echo "InvestmentTracker MCP API 快速测试"
echo "=========================================="
echo ""

# 设置变量
URL="https://investmenttracker-ingest-production.up.railway.app/mcp"
TOKEN="it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
OUTPUT_FILE="/tmp/mcp_response_$(date +%s).txt"

echo "1. 测试基本连接..."
echo "------------------------------------------"
curl -s -o "$OUTPUT_FILE" -w "状态码: %{http_code}\n大小: %{size_download}字节\n" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: text/event-stream" \
  "$URL"

echo ""
echo "响应文件: $OUTPUT_FILE"
echo "文件大小: $(wc -c < "$OUTPUT_FILE") 字节"
echo ""

echo "2. 查看响应开头..."
echo "------------------------------------------"
head -c 500 "$OUTPUT_FILE"
echo -e "\n... [截断] ..."

echo ""
echo "3. 查看响应结尾..."
echo "------------------------------------------"
tail -c 500 "$OUTPUT_FILE"
echo ""

echo "4. 检查SSE格式..."
echo "------------------------------------------"
echo "事件分隔符数量: $(grep -c '^$' "$OUTPUT_FILE" || echo "0")"
echo "数据行数量: $(grep -c '^data:' "$OUTPUT_FILE" || echo "0")"
echo "事件行数量: $(grep -c '^event:' "$OUTPUT_FILE" || echo "0")"
echo "注释行数量: $(grep -c '^:' "$OUTPUT_FILE" || echo "0")"
echo ""

echo "5. 尝试解析JSON..."
echo "------------------------------------------"
# 提取第一个数据块
FIRST_DATA=$(grep -m1 '^data:' "$OUTPUT_FILE" | sed 's/^data: //' 2>/dev/null || echo "")
if [ -n "$FIRST_DATA" ]; then
    echo "第一个数据块:"
    echo "$FIRST_DATA" | python3 -m json.tool 2>&1 | head -20
else
    echo "未找到数据块"
fi

echo ""
echo "6. 检查错误位置附近..."
echo "------------------------------------------"
# 如果文件足够大，检查16738位置附近
FILE_SIZE=$(wc -c < "$OUTPUT_FILE")
if [ "$FILE_SIZE" -gt 17000 ]; then
    echo "文件大小: $FILE_SIZE 字节"
    echo "检查位置 16600-16900:"
    dd if="$OUTPUT_FILE" bs=1 skip=16600 count=300 2>/dev/null | cat -v
    echo ""
else
    echo "文件太小 ($FILE_SIZE 字节)，无法检查错误位置"
fi

echo ""
echo "7. 测试POST请求..."
echo "------------------------------------------"
POST_RESPONSE="/tmp/mcp_post_$(date +%s).txt"
cat > /tmp/mcp_request.json << EOF
{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 1
}
EOF

curl -s -o "$POST_RESPONSE" -w "状态码: %{http_code}\n" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: text/event-stream" \
  -H "Content-Type: application/json" \
  -X POST \
  --data-binary @/tmp/mcp_request.json \
  "$URL"

echo "POST响应大小: $(wc -c < "$POST_RESPONSE") 字节"
echo ""

echo "=========================================="
echo "测试完成"
echo "=========================================="
echo ""
echo "分析建议:"
echo "1. 如果响应是SSE格式，需要专门的SSE客户端"
echo "2. 如果响应包含JSON数据，检查格式是否正确"
echo "3. 如果响应为空或错误，检查API可用性"
echo ""
echo "关键文件:"
echo "- 响应文件: $OUTPUT_FILE"
echo "- POST响应: $POST_RESPONSE"
echo "- 请求JSON: /tmp/mcp_request.json"