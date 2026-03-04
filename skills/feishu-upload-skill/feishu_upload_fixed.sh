#!/bin/bash
# 飞书文件上传工具 - 修复版

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
    echo "示例: $0 test.txt nodcnvFRC2MkW7uFVUgiluN217e"
    exit 1
fi

FILE_PATH="$1"
FOLDER_TOKEN="${2:-nodcnvFRC2MkW7uFVUgiluN217e}"  # 使用默认根目录token

if [[ ! -f "$FILE_PATH" ]]; then
    echo "错误: 文件不存在: $FILE_PATH"
    exit 1
fi

FILE_NAME=$(basename "$FILE_PATH")
FILE_SIZE=$(stat -c%s "$FILE_PATH")

echo "上传文件: $FILE_NAME"
echo "文件大小: $FILE_SIZE 字节"
echo "目标文件夹Token: $FOLDER_TOKEN"

# 第一步：获取上传预授权
echo -e "\n1. 获取上传预授权..."
PAYLOAD="{\"file_name\":\"$FILE_NAME\",\"parent_type\":\"explorer\",\"size\":$FILE_SIZE,\"parent_node\":\"$FOLDER_TOKEN\"}"

echo "请求载荷: $PAYLOAD"

PREPARE_RESPONSE=$(curl -s -X POST \
    "https://open.feishu.cn/open-apis/drive/v1/files/upload_prepare" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json; charset=utf-8" \
    -d "$PAYLOAD")

echo "响应: $PREPARE_RESPONSE"

# 检查响应代码
CODE=$(echo "$PREPARE_RESPONSE" | grep -o '"code":[0-9]*' | cut -d: -f2)
if [[ "$CODE" != "0" ]]; then
    echo "错误: 获取上传预授权失败, 代码: $CODE"
    MSG=$(echo "$PREPARE_RESPONSE" | grep -o '"msg":"[^"]*"' | cut -d'"' -f4)
    echo "错误信息: $MSG"
    exit 1
fi

echo "✅ 预授权成功"

# 对于小文件，可能不需要分块上传
# 尝试直接使用简单上传API
echo -e "\n2. 尝试直接上传..."

# 获取MIME类型
MIME_TYPE=$(file --mime-type -b "$FILE_PATH" 2>/dev/null || echo "text/plain")

# 使用简单上传API（适用于小文件）
echo "使用简单上传API..."
SIMPLE_RESPONSE=$(curl -s -X POST \
    "https://open.feishu.cn/open-apis/drive/v1/files/upload_all" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: multipart/form-data" \
    -F "file_name=$FILE_NAME" \
    -F "parent_type=explorer" \
    -F "parent_node=$FOLDER_TOKEN" \
    -F "file=@$FILE_PATH;type=$MIME_TYPE")

echo "简单上传响应: $SIMPLE_RESPONSE"

# 检查简单上传是否成功
SIMPLE_CODE=$(echo "$SIMPLE_RESPONSE" | grep -o '"code":[0-9]*' | cut -d: -f2)
if [[ "$SIMPLE_CODE" == "0" ]]; then
    # 提取文件信息
    FILE_TOKEN=$(echo "$SIMPLE_RESPONSE" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
    FILE_URL=$(echo "$SIMPLE_RESPONSE" | grep -o '"url":"[^"]*"' | cut -d'"' -f4)
    
    if [[ -n "$FILE_TOKEN" && -n "$FILE_URL" ]]; then
        echo -e "\n✅ 文件上传成功 (简单上传)!"
        echo "文件Token: $FILE_TOKEN"
        echo "文件URL: $FILE_URL"
        
        # 保存结果
        echo "{\"token\":\"$FILE_TOKEN\",\"url\":\"$FILE_URL\",\"name\":\"$FILE_NAME\",\"method\":\"simple\"}" > upload_result.json
        echo "结果已保存到: upload_result.json"
        exit 0
    fi
fi

echo "简单上传失败，尝试分块上传..."

# 分块上传流程
UPLOAD_ID=$(echo "$PREPARE_RESPONSE" | grep -o '"upload_id":"[^"]*"' | cut -d'"' -f4)
BLOCK_SIZE=$(echo "$PREPARE_RESPONSE" | grep -o '"block_size":[0-9]*' | cut -d: -f2)
BLOCK_NUM=$(echo "$PREPARE_RESPONSE" | grep -o '"block_num":[0-9]*' | cut -d: -f2)

echo "上传ID: $UPLOAD_ID"
echo "块大小: $BLOCK_SIZE"
echo "块数量: $BLOCK_NUM"

if [[ -z "$UPLOAD_ID" ]]; then
    echo "错误: 无法获取上传ID"
    exit 1
fi

# 对于小文件，可能只需要一个块
echo -e "\n3. 上传文件块..."
# 这里简化处理，假设文件小于块大小
UPLOAD_PART_RESPONSE=$(curl -s -X PUT \
    "https://open.feishu.cn/open-apis/drive/v1/files/upload_part" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: $MIME_TYPE" \
    -H "Upload-ID: $UPLOAD_ID" \
    -H "X-Tt-Logid: $(date +%s)" \
    -H "Seq: 0" \
    -H "Size: $FILE_SIZE" \
    --data-binary @"$FILE_PATH")

echo "上传块响应: $UPLOAD_PART_RESPONSE"

# 完成上传
echo -e "\n4. 完成上传..."
FINISH_RESPONSE=$(curl -s -X POST \
    "https://open.feishu.cn/open-apis/drive/v1/files/upload_finish" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json; charset=utf-8" \
    -d "{\"upload_id\":\"$UPLOAD_ID\"}")

echo "完成响应: $FINISH_RESPONSE"

# 提取文件信息
FILE_TOKEN=$(echo "$FINISH_RESPONSE" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
FILE_URL=$(echo "$FINISH_RESPONSE" | grep -o '"url":"[^"]*"' | cut -d'"' -f4)

if [[ -n "$FILE_TOKEN" && -n "$FILE_URL" ]]; then
    echo -e "\n✅ 文件上传成功 (分块上传)!"
    echo "文件Token: $FILE_TOKEN"
    echo "文件URL: $FILE_URL"
    
    # 保存结果
    echo "{\"token\":\"$FILE_TOKEN\",\"url\":\"$FILE_URL\",\"name\":\"$FILE_NAME\",\"method\":\"multipart\"}" > upload_result.json
    echo "结果已保存到: upload_result.json"
else
    echo "警告: 无法提取完整的文件信息"
    echo "原始响应: $FINISH_RESPONSE"
    exit 1
fi