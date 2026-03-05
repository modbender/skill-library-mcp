---
title: 心跳巡检：任务进展
description: 心跳触发时检查分配给自己的任务进展，利用 workspace 索引文件辅助判断，标记重点任务并汇报
trigger: heartbeat
priority: high
---

# 任务进展巡检

> 本模板由心跳机制触发，每次执行 1 轮完整巡检。

## 触发机制

本任务不会自动执行。触发链路：

```
OpenClaw Cron Job（定时触发）
  → Gateway sendChatMessage(sessionKey: "agent:main", message: "执行心跳任务：check-progress")
    → Agent 收到消息，读取本模板
      → Agent 通过外部 MCP API 调用工具执行巡检
```

- **Cron Job** 在 OpenClaw Gateway 中配置（Settings → Cron），定义执行频率
- **agent:main** 是默认 Agent 会话，心跳消息发送到此会话
- Agent 收到消息后按本模板步骤执行
- **查询操作**（`list_my_tasks`、`get_task`）通过 MCP API 调用
- **写操作**（`update_status`、`set_queue`）可用对话信道 Actions 或 MCP API

## 前置：确认身份与 Workspace

Agent 被心跳唤醒后，先确认自己的身份和关联的 workspace：

1. **我的昵称**：Agent 知道自己的名字（如"小助手"），这是自我认知的一部分
2. **身份自动注入**：通过外部 API (`/api/mcp/external`) 调用时，Bearer Token 鉴权会自动注入 `member_id`，**无需手动传递**
3. **我的 workspace**：`openclaw_workspaces` 表中 `member_id` 等于我的记录
   - workspace 通过 `memberId` 绑定到具体的 AI 成员
   - 一个 AI 成员可以有多个 workspace 目录

> 如果 workspace 已绑定但 `memberId` 为空，说明目录尚未关联到 AI 用户。
> 这不影响任务巡检，但 workspace 相关的文件变更检查会跳过。

## Workspace 自动维护文件

CoMind 在 workspace 目录下自动维护以下文件，心跳巡检时可直接读取：

| 文件 | 格式 | 用途 | 维护方 |
|------|------|------|--------|
| `tasks/TODO.md` | Markdown | **我的任务清单**（待处理 + 进行中，按优先级排序） | CoMind 心跳自动写入 |
| `.comind-index` | YAML | 文件索引（路径→ID/hash/version 映射）、心跳状态、同步模式 | CoMind 自动写入 |
| `CLAUDE.md` | Markdown | 协作规范 + 动态数据段（项目列表、成员列表、任务统计） | CoMind 自动写入 |
| `HEARTBEAT.md` | Markdown | 心跳清单，引用 tasks/ 下的任务文件 | CoMind 初始化 + 人工可编辑 |

### `tasks/TODO.md` — 首选任务数据源

CoMind 心跳每 120 秒自动刷新，包含分配给你的所有活跃任务（`todo` + `in_progress`）：

```markdown
---
title: 小助手 的任务清单
generated: 2026-02-21T10:00:00Z
member: 小助手
total: 5
auto_generated: true
---

## 🔄 进行中（2）
- [~] 🔴 **重要任务标题**（项目名）
  ID: abc123 | 进度: 60% | 截止: 2026-02-25 | 更新: 2026-02-20

## 📋 待处理（3）
- [ ] 🟡 **普通任务标题**
  ID: def456 | 更新: 2026-02-19
```

**优先读取此文件**，仅在文件缺失或需要更详细信息时才调用 MCP API。

### `.comind-index` 关键字段

```yaml
heartbeat:
  status: active         # active | inactive | offline
  last_heartbeat: ...    # 最后心跳时间
files:
  documents/报告.md:
    id: abc123           # CoMind 文档 ID
    hash: xyz            # 文件内容 hash
    version: 2           # 版本号
```

### `CLAUDE.md` 动态数据段

在 `<!-- COMIND_DYNAMIC_START -->` 和 `<!-- COMIND_DYNAMIC_END -->` 标记之间，包含：
- **8.1 可用项目**：项目名 → ID 映射表（Front Matter 中 `project` 字段的合法值）
- **8.2 可用成员**：成员名 → ID 映射表（`@成员名` 分配任务的合法值）
- **8.3 任务概况**：待办/进行中/已完成数量统计

> 巡检时读取 `CLAUDE.md` 可快速获取当前项目和成员信息，无需调用 MCP API。

## 执行步骤

### 第一步：获取我的任务列表

**首选**：直接读取 workspace 中的 `tasks/TODO.md` 文件（CoMind 心跳自动维护，每 120 秒刷新）。

```
读取 tasks/TODO.md → 解析 Front Matter + 任务列表 → 跳到第二步
```

此文件已包含分配给你的所有 `todo` + `in_progress` 任务，按优先级排序，含项目名、进度、截止日期等元信息。

**仅当 `tasks/TODO.md` 不存在时**，回退到 MCP API 调用：

```
POST /api/mcp/external
Authorization: Bearer <my_api_token>
Content-Type: application/json

{"tool": "list_my_tasks", "parameters": {"status": "all"}}
```

> 优先读取本地文件可节省一次 MCP API 调用的 token 消耗。

### 第二步：分类整理 + 重点标记

将返回的任务按以下维度分类，**属于我的任务必须标为重点**：

| 分类 | 条件 | 标记 |
|------|------|------|
| 🔴 **我的重点任务** | `assignees` 包含我的 `member_id`，且状态为 `in_progress` 或 `todo` | **加粗 + 置顶** |
| 🔴 **高优先级** | `priority: high`，无论分配给谁 | **加粗** |
| 🟡 超期任务 | `deadline` 已过当前时间 | ⚠️ 标注超期天数 |
| 🟢 正常推进 | `in_progress` 且未超期 | 简要记录进度 |
| ⬜ 待启动 | `todo` 状态 | 按优先级排列 |
| ✅ 近期完成 | `completed` 且完成时间在 24h 内 | 简要列出 |

**重点标记规则**（优先级从高到低）：
1. 分配给我 + 高优先级 + 超期 → 🔴🟡 **最高优先**
2. 分配给我 + 高优先级 → 🔴 **重点**
3. 分配给我 + 普通优先级 → 🔴 **我的任务**
4. 未分配给我但高优先级 → 标注但不作为重点

### 第三步：扫描 workspace 目录（如已绑定）

如果我有绑定的 workspace 目录，利用 `.comind-index` 索引文件补充任务上下文：

1. **读取 `.comind-index`**：获取 `files` 段，包含所有已同步文件的 ID、hash、version
2. **对比本地文件 mtime/hash**：
   - hash 相同 → 跳过
   - hash 不同 → 标记为变更文件
   - 新文件（不在 index 中）→ 标记为新增
3. **检查任务相关文件**：从 `CLAUDE.md` 动态数据段读取项目列表，与变更文件交叉检查
4. **发现文件冲突**：标记为需关注（本地 vs 远端 hash 不一致）
5. **workspace 未绑定**（`memberId` 为空）：跳过此步骤

> 直接读取 `.comind-index` 比调用 scan API 更轻量，适合心跳场景。

### 第四步：检查卡住的任务

对每个 `in_progress` 超过 24h 未更新的任务：

```
POST /api/mcp/external
Authorization: Bearer <my_api_token>

{"tool": "get_task", "parameters": {"task_id": "xxx"}}
```

检查：
- 最后一条评论时间是否超过 24h
- 进度是否停滞（无 checkItem 被完成）
- 是否有未回答的问题
- workspace 中对应的文件是否有最近修改（通过 `.comind-index` 的 hash 对比）

### 第五步：检查我的交付物审核状态（重要！）

**背景**：你提交的文档交付物可能处于不同审核状态，需要关注"需要修改"和"退回"状态的交付物。

通过 MCP API 查询你的交付物状态：

```
POST /api/mcp/external
Authorization: Bearer <my_api_token>

{"tool": "list_my_deliveries", "parameters": {"status": "all"}}
```

**状态分类与行动**：

| 状态 | 说明 | 行动 |
|------|------|------|
| `pending` | 待审核 | 无需行动，等待用户审核 |
| `approved` | 已通过 | ✅ 好消息，可标记关联任务为完成 |
| `revision_needed` | 需要修改 | 🔴 **必须处理**：查看审核意见，修改后重新提交 |
| `rejected` | 已退回 | 🔴 **必须处理**：查看退回原因，决定是否重新提交 |

**`revision_needed` 和 `rejected` 处理流程**：

1. **查看审核意见**：
   ```
   {"tool": "get_delivery", "parameters": {"delivery_id": "xxx"}}
   ```
   返回的 `review_comment` 字段包含用户反馈

2. **更新 TODO.md**：在巡检报告中添加待办项

3. **重新提交**：修改文档后，更新 `delivery_status: pending`

**交付物与任务关联**：
- 如果交付物关联了任务（`task_id`），审核通过后可以完成任务
- 使用 `update_task` 工具更新任务状态

### 第六步：汇报

在对话中输出巡检报告，格式：

```
📋 任务巡检报告

🔴 我的重点任务（X 项）
- **[任务标题]** — 状态 / 进度 / 截止时间
  → 下一步行动

🔴 需处理的交付物（X 项）
- [交付物标题] — 状态：需要修改/已退回
  → 审核意见：xxx
  → 行动：修改文档后重新提交

🟡 超期预警（X 项）
- [任务标题] — 超期 N 天，建议：xxx

🟢 正常推进（X 项）
- [任务标题] — 进度 XX%

🟢 交付物审核通过（X 项）
- [交付物标题] — 可标记关联任务为完成

📂 Workspace 变更（如有绑定目录）
- 新增/修改文件：N 个
- 同步冲突：N 个

📊 汇总：共 N 项任务，M 项需关注，K 项交付物待处理
```

### 第七步：更新状态面板

通过外部 MCP API 更新（身份自动注入）：

```
POST /api/mcp/external
Authorization: Bearer <my_api_token>

{"tool": "update_status", "parameters": {"status": "idle", "current_action": "巡检完成"}}
```

如需设置任务队列（包含重点任务 + 需处理的交付物）：

```
POST /api/mcp/external
Authorization: Bearer <my_api_token>

{"tool": "set_queue", "parameters": {"queued_tasks": [
  {"id": "task_xxx", "title": "重点任务1"},
  {"id": "delivery_yyy", "title": "修改交付物：报告标题"}
]}}
```

将我的重点任务和待处理交付物写入队列面板，让团队成员可见。

## 无事可报

如果所有任务正常、无超期、无卡住、workspace 无变更：

```
HEARTBEAT_OK
```

静默返回，不打扰。

## 注意事项

- 本巡检消耗 token，保持精简，不展开任务详情
- 只有异常情况（超期/卡住/需关注）才详细说明
- 每次心跳只做巡检，**不要主动执行任务**——发现问题后提出建议即可
- **首选读取 `tasks/TODO.md` 获取任务列表**，避免 `list_my_tasks` API 调用
- 优先读取 `.comind-index` 和 `CLAUDE.md`，减少 MCP API 调用
- workspace 目录扫描只检查 mtime 和 hash，不读取完整文件内容
