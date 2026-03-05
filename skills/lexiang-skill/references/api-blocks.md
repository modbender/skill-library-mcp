# 在线文档块接口 API

> **文档参考**: https://lexiang.tencent.com/wiki/api/15016.html

## 创建嵌套块

**接口地址**: `POST /cgi-bin/v1/kb/page/entries/{entry_id}/blocks/descendant`

**请求头**:
- `Authorization: Bearer {access_token}`
- `x-staff-id`: 成员账号（作为创建者）
- `Content-Type: application/json; charset=utf-8`

**核心参数说明**:
| 参数 | 类型 | 必须 | 说明 |
|------|------|------|------|
| parent_block_id | String | 否 | 父块 ID。**留空则插入到页面根节点** |
| index | Int | 否 | 插入位置索引（从 0 开始） |
| children | Array | 嵌套块必填 | 第一级子块的临时 ID 列表 |
| descendant | Array | 是 | 所有待创建块的数组 |

> **提示**：对于新建的空白文档，**不传 parent_block_id** 即可直接插入内容到页面根节点。

**descendant 数组对象结构**:
| 参数 | 说明 |
|------|------|
| block_id | 嵌套块模式必填，自定义临时 ID（字符串），用于建立父子关系 |
| block_type | 块类型（见下表） |
| children | 该块包含的子块临时 ID 列表 |
| [内容字段] | 根据 block_type 不同使用不同字段 |

**块类型**:
`p`(段落), `h1`-`h5`(标题), `code`(代码), `table`(表格), `table_cell`(表格单元格), `task`(任务), `callout`(高亮块), `toggle`(折叠块), `bulleted_list`(无序列表), `numbered_list`(有序列表), `divider`(分隔线), `column_list`(分栏), `column`(列), `mermaid`, `plantuml`

**不支持嵌套子块的类型**: `h1`-`h5`, `code`, `image`, `attachment`, `video`, `divider`, `mermaid`, `plantuml`

---

## 示例

### 简单段落
```bash
curl -X POST "https://lxapi.lexiangla.com/cgi-bin/v1/kb/page/entries/{entry_id}/blocks/descendant" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "descendant": [
      {
        "block_type": "p",
        "text": {
          "elements": [{"text_run": {"content": "这是一段普通文本"}}]
        }
      }
    ]
  }'
```

### 带样式的标题
```bash
{
  "block_type": "h2",
  "heading2": {
    "elements": [
      {"text_run": {"content": "普通文本"}},
      {"text_run": {"content": "加粗", "text_style": {"bold": true}}},
      {"text_run": {"content": "下划线", "text_style": {"underline": true}}}
    ]
  }
}
```

**text_style 支持的样式**: bold, italic, underline, strikethrough, code, color, background_color

### 任务块
```json
{
  "block_type": "task",
  "task": {
    "name": "完成 API 文档更新",
    "done": false,
    "due_at": {"date": "2025-12-31", "time": "18:00:00"},
    "assignees": [{"staff_uuid": "员工UUID"}]
  }
}
```

### 代码块
```json
{
  "block_type": "code",
  "code": {
    "language": "python",
    "content": "def hello():\n    print(\"Hello, World!\")"
  }
}
```

### 引用块（嵌套结构）
```json
{
  "children": ["quote-1"],
  "descendant": [
    {
      "block_id": "quote-1",
      "block_type": "quote",
      "children": ["quote-text-1"]
    },
    {
      "block_id": "quote-text-1",
      "block_type": "p",
      "text": {"elements": [{"text_run": {"content": "引用文本"}}]}
    }
  ]
}
```

### 高亮块 (Callout)
```json
{
  "children": ["callout-1"],
  "descendant": [
    {
      "block_id": "callout-1",
      "block_type": "callout",
      "callout": {"background_color": "#FFF3E0", "icon": "⚠️"},
      "children": ["callout-text-1"]
    },
    {
      "block_id": "callout-text-1",
      "block_type": "p",
      "text": {"elements": [{"text_run": {"content": "警告提示"}}]}
    }
  ]
}
```

### 无序列表
```json
{
  "block_type": "bulleted_list",
  "bulleted": {
    "elements": [{"text_run": {"content": "列表项内容"}}]
  }
}
```
> 注意：`block_type` 是 `bulleted_list`，但内容字段是 `bulleted`

### 有序列表
```json
{
  "block_type": "numbered_list",
  "numbered": {
    "elements": [{"text_run": {"content": "列表项内容"}}]
  }
}
```
> 注意：`block_type` 是 `numbered_list`，但内容字段是 `numbered`

### 表格（嵌套块典型用法）
```json
{
  "children": ["table-1"],
  "descendant": [
    {
      "block_id": "table-1",
      "block_type": "table",
      "table": {
        "row_size": 2,
        "column_size": 2,
        "column_width": [200, 200],
        "header_row": true,
        "header_column": false
      },
      "children": ["cell-1-1", "cell-1-2", "cell-2-1", "cell-2-2"]
    },
    {
      "block_id": "cell-1-1",
      "block_type": "table_cell",
      "table_cell": {"align": "center", "vertical_align": "middle"},
      "children": ["text-1-1"]
    },
    {
      "block_id": "text-1-1",
      "block_type": "p",
      "text": {"elements": [{"text_run": {"content": "表头", "text_style": {"bold": true}}}]}
    }
  ]
}
```

**table 参数**: row_size(行数), column_size(列数), column_width(各列宽度), header_row(是否有表头行), header_column(是否有表头列)
**table_cell 参数**: align(left/center/right), vertical_align(top/middle/bottom)

### 批量创建多个块
将多个块放在同一个 `descendant` 数组中，一次请求完成。

---

## 更新块内容
```bash
curl -X PUT "https://lxapi.lexiangla.com/cgi-bin/v1/kb/page/entries/{entry_id}/blocks/{block_id}" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"action": "update_text_elements", "text_elements": [{"type": "text", "text": "更新内容"}]}'
```

## 删除块
```bash
curl -X DELETE "https://lxapi.lexiangla.com/cgi-bin/v1/kb/page/entries/{entry_id}/blocks/{block_id}" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID"
```

## 获取块详情
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/kb/page/entries/{entry_id}/blocks/{block_id}" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```

## 获取子块列表
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/kb/page/entries/{entry_id}/blocks/children?parent_block_id={block_id}&with_descendants=0" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```

## 获取附件详情
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/kb/files/{file_id}" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```
> 响应包含 `links.download` 附件下载链接
