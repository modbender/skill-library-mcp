# 飞书 OpenAPI 详细指南

## API 基础

### 认证
所有 API 调用需要 `tenant_access_token`。

获取 token：

```bash
curl -X POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal \
  -H "Content-Type: application/json" \
  -d '{"app_id": "your_app_id", "app_secret": "your_app_secret"}'
```

响应示例：

```json
{
  "code": 0,
  "tenant_access_token": "t-xxx",
  "expire": 7200
}
```

### 请求头
所有 API 请求必须包含：

```http
Authorization: Bearer {tenant_access_token}
Content-Type: application/json
```

---

## 核心接口详解

### 1. 创建块（写入内容）

**接口**：
```
POST /docx/v1/documents/{document_id}/blocks/{block_id}/children
```

**路径参数**：
- `document_id`: 文档 ID
- `block_id`: 父块 ID（通常是 document_id，即根节点）

**请求体**：

```json
{
  "children": [
    {
      "block_type": 2,
      "text": {
        "elements": [
              {
                "text_run": {
                  "content": "文本内容"
                }
              }
            ]
        }
    }
  ]
}
```

**响应示例**：

```json
{
  "code": 0,
  "data": {
    "children": [
      {
        "block_id": "doxcnxxx",
        "block_type": 2
      }
    ]
  }
}
```

**block_type 说明**：
- `1`: 页面块（Page）
- `2`: 文本块（Text）
- `3`: 标题 1/2/3（Heading 1/2/3）
- 更多类型参见飞书文档

---

### 2. 获取文档纯文本

**接口**：
```
GET /docx/v1/documents/{document_id}/plaintext
```

**响应示例**：

```json
{
  "code": 0,
  "data": {
    "content": "文档的纯文本内容"
  }
}
```

---

### 3. 列出所有块

**接口**：
```
GET /docx/v1/documents/{document_id}/blocks/{document_id}/children
```

**查询参数**：
- `page_size`: 每页数量（1-500，默认 100）
- `page_token`: 分页 token

**响应示例**：

```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "block_id": "doxcnxxx",
        "block_type": 2,
        "text": {
          "elements": [...]
        }
      }
    ],
    "page_token": "next_page_token",
    "has_more": true
  }
}
```

---

### 4. 更新块

**接口**：
```
PATCH /docx/v1/documents/{document_id}/blocks/{block_id}
```

**请求体**：

```json
{
  "text": {
    "elements": [
      {
        "text_run": {
          "content": "新的文本内容"
        }
      }
    ]
  }
}
```

---

### 5. 删除块

**接口**：
```
DELETE /docx/v1/documents/{document_id}/blocks/{block_id}
```

**响应示例**：

```json
{
  "code": 0,
  "msg": "success"
}
```

---

## 高级操作

### 创建带格式的文本

```json
{
  "children": [
    {
      "block_type": 2,
      "text": {
        "elements": [
              {
                "text_run": {
                  "content": "粗体文本",
                  "text_element_style": {
                    "bold": true
                  }
                }
              },
              {
                "text_run": {
                  "content": "斜体文本",
                  "text_element_style": {
                    "italic": true
                  }
                }
              }
            ]
        }
    }
  ]
}
```

### 创建标量

```json
{
  "children": [
    {
      "block_type": 3,  // Heading 1
      "heading1": {
        "elements": [
              {
                "text_run": {
                  "content": "标量 1"
                }
              }
            ]
        }
    }
  ]
}
```

### 创建列表

```json
{
  "children": [
    {
      "block_type": 19,  // Bulleted list
      "bulleted_list": {
        "elements": [
              {
                "text_run": {
                  "content": "列表项 1"
                }
              }
            ]
        }
    }
  ]
}
```

---

## 完整工作流程示例

### 工作流 1：创建新文档并写入内容

```bash
# 1. 获取 token
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id": "xxx", "app_secret": "xxx"}' | jq -r '.tenant_access_token')

# 2. 创建文档（使用其他 API 或手动创建）
# 假设 document_id = "ABC123"

# 3. 写入内容
curl -X POST "https://open.feishu.cn/open-apis/docx/v1/documents/ABC123/blocks/ABC123/children" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "children": [{
      "block_type": 2,
      "text": {
        "elements": [
              {
                "text_run": {
                  "content": "Hello World"
                }
              }
            ]
        }
      }
    }]
  }'
```

### 工作流 2：读取并修改文档

```bash
# 1. 获取块列表
curl -X GET "https://open.feishu.cn/open-apis/docx/v1/documents/ABC123/blocks/ABC123/children" \
  -H "Authorization: Bearer $TOKEN" | jq '.data.items[0].block_id'

# 2. 更新块内容
curl -X PATCH "https://open.feishu.cn/open-apis/docx/v1/documents/ABC123/blocks/BLOCK_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": {
      "elements": [
              {
                "text_run": {
                  "content": "更新的内容"
                }
              }
            ]
        }
      }
    }'
```

### 工作流 3：删除特定块

```bash
# 删除块
curl -X DELETE "https://open.feishu.cn/open-apis/docx/v1/documents/ABC123/blocks/BLOCK_ID" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 错误处理

### 错误码格式

飞书 API 返回的响应格式：

```json
{
  "code": 错误码,
  "msg": "错误信息"
}
```

### 常见错误码

| 错误码 | 含义 | 解决方案 |
|--------|------|---------|
| 0 | 成功 | - |
| 99991663 | 无效的 app_id | 检查应用配置 |
| 99991661 | 缺少 tenant_access_token | 确保请求头包含 token |
| 403 | 无权限 | 检查应用是否为文档协作者 |
| 404 | 文档不存在 | 检查 document_id 是否正确 |
| 500 | 内部错误 | 重试或联系支持 |

---

## 性能优化

### 批量操作

如果需要创建多个块，可以一次请求创建多个：

```json
{
  "children": [
    {
      "block_type": 2,
      "text": {
        "elements": [
              {
                "text_run": {
                  "content": "第一段"
                }
              }
            ]
        }
    },
    {
      "block_type": 2,
      "text": {
        "elements": [
              {
                "text_run": {
                  "content": "第二段"
                }
              }
            ]
        }
    }
  ]
}
```

### 分页读取

处理大文档时，使用分页：

```bash
PAGE_TOKEN=""

while true; do
  RESONSE=$(curl -s "https://open.feishu.cn/open-apis/docx/v1/documents/DOC_ID/blocks/DOC_ID/children?page_size=100&page_token=$PAGE_TOKEN" \
    -H "Authorization: Bearer $TOKEN")
  
  HAS_MORE=$(echo "$RESPONSE" | jq '.data.has_more')
  
  if [ "$HAS_MORE" = "false" ]; then
    break
  fi
  
  PAGE_TOKEN=$(echo "$RESPONSE" | jq -r '.data.page_token')
done
```

---

## 参考链接

- [飞书开放平台文档](https://open.feishu.cn/document)
- [文档 API 概述](https://open.feishu.cn/document/server-docs/docs/docx-v1/document/introduction)
- [块 API 参考](https://open.feishu.cn/document/server-docs/docs/docx-v1/document-block/create)
