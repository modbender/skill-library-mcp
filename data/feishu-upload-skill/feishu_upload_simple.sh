#!/bin/bash
# 飞书文件上传工具 - 简化版

set -e

# 加载访问令牌
TOKEN_FILE="/home/node/.openclaw/workspace/feishu_token.txt"
if [[ ! -f "$TOKEN_FILE" ]]; then
    echo "错误: 找不到访问令牌文件"
    exit 1
fi

ACCESS_TOKEN=$(cat "$TOKEN_FILE" | tr -d '\n')
echo "使用访问令牌: ${ACCESS_TOKEN:0:30}..."

# 检查参数
if [[ $# -lt 1 ]]; then
    echo "用法: $0 <文件路径> [文件夹token]"
    echo "示例: $0 test.txt"
    exit 1
fi

FILE_PATH="$1"
FOLDER_TOKEN="$2"

if [[ ! -f "$FILE_PATH" ]]; then
    echo "错误: 文件不存在: $FILE_PATH"
    exit 1
fi

FILE_NAME=$(basename "$FILE_PATH")
FILE_SIZE=$(stat -c%s "$FILE_PATH")

echo "上传文件: $FILE_NAME"
echo "文件大小: $FILE_SIZE 字节"

# 第一步：获取上传预授权
echo "第一步：获取上传预授权..."
PAYLOAD="{\"file_name\":\"$FILE_NAME\",\"parent_type\":\"explorer\",\"size\":$FILE_SIZE"
if [[ -n "$FOLDER_TOKEN" ]]; then
    PAYLOAD="${PAYLOAD},\"parent_node\":\"$FOLDER_TOKEN\""
fi
PAYLOAD="${PAYLOAD}}"

PREPARE_RESPONSE=$(curl -s -X POST \
    "https://open.feishu.cn/open-apis/drive/v1/files/upload_prepare" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json; charset=utf-8" \
    -d "$PAYLOAD")

echo "预授权响应: $PREPARE_RESPONSE"

# 提取upload_token和upload_url
UPLOAD_TOKEN=$(echo "$PREPARE_RESPONSE" | grep -o '"upload_token":"[^"]*"' | cut -d'"' -f4)
UPLOAD_URL=$(echo "$PREPARE_RESPONSE" | grep -o '"upload_url":"[^"]*"' | cut -d'"' -f4)

if [[ -z "$UPLOAD_TOKEN" || -z "$UPLOAD_URL" ]]; then
    echo "错误: 无法获取上传信息"
    exit 1
fi

echo "上传Token: $UPLOAD_TOKEN"
echo "上传URL: $UPLOAD_URL"

# 第二步：上传文件内容
echo "第二步：上传文件内容..."
MIME_TYPE=$(file --mime-type -b "$FILE_PATH" || echo "application/octet-stream")

UPLOAD_RESPONSE=$(curl -s -X PUT \
    "$UPLOAD_URL" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: $MIME_TYPE" \
    --data-binary @"$FILE_PATH" \
    -w "\n%{http_code}")

HTTP_CODE=$(echo "$UPLOAD_RESPONSE" | tail -1)

if [[ "$HTTP_CODE" != "200" && "$HTTP_CODE" != "201" && "$HTTP_CODE" != "204" ]]; then
    echo "错误: 文件内容上传失败, HTTP代码: $HTTP_CODE"
    exit 1
fi

echo "文件内容上传成功"

# 第三步：完成上传
echo "第三步：完成上传..."
FINISH_RESPONSE=$(curl -s -X POST \
    "https://open.feishu.cn/open-apis/drive/v1/files/upload_finish" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json; charset=utf-8" \
    -d "{\"upload_token\":\"$UPLOAD_TOKEN\"}")

echo "完成响应: $FINISH_RESPONSE"

# 提取文件信息
FILE_TOKEN=$(echo "$FINISH_RESPONSE" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
FILE_URL=$(echo "$FINISH_RESPONSE" | grep -o '"url":"[^"]*"' | cut -d'"' -f4)

if [[ -n "$FILE_TOKEN" && -n "$FILE_URL" ]]; then
    echo "✅ 文件上传成功!"
    echo "文件Token: $FILE_TOKEN"
    echo "文件URL: $FILE_URL"
    
    # 保存结果
    echo "{\"token\":\"$FILE_TOKEN\",\"url\":\"$FILE_URL\",\"name\":\"$FILE_NAME\"}" > upload_result.json
    echo "结果已保存到: upload_result.json"
else
    echo "警告: 无法提取完整的文件信息"
    echo "原始响应: $FINISH_RESPONSE"
fi