# 知识节点 API

## 知识节点 CRUD

### 创建文件夹
```bash
curl -X POST "https://lxapi.lexiangla.com/cgi-bin/v1/kb/entries" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "data": {
      "type": "kb_entry",
      "attributes": {
        "entry_type": "directory",
        "name": "文件夹名称"
      },
      "relationships": {
        "space": {
          "data": {"type": "kb_space", "id": "space_id_here"}
        },
        "parent_entry": {
          "data": {"type": "kb_entry", "id": "parent_entry_id"}
        }
      }
    }
  }'
```
> **注意**：使用 JSON:API 规范格式，`space_id` 和 `parent_entry_id` 需要通过 `relationships` 指定

### 创建在线文档
```bash
curl -X POST "https://lxapi.lexiangla.com/cgi-bin/v1/kb/entries" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "data": {
      "type": "kb_entry",
      "attributes": {
        "entry_type": "page",
        "name": "文档标题"
      },
      "relationships": {
        "space": {
          "data": {"type": "kb_space", "id": "space_id_here"}
        },
        "parent_entry": {
          "data": {"type": "kb_entry", "id": "parent_entry_id"}
        }
      }
    }
  }'
```

### 上传文件（需先获取 state）
```bash
curl -X POST "https://lxapi.lexiangla.com/cgi-bin/v1/kb/entries?state={STATE}" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "data": {
      "type": "kb_entry",
      "attributes": {
        "entry_type": "file",
        "name": "文件名.pdf"
      },
      "relationships": {
        "space": {
          "data": {"type": "kb_space", "id": "space_id_here"}
        },
        "parent_entry": {
          "data": {"type": "kb_entry", "id": "parent_entry_id"}
        }
      }
    }
  }'
```
> 支持类型：video(视频), audio(音频), file(图片/文档等)

### 重命名知识节点
```bash
curl -X PUT "https://lxapi.lexiangla.com/cgi-bin/v1/kb/entries/{entry_id}/rename" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"name": "新名称"}'
```

### 重新上传文件
```bash
curl -X PUT "https://lxapi.lexiangla.com/cgi-bin/v1/kb/entries/{entry_id}/upload?state={STATE}" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID"
```

### 删除知识节点
```bash
curl -X DELETE "https://lxapi.lexiangla.com/cgi-bin/v1/kb/entries/{entry_id}" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID"
```
> **注意**：删除节点前必须保证其下没有子节点

### 获取知识列表
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/kb/entries?space_id={space_id}&parent_id={parent_id}&limit=20" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```

### 获取知识详情
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/kb/entries/{entry_id}" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```
> 对于文件类型，响应包含临时 `download` 下载链接（有效60分钟）

### 获取线上文档内容
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/kb/entries/{entry_id}/content?content_type=html" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```
| 参数 | 必须 | 说明 |
|------|------|------|
| content_type | 是 | 内容格式，可选值：html |

> 仅支持 page 类型，返回 HTML 格式内容

### 设置/移除/获取知识节点成员与权限

设置：
```bash
curl -X POST "https://lxapi.lexiangla.com/cgi-bin/v1/kb/entries/{entry_id}/subject?downgrade=0" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"data": [{"type": "staff", "id": "lisi", "role": "editor"}]}'
```

移除：
```bash
curl -X DELETE "https://lxapi.lexiangla.com/cgi-bin/v1/kb/entries/{entry_id}/subject" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"data": [{"type": "staff", "id": "lisi", "role": "editor"}]}'
```

设置继承：
```bash
curl -X PUT "https://lxapi.lexiangla.com/cgi-bin/v1/kb/entries/{entry_id}/inherit" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"member_inherit_type": "inherit"}'
```

获取：
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/kb/entries/{entry_id}/subject?limit=20" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```

## 知识反馈

### 获取反馈列表
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/kb/spaces/{space_id}/feedbacks?limit=20" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```
**反馈状态 status：** unprocessed / processing / processed / not_process
**反馈类型 type：** kb_content_incomplete / kb_content_mistake / kb_content_suggestion
