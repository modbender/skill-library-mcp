# 团队与知识库管理 API

## 一、团队管理

### 获取团队列表
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/kb/teams?limit=20&page_token=" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```

### 获取团队详情
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/kb/teams/{team_id}" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```

### 设置团队成员与权限
```bash
curl -X POST "https://lxapi.lexiangla.com/cgi-bin/v1/kb/teams/{team_id}/subject?downgrade=0" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "data": [
      {"type": "staff", "id": "lisi", "role": "manager"},
      {"type": "department", "id": "123", "role": "editor"}
    ]
  }'
```
| 参数 | 说明 |
|------|------|
| downgrade | 0:仅增加/不降级, 1:允许覆盖权限 |
| type | staff(成员) 或 department(部门) |
| role | manager(管理), editor(编辑), downloader(查看下载), viewer(仅查看) |

### 移除团队成员与权限
```bash
curl -X DELETE "https://lxapi.lexiangla.com/cgi-bin/v1/kb/teams/{team_id}/subject" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"data": [{"type": "staff", "id": "lisi", "role": "editor"}]}'
```

### 获取团队成员与权限
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/kb/teams/{team_id}/subject?limit=20" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```

## 二、知识库管理

### 创建知识库
```bash
curl -X POST "https://lxapi.lexiangla.com/cgi-bin/v1/kb/spaces" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "name": "技术文档库",
    "team": {
      "data": {"type": "team", "id": "team_id_here"}
    },
    "visible_type": 1,
    "subject": [
      {"type": "staff", "id": "lisi", "role": "editor"}
    ]
  }'
```
| 参数 | 必须 | 说明 |
|------|------|------|
| name | 是 | 知识库名称 |
| team.data.id | 是 | 所属团队ID |
| visible_type | 否 | 0:不可见, 1:可见, 2:跟随团队 |
| subject | 否 | 初始化权限设置 |

### 更新知识库
```bash
curl -X PUT "https://lxapi.lexiangla.com/cgi-bin/v1/kb/spaces/{space_id}" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"name": "新知识库名称"}'
```

### 删除知识库
```bash
curl -X DELETE "https://lxapi.lexiangla.com/cgi-bin/v1/kb/spaces/{space_id}" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID"
```

### 获取知识库列表
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/kb/spaces?team_id={team_id}&limit=20" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```

### 获取知识库详情
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/kb/spaces/{space_id}" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```

### 设置/移除/获取知识库成员与权限

设置：
```bash
curl -X POST "https://lxapi.lexiangla.com/cgi-bin/v1/kb/spaces/{space_id}/subject?downgrade=0" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "data": [
      {"type": "staff", "id": "lisi", "role": "editor"},
      {"type": "department", "id": "123", "role": "viewer"}
    ]
  }'
```

移除：
```bash
curl -X DELETE "https://lxapi.lexiangla.com/cgi-bin/v1/kb/spaces/{space_id}/subject" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"data": [{"type": "staff", "id": "lisi", "role": "editor"}]}'
```

获取：
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/kb/spaces/{space_id}/subject?limit=20" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```

## 权限角色说明

| 角色 | 说明 |
|------|------|
| manager | 管理权限 |
| editor | 编辑权限 |
| downloader | 查看/下载权限 |
| viewer | 仅查看权限 |
