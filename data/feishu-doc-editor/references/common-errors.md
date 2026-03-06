# 飞书文档 API 常见错误诊断与解决指南

本指南详细列出飞书文档编辑 API 使用过程中常见的错误、诊断方法和解决方案。

---

## 目录

1. [认证相关错误](#认证相关错误)
2. [权限相关错误](#权限相关错误)
3. [文档相关错误](#文档相关错误)
4. [请求格式错误](#请求格式错误)
5. [性能和限流错误](#性能和限流错误)
6. [调试技巧](#调试技巧)

---

## 认证相关错误

### 错误 1：缺少 tenant_access_token

**错误码**：`99991661`

**错误信息**：
```json
{
  "code": 99991661,
  "msg": "request token missing"
}
```

**症状**：
- API 调用立即失败
- 错误信息明确指出缺少 token

**原因分析**：
1. 请求头未包含 `Authorization` 字段
2. `Authorization` 字段格式不正确
3. token 值为空或格式错误

**解决方案**：

```bash
# ❌ 错误示例
curl -X POST "https://open.feishu.cn/open-apis/..." \
  -H "Content-Type: application/json" \
  -d '{"..."}'

# ✅ 正确示例
curl -X POST "https://open.feishu.cn/open-apis/..." \
  -H "Authorization: Bearer {tenant_access_token}" \
  -H "Content-Type: application/json" \
  -d '{"..."}'
```

**验证方法**：
```bash
# 检查请求头是否包含 Authorization
curl -v -X POST "https://open.feishu.cn/open-apis/..." \
  -H "Authorization: Bearer {tenant_access_token}" 2>&1 | grep -i authorization
```

---

### 错误 2：tenant_access_token 无效或过期

**错误码**：`99991663`

**错误信息**：
```json
{
  "code": 99991663,
  "msg": "invalid token"
}
```

**症状**：
- 之前能用的 token 突然失效
- API 调用返回 token 无效错误

**原因分析**：
1. token 已过期（有效期为 2 小时）
2. token 格式错误
3. app_id 或 app_secret 错误
4. 应用被禁用或删除

**解决方案**：

```bash
# 1. 重新获取 token
curl -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "your_app_id",
    "app_secret": "your_app_secret"
  }'

# 2. 验证返回的 token
{
  "code": 0,
  "tenant_access_token": "t-xxx",
  "expire": 7200
}

# 3. 在代码中实现自动续期
TOKEN_EXPIRE_TIME=$(date +%s)
EXPIRE_SECONDS=7200

# 检查是否需要刷新 token
if [ $(($(date +%s) - TOKEN_EXPIRE_TIME)) -gt $EXPIRE_SECONDS ]; then
  echo "Token expired, refreshing..."
  # 重新获取 token
fi
```

**验证方法**：
```bash
# 使用新 token 测试 API
NEW_TOKEN="t-new_token_here"
curl -X GET "https://open.feishu.cn/open-apis/docx/v1/documents/xxx/plaintext" \
  -H "Authorization: Bearer $NEW_TOKEN"
```

---

### 错误 3：app_id 或 app_secret 错误

**错误码**：`99991663`

**错误信息**：
```json
{
  "code": 99991663,
  "msg": "app_id or app_secret error"
}
```

**症状**：
- 获取 token 时失败
- 提示 app_id 或 app_secret 错误

**原因分析**：
1. app_id 或 app_secret 复制错误
2. 应用的凭证已重置
3. 使用了错误环境的凭证（测试 vs 生产）

**解决方案**：

```bash
# 1. 重新从飞书开放平台复制凭证
# 登录 https://open.feishu.cn
# 进入应用 → 凭证管理 → 复制

# 2. 验证凭证格式
# app_id 格式：cli_aXXXXXXXXXXXX
# app_secret 格式：32 位字符串

# 3. 测试凭证是否正确
curl -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "cli_a1234567890",
    "app_secret": "abcdefghijklmnopqrstuvwxyz123456"
  }'
```

---

## 权限相关错误

### 错误 4：应用没有文档访问权限（403 Forbidden）

**错误码**：`403`

**错误信息**：
```json
{
  "code": 403,
  "msg": "permission denied"
}
```

**症状**：
- token 有效，但无法访问特定文档
- 读取或编辑文档时返回 403

**原因分析**：
1. 应用未添加为文档协作者
2. 应用的 API 权限未申请
3. 应用的权限级别不足（只有查看权限，尝试编辑）

**解决方案**：

**方案 1：添加应用为文档协作者**
```
1. 打开目标文档
2. 点击右上角 "..." → "更多" → "添加文档应用"
3. 搜索并选择你的应用
4. 设置权限为"可编辑"
5. 点击"邀请"
```

**方案 2：检查应用 API 权限**
```
1. 登录飞书开放平台
2. 进入你的应用
3. 检查"权限管理"页面
4. 确认已申请以下权限：
   - docx:document:readonly（查看）
   - docx:document:write_only（编辑）
5. 如果未申请，立即申请
```

**验证方法**：
```bash
# 1. 列出文档协作者，确认应用在列表中
# 通过飞书客户端或 API 检查

# 2. 测试读取权限
curl -X GET "https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/plaintext" \
  -H "Authorization: Bearer {token}"

# 3. 测试编辑权限
curl -X POST "https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"children": [{"block_type": 2, "text": {"elements": [{"text_run": {"content": "test"}}]}}]}'
```

---

### 错误 5：API 权限未批准

**错误码**：`99991400`

**错误信息**：
```json
{
  "code": 99991400,
  "msg": "permission not approved"
}
```

**症状**：
- API 调用失败，提示权限未批准
- 应用虽然申请了权限，但审批未通过

**原因分析**：
1. 权限申请待审批
2. 权限申请被拒绝
3. 应用未发布

**解决方案**：

```
1. 检查权限审批状态
   - 登录飞书开放平台
   - 进入应用 → 权限管理
   - 查看权限状态（已批准/待审批/已拒绝）

2. 如果待审批
   - 联系企业管理员审批
   - 或提供更详细的申请理由

3. 如果被拒绝
   - 重新提交申请
   - 提供详细的使用场景说明
   - 必要时联系飞书技术支持

4. 确保应用已发布
   - 进入"版本管理与发布"
   - 检查应用状态
   - 如果未发布，提交审核并发布
```

---

## 文档相关错误

### 错误 6：文档不存在（404 Not Found）

**错误码**：`404`

**错误信息**：
```json
{
  "code": 404,
  "msg": "document not found"
}
```

**症状**：
- API 调用返回 404
- 提示文档不存在

**原因分析**：
1. document_id 错误
2. 文档已被删除
3. 文档移动到了其他位置
4. URL 解析错误

**解决方案**：

```bash
# 1. 重新提取 document_id
# 正确格式：https://xxx.feishu.cn/docx/ABC123def
# document_id = ABC123def

# 错误示例：
URL="https://xxx.feishu.cn/docx/ABC123def?copy=open"
# 需要移除查询参数
DOC_ID=$(echo "$URL" | grep -oP 'docx/\K[^?]*')

# 2. 验证 document_id 格式
# document_id 应该是 16-24 位字母数字组合

# 3. 测试文档是否存在
curl -X GET "https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/plaintext" \
  -H "Authorization: Bearer {token}"
```

**验证方法**：
1. 在浏览器中打开文档 URL
2. 确认文档可以正常访问
3. 检查 document_id 是否正确

---

### 错误 7：块 ID 不存在

**错误码**：`404`

**错误信息**：
```json
{
  "code": 404,
  "msg": "block not found"
}
```

**症状**：
- 更新或删除块时失败
- 提示块不存在

**原因分析**：
1. block_id 错误
2. 块已被删除
3. 块 ID 在使用过程中发生了变化

**解决方案**：

```bash
# 1. 重新列出文档的所有块
curl -X GET "https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children" \
  -H "Authorization: Bearer {token}" | jq '.data.items[] | .block_id'

# 2. 使用正确的 block_id
# 从列表中找到目标块的 ID

# 3. 操作前先验证块是否存在
curl -X GET "https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{block_id}" \
  -H "Authorization: Bearer {token}"

# 4. 如果块不存在，更新块的列表
# 块可能会因为编辑操作而改变
```

---

## 请求格式错误

### 错误 8：请求体格式错误

**错误码**：`400`

**错误信息**：
```json
{
  "code": 400,
  "msg": "invalid request body"
}
```

**症状**：
- API 调用返回 400 错误
- 提示请求体格式无效

**原因分析**：
1. JSON 格式错误
2. 缺少必需字段
3. 字段类型错误
4. 字段值超出允许范围

**解决方案**：

```bash
# 1. 验证 JSON 格式
echo '{"test": "value"}' | jq .

# 2. 检查必需字段
# 创建块时必需：
# - block_type
# - text.elements[0].text_run.content

# 3. 使用 jq 格式化 JSON
curl -X POST "URL" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d @request.json | jq .

# 4. 完整示例
cat > request.json << EOF
{
  "children": [
    {
      "block_type": 2,
      "text": {
        "elements": [
          {
            "text_run": {
              "content": "测试内容"
            }
          }
        ]
      }
    }
  ]
}
EOF

curl -X POST "URL" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d @request.json
```

---

## 性能和限流错误

### 错误 9：请求过于频繁（Rate Limit）

**错误码**：`429`

**错误信息**：
```json
{
  "code": 429,
  "msg": "too many requests"
}
```

**症状**：
- 大量请求后开始返回 429
- 需要等待一段时间后才能继续

**原因分析**：
1. 请求频率超过 API 限流阈值
2. 短时间内发送了太多请求

**解决方案**：

```bash
# 1. 实现请求限流
# 使用 sleep 命令控制请求频率
for i in {1..100}; do
  curl -X POST "URL" ...
  sleep 0.1  # 每秒最多 10 个请求
done

# 2. 批量操作
# 一次请求创建多个块，而不是多次请求
curl -X POST "URL" \
  -d '{
    "children": [
      {"block_type": 2, "text": {...}},
      {"block_type": 2, "text": {...}},
      {"block_type": 2, "text": {...}}
    ]
  }'

# 3. 实现指数退避重试
MAX_RETRIES=3
RETRY_DELAY=1

for attempt in $(seq 1 $MAX_RETRIES); do
  RESPONSE=$(curl -s -X POST "URL" ...)
  CODE=$(echo "$RESPONSE" | jq -r '.code')
  
  if [ "$CODE" = "429" ]; then
    echo "Rate limited, retrying in $RETRY_DELAY seconds..."
    sleep $RETRY_DELAY
    RETRY_DELAY=$((RETRY_DELAY * 2))
  else
    break
  fi
done
```

---

## 调试技巧

### 技巧 1：启用详细日志

```bash
# 使用 curl 的 -v 参数查看详细请求
curl -v -X GET "https://open.feishu.cn/open-apis/docx/v1/documents/xxx/plaintext" \
  -H "Authorization: Bearer {token}"

# 输出包含：
# - 请求头
# - 响应头
# - 响应体
# - SSL 证书信息
```

---

### 技巧 2：使用 jq 解析响应

```bash
# 美化 JSON 输出
curl -s -X GET "URL" -H "Authorization: Bearer {token}" | jq .

# 提取特定字段
curl -s -X GET "URL" -H "Authorization: Bearer {token}" | jq -r '.code'
curl -s -X GET "URL" -H "Authorization: Bearer {token}" | jq -r '.data.content'

# 检查错误
curl -s -X GET "URL" -H "Authorization: Bearer {token}" | jq -r 'if .code == 0 then "Success" else "Error: \(.msg)" end'
```

---

### 技巧 3：测试脚本

```bash
#!/bin/bash

# 配置
APP_ID="cli_a1234567890"
APP_SECRET="abcdefghijklmnopqrstuvwxyz123456"
DOC_ID="ABC123def"

# 1. 获取 token
echo "获取 token..."
TOKEN_RESPONSE=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\": \"$APP_ID\", \"app_secret\": \"$APP_SECRET\"}")

TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.tenant_access_token')
CODE=$(echo "$TOKEN_RESPONSE" | jq -r '.code')

if [ "$CODE" != "0" ]; then
  echo "❌ 获取 token 失败"
  echo "$TOKEN_RESPONSE" | jq .
  exit 1
fi

echo "✅ Token: ${TOKEN:0:20}..."

# 2. 测试读取文档
echo "测试读取文档..."
READ_RESPONSE=$(curl -s -X GET "https://open.feishu.cn/open-apis/docx/v1/documents/$DOC_ID/plaintext" \
  -H "Authorization: Bearer $TOKEN")

CODE=$(echo "$READ_RESPONSE" | jq -r '.code')

if [ "$CODE" = "0" ]; then
  echo "✅ 读取成功"
  echo "$READ_RESPONSE" | jq -r '.data.content' | head -20
else
  echo "❌ 读取失败"
  echo "$READ_RESPONSE" | jq .
fi
```

---

### 技巧 4：错误日志记录

```bash
#!/bin/bash

# 日志函数
log_error() {
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  echo "[$timestamp] ERROR: $1" >> /tmp/feishu_api_errors.log
}

# 使用示例
curl -s -X POST "URL" -H "Authorization: Bearer {token}" -d '{"..."}' || {
  log_error "API 调用失败: URL"
  log_error "请求体: {...}"
  log_error "响应: $(curl -s ...)"
}
```

---

## 总结

### 快速诊断流程

```
遇到错误
    ↓
检查错误码
    ↓
├─ 认证错误（99991661, 99991663）
│   └─ 验证 token 是否正确获取
│
├─ 权限错误（403, 99991400）
│   └─ 检查应用权限和文档协作者
│
├─ 文档错误（404）
│   └─ 验证 document_id 和 block_id
│
├─ 请求错误（400）
│   └─ 验证 JSON 格式和必需字段
│
└─ 限流错误（429）
    └─ 实现请求限流和重试机制
```

### 最佳实践

1. **始终验证响应**
   ```bash
   RESPONSE=$(curl -s ...)
   if [ "$(echo "$RESPONSE" | jq -r '.code')" != "0" ]; then
     echo "API 调用失败"
     echo "$RESPONSE" | jq .
   fi
   ```

2. **实现自动重试**
   - 对于网络错误
   - 对于限流错误
   - 对于临时性错误

3. **记录详细日志**
   - 请求时间
   - 请求参数
   - 响应内容
   - 错误信息

4. **监控 API 使用**
   - 请求频率
   - 错误率
   - 响应时间

通过本指南，你应该能够快速定位和解决飞书文档 API 使用中的大部分问题！
