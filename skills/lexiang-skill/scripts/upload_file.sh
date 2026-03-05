#!/bin/bash
# 乐享知识库文件上传脚本（三步流程）
# 使用方式：bash scripts/upload_file.sh <文件路径> <知识库ID> [父节点ID]
#
# 前置条件：已通过 source scripts/init.sh 设置好环境变量
#   - $LEXIANG_TOKEN
#   - $LEXIANG_STAFF_ID

set -e

FILE_PATH="$1"
SPACE_ID="$2"
PARENT_ID="${3:-}"

if [ -z "$FILE_PATH" ] || [ -z "$SPACE_ID" ]; then
  echo "用法: bash scripts/upload_file.sh <文件路径> <知识库ID> [父节点ID]"
  echo "示例: bash scripts/upload_file.sh ./doc.md abc123 parent_entry_id"
  exit 1
fi

if [ ! -f "$FILE_PATH" ]; then
  echo "错误：文件不存在: $FILE_PATH"
  exit 1
fi

if [ -z "$LEXIANG_TOKEN" ] || [ -z "$LEXIANG_STAFF_ID" ]; then
  echo "错误：请先执行 source scripts/init.sh 加载凭证"
  exit 1
fi

FILE_NAME=$(basename "$FILE_PATH")
echo "准备上传文件: $FILE_NAME"

# 步骤1: 获取上传凭证
echo "步骤1: 获取上传凭证..."
UPLOAD_PARAMS=$(curl -s -X POST "https://lxapi.lexiangla.com/cgi-bin/v1/kb/files/upload-params" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "{\"name\": \"$FILE_NAME\", \"media_type\": \"file\"}")

BUCKET=$(echo "$UPLOAD_PARAMS" | jq -r '.options.Bucket')
REGION=$(echo "$UPLOAD_PARAMS" | jq -r '.options.Region')
KEY=$(echo "$UPLOAD_PARAMS" | jq -r '.object.key')
STATE=$(echo "$UPLOAD_PARAMS" | jq -r '.object.state')
AUTH=$(echo "$UPLOAD_PARAMS" | jq -r '.object.auth.Authorization')
COS_TOKEN=$(echo "$UPLOAD_PARAMS" | jq -r '.object.auth.XCosSecurityToken')

if [ -z "$BUCKET" ] || [ "$BUCKET" = "null" ]; then
  echo "错误：获取上传凭证失败"
  echo "$UPLOAD_PARAMS"
  exit 1
fi

echo "  Bucket: $BUCKET, Region: $REGION"

# 步骤2: 上传到腾讯云COS
echo "步骤2: 上传文件到COS..."
COS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X PUT \
  "https://${BUCKET}.cos.${REGION}.myqcloud.com/${KEY}" \
  -H "Authorization: $AUTH" \
  -H "x-cos-security-token: $COS_TOKEN" \
  -H "Content-Type: application/octet-stream" \
  --data-binary "@$FILE_PATH")

if [ "$COS_RESPONSE" != "200" ]; then
  echo "错误：上传到COS失败，HTTP状态码: $COS_RESPONSE"
  exit 1
fi
echo "  上传成功"

# 步骤3: 创建知识节点
echo "步骤3: 创建知识节点..."

if [ -n "$PARENT_ID" ]; then
  RELATIONSHIPS='"parent_entry": {"data": {"type": "kb_entry", "id": "'"$PARENT_ID"'"}}'
else
  RELATIONSHIPS=""
fi

CREATE_RESPONSE=$(curl -s -X POST \
  "https://lxapi.lexiangla.com/cgi-bin/v1/kb/entries?state=$STATE&space_id=$SPACE_ID" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "{
    \"data\": {
      \"type\": \"kb_entry\",
      \"attributes\": {
        \"entry_type\": \"file\",
        \"name\": \"$FILE_NAME\"
      }$([ -n "$RELATIONSHIPS" ] && echo ", \"relationships\": {$RELATIONSHIPS}")
    }
  }")

ENTRY_ID=$(echo "$CREATE_RESPONSE" | jq -r '.data.id // empty')

if [ -n "$ENTRY_ID" ] && [ "$ENTRY_ID" != "null" ]; then
  echo "上传完成！"
  echo "  Entry ID: $ENTRY_ID"
  echo "  文件名: $FILE_NAME"
else
  echo "警告：节点创建可能失败，请检查响应："
  echo "$CREATE_RESPONSE" | jq .
fi
