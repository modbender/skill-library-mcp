# 其他 API（任务、属性、日志、AI、素材、导出、SSO）

## 一、任务管理

### 查询成员任务列表
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/tasks?staff_id=zhangsan&type=reading&status=0&limit=20" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```
| 参数 | 必须 | 说明 |
|------|------|------|
| staff_id | 是 | 被查询者员工ID |
| type | 否 | reading(阅读任务), collaboration(协作任务) |
| status | 否 | 0:未完成, 2:已完成 |
| limit | 否 | 每页数量，默认20，最大100 |
| page_token | 否 | 分页令牌 |

### 查询任务详情
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/tasks/{task_id}" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```

### 查询任务成员列表
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/tasks/{task_id}/members?limit=20" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```

## 二、自定义属性管理

### 获取自定义属性列表
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/kb/properties?source_type=company&limit=20" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```
| 参数 | 说明 |
|------|------|
| source_type | company(公司属性), kb_space(知识库属性) |
| source_id | 当 source_type=kb_space 时必填 |

### 获取自定义属性详情
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/kb/properties/{property_id}" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```

### 编辑自定义属性
```bash
curl -X PUT "https://lxapi.lexiangla.com/cgi-bin/v1/kb/properties/{property_id}/schema" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "name": "属性名称",
    "description": "属性描述",
    "multiple": false,
    "options": [
      {"key": "opt1", "value": "选项1"},
      {"key": "opt2", "value": "选项2"}
    ]
  }'
```

### 获取/修改知识自定义属性
获取：
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/kb/entries/{entry_id}/properties/values" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```

修改：
```bash
curl -X PUT "https://lxapi.lexiangla.com/cgi-bin/v1/kb/entries/{entry_id}/properties/values" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"properties": [{"id": "property_id", "value": ["opt1"]}]}'
```

## 三、操作日志

### 获取知识操作日志列表
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/kb/operation-logs?log_type=kb&started_at=2025-01-01&ended_at=2025-12-31" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```
> 返回知识库内的文档操作（新建、添加权限等），包含操作人、IP、地理位置及具体操作内容

### 获取管理操作日志列表
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/kb/operation-logs?log_type=manager&started_at=2025-01-01&ended_at=2025-12-31" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```

## 四、AI 助手

### FAQ 列表
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/ai-faqs?limit=20&page=1" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```

### AI 搜索（需要 x-staff-id）
```bash
curl -X POST "https://lxapi.lexiangla.com/cgi-bin/v1/ai/search" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"query": "搜索关键词"}'
```

### AI 问答（需要 x-staff-id）
```bash
curl -X POST "https://lxapi.lexiangla.com/cgi-bin/v1/ai/qa" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"query": "问题内容", "research": false}'
```
> `research=true` 使用专业研究模式

### 知识解析
```bash
# 获取知识解析结果
curl "https://lxapi.lexiangla.com/cgi-bin/v1/kb/entries/{entry_id}/parsed-content" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"

# 获取知识解析切片（用于 Embedding，返回 jsonl 下载地址，有效期60分钟）
curl "https://lxapi.lexiangla.com/cgi-bin/v1/kb/entries/{entry_id}/chunked-content" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"

# 获取附件解析结果/切片
curl "https://lxapi.lexiangla.com/cgi-bin/v1/kb/files/{file_id}/parsed-content" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
curl "https://lxapi.lexiangla.com/cgi-bin/v1/kb/files/{file_id}/chunked-content" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```

## 五、素材管理（文件上传三步流程）

> **文档参考**: https://lexiang.tencent.com/wiki/api/12004.html

### 步骤一：获取上传凭证
```bash
curl -X POST "https://lxapi.lexiangla.com/cgi-bin/v1/kb/files/upload-params" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"name": "文件名.md", "media_type": "file"}'
```
| 参数 | 必须 | 说明 |
|------|------|------|
| name | 是 | 文件名（需带扩展名） |
| media_type | 是 | `file`(文件), `video`(视频), `audio`(音频) |

### 步骤二：上传文件到腾讯云 COS
```bash
curl -X PUT "https://{Bucket}.cos.{Region}.myqcloud.com/{key}" \
  -H "Authorization: {object.auth.Authorization}" \
  -H "x-cos-security-token: {object.auth.XCosSecurityToken}" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @/path/to/file
```

### 步骤三：使用 state 创建知识节点
```bash
curl -X POST "https://lxapi.lexiangla.com/cgi-bin/v1/kb/entries?state={state}&space_id={space_id}" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "data": {
      "type": "kb_entry",
      "attributes": {"entry_type": "file", "name": "文件名.md"},
      "relationships": {
        "parent_entry": {"data": {"type": "kb_entry", "id": "parent_entry_id"}}
      }
    }
  }'
```

> 建议使用 `scripts/upload_file.sh` 脚本完成完整的三步上传流程。

## 六、导出任务管理

### 查询任务
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/jobs/{job_id}" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```
> - 只能查询72小时内创建的任务
> - `download_url` 有效期约 5 小时
> - status: 0(等待中), 1(进行中), 2(已完成)

## 七、单点登录（SSO）

乐享知识库支持 OAuth 授权码模式的单点登录，分为 SP 发起和 IdP 发起两种流程。

**可信 IP**（用于判断请求是否合法）：`111.230.70.44`, `111.230.156.88`
