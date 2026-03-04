---
name: lexiang
description: 腾讯乐享知识库 API 集成。提供团队、知识库、知识节点、在线文档块的完整 CRUD 操作，以及通讯录管理、AI 搜索/问答、文件上传、任务管理等功能。此 skill 适用于需要通过 API 管理乐享知识库内容（创建/查询/编辑文档、搜索知识、管理团队权限等）的场景。
homepage: https://lexiang.tencent.com/wiki/api/?event_type=link_exchange&event_channel=skill&event_detail=github
metadata: {"openclaw":{"emoji":"📚"}}
---

# 腾讯乐享知识库 API

腾讯乐享知识库是企业级知识管理平台，提供知识库、团队协作、文档管理、AI助手等功能。

## 数据模型

- **Team（团队）**：顶级组织单元，一个团队下可以有多个知识库（Space）
- **Space（知识库）**：知识的容器，属于某个团队，包含多个条目（Entry），有 `root_entry_id` 作为根节点
- **Entry（条目/知识）**：知识库中的内容单元，可以是页面（page）、文件夹（folder）或文件（file），支持树形结构（parent_id）
- **File（文件）**：附件类型的条目，如 PDF、Word、图片等

层级关系：`Team -> Space -> Entry（树形结构，root_entry_id 为根）`

## URL 规则

生成知识库链接时，必须使用企业专属域名（如 `csig.lexiangla.com`），**禁止使用** `https://lexiang.tencent.com/wiki/{id}` 格式。

| 资源类型 | URL 格式 |
|---------|----------|
| 团队首页 | `https://{domain}/t/{team_id}/spaces` |
| 知识库 | `https://{domain}/spaces/{space_id}` |
| 知识条目 | `https://{domain}/pages/{entry_id}` |

优先使用 API 响应中的 `links` 字段；如果 API 未返回完整链接，根据上述规则拼接。

## 凭证配置

### 环境变量
```bash
export LEXIANG_APP_KEY="your_app_key"
export LEXIANG_APP_SECRET="your_app_secret"
export LEXIANG_STAFF_ID="your_staff_id"  # 写操作必需
```

### 凭证配置优先级
1. 环境变量（最高优先级）
2. `~/.openclaw/openclaw.json` 中的 `skills.entries.lexiang.env` 字段
3. `~/.config/lexiang/credentials` JSON 文件

### 初始化（加载凭证 + 获取 Token）

执行 `scripts/init.sh` 脚本自动处理凭证加载和 Token 获取：
```bash
source scripts/init.sh
# 之后可使用 $LEXIANG_TOKEN 和 $LEXIANG_STAFF_ID
```

Token 有效期 2 小时，获取频率限制 20次/10分钟。脚本会自动缓存到 `~/.config/lexiang/token`。

## API 调用基础

### 请求头
```bash
# 读操作
-H "Authorization: Bearer $LEXIANG_TOKEN"
-H "Content-Type: application/json; charset=utf-8"

# 写操作（额外需要）
-H "x-staff-id: $LEXIANG_STAFF_ID"
```

### 需要 x-staff-id 的接口
所有写操作（创建/更新/删除）、AI 搜索/问答、权限设置

### 创建知识节点的格式
使用 **JSON:API 规范格式**，通过 `relationships` 指定所属知识库和父节点：
```json
{
  "data": {
    "type": "kb_entry",
    "attributes": {"entry_type": "page", "name": "标题"},
    "relationships": {
      "space": {"data": {"type": "kb_space", "id": "SPACE_ID"}},
      "parent_entry": {"data": {"type": "kb_entry", "id": "PARENT_ID"}}
    }
  }
}
```

### 通用限制
- 频率限制：大部分接口 3000次/分钟
- 权限要求：需在 AppKey 的授权范围内

## 核心工作流

### 1. 查询知识

```bash
# 获取团队列表
curl "https://lxapi.lexiangla.com/cgi-bin/v1/kb/teams?limit=20" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"

# 获取知识库列表
curl "https://lxapi.lexiangla.com/cgi-bin/v1/kb/spaces?team_id={team_id}&limit=20" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"

# 获取知识列表
curl "https://lxapi.lexiangla.com/cgi-bin/v1/kb/entries?space_id={space_id}&limit=20" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"

# 获取文档内容（HTML 格式）
curl "https://lxapi.lexiangla.com/cgi-bin/v1/kb/entries/{entry_id}/content?content_type=html" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```

### 2. 创建文档

两种方式对比：

| 方式 | 优点 | 推荐场景 |
|------|------|---------|
| **上传 Markdown 文件** | 简单高效、格式完整保留 | 批量创建文档、Markdown 内容发布 |
| **块接口 (page + blocks)** | 精确控制格式、可实时编辑 | 需要程序化编辑文档内容 |

**推荐方式：上传 Markdown 文件**

使用 `scripts/upload_file.sh` 脚本：
```bash
source scripts/init.sh
bash scripts/upload_file.sh ./document.md SPACE_ID [PARENT_ENTRY_ID]
```

### 3. AI 搜索与问答

```bash
# AI 搜索
curl -X POST "https://lxapi.lexiangla.com/cgi-bin/v1/ai/search" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"query": "搜索关键词"}'

# AI 问答（research=true 使用专业研究模式）
curl -X POST "https://lxapi.lexiangla.com/cgi-bin/v1/ai/qa" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "x-staff-id: $LEXIANG_STAFF_ID" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"query": "问题内容", "research": false}'
```

## 使用块接口的关键注意事项

对于需要使用在线文档块接口的场景，注意以下要点（详细示例见 `references/api-blocks.md`）：

1. **新建文档不传 parent_block_id**：直接插入内容到页面根节点
2. **列表块字段名不同于类型名**：`bulleted_list` 用 `bulleted` 字段，`numbered_list` 用 `numbered` 字段
3. **标题块字段需匹配**：`h1` 用 `heading1`，`h2` 用 `heading2`，不是 `text`
4. **嵌套块必须使用 children 和 block_id**：表格/引用/高亮块通过临时 ID 建立父子关系
5. **不支持嵌套的类型**：`h1`-`h5`、`code`、`image`、`attachment`、`video`、`divider`、`mermaid`、`plantuml`

## 常见错误排查

| 错误信息 | 原因 | 解决方案 |
|----------|------|---------|
| `必须指定员工账号` | 缺少 x-staff-id | 添加 `-H "x-staff-id: $LEXIANG_STAFF_ID"` |
| `data.attributes.entry_type 不能为空` | 请求格式错误 | 使用 JSON:API 规范格式 |
| `content_type 不能为空` | 缺少参数 | 添加 `?content_type=html` |
| 列表内容为空 | 字段名错误 | 无序列表用 `bulleted`，有序列表用 `numbered` |
| 嵌套块创建失败 | 缺少关联 | 确保 `children` + `block_id` 配对 |
| 上传接口 404 | 旧版路径 | 使用 `/v1/kb/files/upload-params` |

## 详细 API 参考

按需查阅以下参考文件获取完整的接口文档：

| 文件 | 内容 | 搜索关键词 |
|------|------|-----------|
| `references/api-contact.md` | 通讯录管理（成员/部门 CRUD） | contact, user, department, staff |
| `references/api-team-space.md` | 团队与知识库管理 | team, space, 权限, subject |
| `references/api-entries.md` | 知识节点 CRUD 与权限 | entry, entries, page, directory, file |
| `references/api-blocks.md` | 在线文档块接口（创建/编辑块内容） | block, descendant, paragraph, table, list |
| `references/api-other.md` | 任务/属性/日志/AI/素材/导出/SSO | task, property, log, ai, search, qa, upload, sso |

## HTTP 错误码

| 状态码 | 说明 |
|--------|------|
| 200/201 | 成功 |
| 204 | 删除成功 |
| 400 | 请求参数错误 |
| 401 | Token 无效或过期 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 429 | 超出频率限制 |
