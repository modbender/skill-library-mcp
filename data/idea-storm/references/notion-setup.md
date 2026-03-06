# Notion 实验页面配置

## 前置条件

需要 Notion API Token 和目标数据库 ID。

### 获取 Token

1. 访问 https://www.notion.so/my-integrations
2. 创建新 integration，获取 Internal Integration Token
3. 将 token 存入环境变量或配置文件

### 数据库配置

在 Notion 中创建一个数据库，包含以下属性：

| 属性名 | 类型 | 说明 |
|--------|------|------|
| 标题 | Title | 实验名称 |
| 状态 | Select | 进行中 / 已完成 / 已放弃 |
| 验证模式 | Select | 图片对比 / 指标优化 / 功能验证 / 自定义 |
| 迭代次数 | Number | 当前迭代轮数 |
| 创建时间 | Date | 实验开始时间 |
| 标签 | Multi-select | 自定义分类标签 |

### API 调用模板

创建页面：
```bash
curl -X POST 'https://api.notion.com/v1/pages' \
  -H 'Authorization: Bearer $NOTION_TOKEN' \
  -H 'Content-Type: application/json' \
  -H 'Notion-Version: 2022-06-28' \
  -d '{
    "parent": { "database_id": "$DATABASE_ID" },
    "properties": {
      "标题": { "title": [{ "text": { "content": "实验标题" } }] },
      "状态": { "select": { "name": "进行中" } },
      "验证模式": { "select": { "name": "指标优化" } },
      "迭代次数": { "number": 0 },
      "创建时间": { "date": { "start": "2026-02-13" } }
    }
  }'
```

追加内容块：
```bash
curl -X PATCH 'https://api.notion.com/v1/blocks/$PAGE_ID/children' \
  -H 'Authorization: Bearer $NOTION_TOKEN' \
  -H 'Content-Type: application/json' \
  -H 'Notion-Version: 2022-06-28' \
  -d '{
    "children": [
      {
        "object": "block",
        "type": "heading_2",
        "heading_2": {
          "rich_text": [{ "text": { "content": "区块标题" } }]
        }
      },
      {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
          "rich_text": [{ "text": { "content": "内容" } }]
        }
      }
    ]
  }'
```

### 环境变量

```bash
export NOTION_TOKEN="secret_xxx"
export IDEA_LAB_DB_ID="数据库ID"
```

配置完成后，skill 会自动使用这些变量操作 Notion。
