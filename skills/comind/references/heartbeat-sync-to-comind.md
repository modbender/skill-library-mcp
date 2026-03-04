---
title: 心跳任务：状态同步
description: 定期将 Agent 当前工作状态、任务队列同步到 CoMind 状态面板，利用 .comind-index 索引检测文件变更
trigger: heartbeat
priority: low
schedule_hint: "建议每 5-10 分钟触发"
---

# 状态同步到 CoMind

> 本模板由心跳机制触发，将 Agent 实时状态同步至 CoMind 面板。

## 触发机制

本任务不会自动执行。触发链路：

```
OpenClaw Cron Job（建议每 5-10 分钟触发）
  → Gateway sendChatMessage(sessionKey: "agent:main", message: "执行心跳任务：sync-to-comind")
    → Agent 收到消息，读取本模板
      → Agent 通过外部 MCP API 同步状态
```

- **Cron Job** 在 OpenClaw Gateway 中配置（Settings → Cron），定义执行频率
- Agent 收到消息后按本模板步骤执行，所有 MCP 调用通过 **`/api/mcp/external`** 端点（Bearer Token 鉴权）

## 前置：Workspace 绑定关系

`openclaw_workspaces` 表通过 `memberId` 字段绑定 AI 成员：
- 一个 AI 成员可关联多个 workspace 目录
- workspace 的 `memberId` 标识"这个目录属于哪个 AI"
- Agent 通过外部 API 调用时，身份从 Bearer Token 自动注入，**无需手动传递 member_id**

**如果 `memberId` 为空**：该 workspace 尚未绑定到任何 AI 成员，跳过文件变更检查。

## Workspace 索引文件

CoMind 在 workspace 目录下自动维护以下文件，状态同步时**必须使用**：

| 文件 | 格式 | 关键内容 | 更新频率 |
|------|------|---------|---------|
| `tasks/TODO.md` | Markdown | **我的任务清单**（待处理 + 进行中，含 ID/进度/截止日期） | 心跳间隔（120s），有变更时写入 |
| `.comind-index` | YAML | 文件索引（路径→ID/hash/version）、心跳状态、同步模式 | 心跳间隔（120s） |
| `CLAUDE.md` | Markdown | 项目列表、成员列表、任务统计（动态段） | 每次同步后 |

### `.comind-index` 核心结构

```yaml
version: 1.0.0
workspace_id: ws_abc123

heartbeat:
  status: active              # active | inactive | offline
  last_heartbeat: 2026-02-18T10:00:00Z
  interval: 120

sync:
  mode: auto_sync             # auto_sync | offline | api | mcp
  last_sync: 2026-02-18T10:00:00Z

files:
  documents/报告.md:
    id: abc123                # CoMind 文档 ID（用于 update_document、deliver_document）
    hash: xyz                 # 文件内容 SHA-256 hash
    version: 2                # 版本号
```

> **重要**：`.comind-index` 中的 `files` 段是 workspace 文件到 CoMind 文档 ID 的映射表。
> 当需要通过 MCP API 更新文档时，从这里获取 `document_id`，无需调用 `search_documents`。

### `CLAUDE.md` 动态数据

在 `<!-- COMIND_DYNAMIC_START -->` 和 `<!-- COMIND_DYNAMIC_END -->` 标记之间：
- **8.1 可用项目**：项目名 → ID 映射
- **8.2 可用成员**：成员名 → ID 映射
- **8.3 任务概况**：整体任务统计

## 执行步骤

### 第一步：自我状态评估

检查当前状态：

| 状态 | 判断条件 |
|------|---------|
| `working` | 当前正在执行某个任务（有 `in_progress` 且最近 10 分钟有活动） |
| `idle` | 无正在执行的任务 |
| `waiting` | 有任务等待外部输入（用户审核、外部 API 等） |

### 第二步：获取我的任务快照

**首选**：直接读取 `tasks/TODO.md`（CoMind 心跳自动维护，每 120 秒刷新）：

```
读取 tasks/TODO.md → 解析 Front Matter（total 字段）+ 任务列表
```

从文件中提取：
- **当前执行中**：`## 🔄 进行中` 段落下的 `[~]` 任务（最多 1 项作为 `current_action`）
- **排队等待**：`## 📋 待处理` 段落下的任务，前 5 项
- 每个任务行包含 `ID: xxx`，可直接用于 `update_status` 的 `task_id` 参数

**仅当 `tasks/TODO.md` 不存在时**，回退到 MCP API 调用：

```
POST /api/mcp/external
Authorization: Bearer <my_api_token>
Content-Type: application/json

{"tool": "list_my_tasks", "parameters": {"status": "all", "limit": 20}}
```

> 外部 API 自动注入 `member_id`，无需手动传递。

从返回数据中提取：
- **当前执行中**：`in_progress` 状态的任务（最多 1 项作为 `current_action`）
- **排队等待**：`todo` 状态按优先级排序的前 5 项
- **等待审核**：`reviewing` 状态的任务

### 第三步：同步状态面板

通过外部 MCP API 更新（身份自动注入）：

```
POST /api/mcp/external
Authorization: Bearer <my_api_token>

{"tool": "update_status", "parameters": {
  "status": "{{computed_status}}",
  "current_action": "{{current_task_title}}",
  "task_id": "{{current_task_id}}",
  "progress": {{current_task_progress}}
}}
```

设置任务队列：

```
POST /api/mcp/external
Authorization: Bearer <my_api_token>

{"tool": "set_queue", "parameters": {
  "queued_tasks": [
    {"id": "xxx", "title": "待办任务1"},
    {"id": "yyy", "title": "待办任务2"}
  ]
}}
```

### 第四步：检查我的 workspace 目录变更

查找绑定到我（`memberId` = 我的 `member_id`）的所有 workspace 目录：

**对每个已绑定的 workspace**：

1. **读取 `.comind-index`** 的 `files` 段，获取已索引文件列表及其 hash
2. **扫描目录**中的 `.md` 文件，获取文件列表和 mtime
3. **对比 hash**：
   - hash 相同 → 跳过
   - hash 不同 → 标记为变更文件
   - 新文件（不在 `.comind-index` 中）→ 标记为新增
4. **有变更时**，通过外部 MCP API 更新文档（从 `.comind-index` 获取 `document_id`）：

```
POST /api/mcp/external
Authorization: Bearer <my_api_token>

{"tool": "update_document", "parameters": {
  "document_id": "abc123",
  "content": "（从本地文件读取的最新内容）"
}}
```

> 从 `.comind-index` 直接获取 `document_id`，比调用 `search_documents` 更快且更准确。

5. **冲突检测**：如果远端 version 与 `.comind-index` 中记录的 version 不匹配，标记冲突但不覆盖
6. **新文件**（不在 index 中）：通过 `create_document` 创建，CoMind 同步后会更新 `.comind-index`

**workspace 未绑定时**（`memberId` 为空）：跳过整个第四步。

### 第五步：检查并更新心跳时间

确保 CoMind 侧知道此 Agent 在线：

```
POST /api/mcp/external
Authorization: Bearer <my_api_token>

{"tool": "update_status", "parameters": {"status": "{{computed_status}}"}}
```

> 每次 `update_status` 调用都会刷新成员的 `last_heartbeat` 时间戳。

## 静默模式

本任务默认**静默执行**——除非发现以下异常才在对话中汇报：

| 异常情况 | 汇报内容 |
|---------|---------|
| workspace 同步冲突 | 🔄 发现文件冲突：xxx.md，本地 vs 远端 version 不一致 |
| workspace 未绑定 | ⚠️ workspace [名称] 未绑定 AI 成员，无法检测变更 |
| `.comind-index` 缺失 | ⚠️ workspace [名称] 缺少 `.comind-index` 索引文件，建议触发一次同步 |
| 状态与实际不符 | ⚠️ 任务 xxx 状态为 in_progress 但已超 48h 无更新 |
| 队列积压 | 📊 当前待办 N 项，建议优先处理：xxx |

无异常时回复：

```
HEARTBEAT_OK
```

## 注意事项

- 本任务是**最轻量**的心跳任务，尽量减少 API 调用
- 如果距上次同步不到 5 分钟且无变更，直接 `HEARTBEAT_OK`
- **首选读取 `tasks/TODO.md` 获取任务列表和任务 ID**，避免 `list_my_tasks` API 调用
- **优先读取 `.comind-index` 获取文件 hash 和 document_id**，避免调用 scan/search API
- workspace 目录扫描只检查文件 mtime，不读取文件内容（除非 hash 变化）
- 状态面板的 `set_queue` 最多放 5 项，避免信息过载
- 多个 workspace 时按优先级扫描：`isDefault: true` 的先扫
