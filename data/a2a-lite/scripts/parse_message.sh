#!/usr/bin/env bash
# 解析 A2A-Lite 协议消息
# 用法: parse_message.sh "<message>"
# 输出 JSON 格式的解析结果

set -euo pipefail

MESSAGE="$1"

# 检查是否为协议消息
if [[ ! "$MESSAGE" =~ ^\[A2A: ]]; then
    echo '{"isA2A": false}'
    exit 0
fi

# 提取标记行（第一行，去掉开头 [A2A: 和结尾 ]）
HEADER_LINE=$(echo "$MESSAGE" | head -1)
HEADER_CONTENT=$(echo "$HEADER_LINE" | sed 's/^\[A2A://' | sed 's/\]$//')

# 解析类型（第一个词）
TYPE=$(echo "$HEADER_CONTENT" | awk '{print $1}')

# 解析参数（key=value 格式）
PARAMS_JSON="{"
FIRST=true
for param in $(echo "$HEADER_CONTENT" | grep -oE '[a-z_-]+=[^ ]+' || true); do
    key=$(echo "$param" | cut -d= -f1)
    value=$(echo "$param" | cut -d= -f2-)
    if [[ "$FIRST" == "true" ]]; then
        FIRST=false
    else
        PARAMS_JSON+=", "
    fi
    PARAMS_JSON+="\"$key\": \"$value\""
done
PARAMS_JSON+="}"

# 提取消息体（第一行之后的内容）
BODY=$(echo "$MESSAGE" | tail -n +2)

# 构建 JSON 输出
echo -n '{"isA2A": true, "type": "'
echo -n "$TYPE"
echo -n '", "params": '
echo -n "$PARAMS_JSON"
echo -n ', "body": '
echo -n "$BODY" | jq -Rs '.'
echo '}'
