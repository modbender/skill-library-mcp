---
name: openclaw-notion-api
description: Notion API 用于创建和管理页面、数据库和块。包含正确的图片、文件上传功能
homepage: https://developers.notion.com
author: ionepub
metadata: {"clawdbot":{"emoji":"📝"}}
---

# openclaw-notion-api

使用 Notion API 创建/读取/更新页面、数据源（数据库）和块。

## Setup（设置）

1. 在 https://www.notion.so/profile/integrations/internal 创建内部集成
2. 复制 API 密钥（以 `ntn_` 或 `secret_` 开头）
3. 存储密钥：
```bash
mkdir -p ~/.config/notion
echo "ntn_your_key_here" > ~/.config/notion/api_key
```
4. 将目标页面/数据库与集成共享（点击 "..." → "Connect to" → 你的集成名称）

## API Basics（API 基础）

所有请求都需要：
```bash
NOTION_KEY=$(cat ~/.config/notion/api_key)
curl -X GET "https://api.notion.com/v1/..." \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json"
```

> **注意：** `Notion-Version` header 是必需的。本技能使用 `2025-09-03`（最新版本）。在此版本中，数据库在 API 中称为"数据源"。

## Common Operations（常用操作）

**搜索页面和数据源：**
```bash
curl -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"query": "page title"}'
```

**获取页面：**
```bash
curl "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03"
```

**获取页面内容（块）：**
```bash
curl "https://api.notion.com/v1/blocks/{page_id}/children" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03"
```

**在数据源中创建页面：**
```bash
curl -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "xxxxxx"},
    "properties": {
      "Name": {"title": [{"text": {"content": "New Item"}}]},
      "Status": {"select": {"name": "Todo"}}
    }
  }'
```

**查询数据源（数据库）：**
```bash
curl -X POST "https://api.notion.com/v1/data_sources/{data_source_id}/query" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {"property": "Status", "select": {"equals": "Active"}},
    "sorts": [{"property": "Date", "direction": "descending"}]
  }'
```

**创建数据源（数据库）：**
```bash
curl -X POST "https://api.notion.com/v1/data_sources" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"page_id": "xxx"},
    "title": [{"text": {"content": "My Database"}}],
    "properties": {
      "Name": {"title": {}},
      "Status": {"select": {"options": [{"name": "Todo"}, {"name": "Done"}]}},
      "Date": {"date": {}}
    }
  }'
```

**更新页面属性：**
```bash
curl -X PATCH "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"properties": {"Status": {"select": {"name": "Done"}}}}'
```

**向页面添加块：**
```bash
curl -X PATCH "https://api.notion.com/v1/blocks/{page_id}/children" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "children": [
      {"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Hello"}}]}}
    ]
  }'
```

## Property Types（属性类型）

数据库项的常用属性格式：
- **标题（Title）：** `{"title": [{"text": {"content": "..."}}]}`
- **富文本（Rich text）：** `{"rich_text": [{"text": {"content": "..."}}]}`
- **选择（Select）：** `{"select": {"name": "Option"}}`
- **多选（Multi-select）：** `{"multi_select": [{"name": "A"}, {"name": "B"}]}`
- **日期（Date）：** `{"date": {"start": "2024-01-15", "end": "2024-01-16"}}`
- **复选框（Checkbox）：** `{"checkbox": true}`
- **数字（Number）：** `{"number": 42}`
- **URL：** `{"url": "https://..."}`
- **邮箱（Email）：** `{"email": "a@b.com"}`
- **关联（Relation）：** `{"relation": [{"id": "page_id"}]}`

## Key Differences in 2025-09-03（2025-09-03 版本的关键差异）

- **数据库 → 数据源：** 使用 `/data_sources/` 端点进行查询和检索
- **双 ID：** 每个数据库现在同时拥有 `database_id` 和 `data_source_id`
  - 创建页面时使用 `database_id`（`parent: {"database_id": "..."}`）
  - 查询时使用 `data_source_id`（`POST /v1/data_sources/{id}/query`）
- **搜索结果：** 数据库以 `"object": "data_source"` 形式返回，并带有其 `data_source_id`
- **响应中的父级：** 页面显示 `parent.data_source_id` 以及 `parent.database_id`
- **查找 data_source_id：** 搜索数据库，或调用 `GET /v1/data_sources/{data_source_id}`

## File Upload（文件上传）

使用 Direct Upload 方法上传图片或文件到 Notion（文件大小不超过 20MB）。两者的步骤完全相同，仅在 Step 3 的块类型上有区别。

### Step 1: Create File Upload Object（创建文件上传对象）

创建上传对象以获取上传 URL：
```bash
curl --request POST \
  --url 'https://api.notion.com/v1/file_uploads' \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H 'Content-Type: application/json' \
  -H 'Notion-Version: 2025-09-03' \
  --data '{}'
```

响应包含：
- `id`：文件上传 ID（在步骤 3 中使用）
- `upload_url`：上传文件内容的 URL

### Step 2: Upload File Content（上传文件内容）

使用 multipart/form-data 上传实际的文件：
```bash
curl --request POST \
  --url 'https://api.notion.com/v1/file_uploads/{file_upload_id}/send' \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H 'Notion-Version: 2025-09-03' \
  -H 'Content-Type: multipart/form-data' \
  -F "file=@/path/to/file.png"
```

**重要：**
- 使用 `POST` 方法（不是 PUT）
- 包含 `Authorization` 和 `Notion-Version` headers
- 使用 `-F` 进行 multipart/form-data
- 文件大小必须 ≤ 20MB

### Step 3: Insert into Page（插入到页面）

将上传的文件作为块添加。根据文件类型选择不同的块类型：

**上传图片：**
```bash
curl --request PATCH \
  --url "https://api.notion.com/v1/blocks/{page_id}/children" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H 'Content-Type: application/json' \
  -H 'Notion-Version: 2025-09-03' \
  --data '{
    "children": [
      {
        "type": "image",
        "image": {
          "type": "file_upload",
          "file_upload": {
            "id": "{file_upload_id}"
          }
        }
      }
    ]
  }'
```

**上传文件：**
```bash
curl --request PATCH \
  --url "https://api.notion.com/v1/blocks/{page_id}/children" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H 'Content-Type: application/json' \
  -H 'Notion-Version: 2025-09-03' \
  --data '{
    "children": [
      {
        "type": "file",
        "file": {
          "type": "file_upload",
          "file_upload": {
            "id": "{file_upload_id}"
          }
        }
      }
    ]
  }'
```

**注意：** 不要在块定义中包含 `"object": "block"`。

### Common Errors（常见错误）

- **invalid_request_url**：检查是否使用了 `POST` 方法和正确的 URL 格式
- **unauthorized**：确保步骤 2 中存在 `Authorization` 和 `Notion-Version` headers
- **validation_error**：必须在附加（步骤 3）之前上传文件（步骤 2）

## Notes（注意事项）

- 页面/数据库 ID 是 UUID（带或不带连字符）
- API 无法设置数据库视图过滤器 — 这是 UI 专属功能
- 速率限制：平均约 3 请求/秒
- 创建数据源时使用 `is_inline: true` 以将其嵌入页面中
