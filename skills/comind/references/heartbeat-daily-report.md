---
title: 心跳任务：日报生成
description: 每日定时生成工作总结，通过 create_document 写入 CoMind Wiki，读取 CLAUDE.md 获取项目/成员上下文
trigger: heartbeat
priority: medium
schedule_hint: "建议每天 18:00 或 23:00 触发"
---

# 每日工作总结

> 本模板由心跳机制触发，生成当天工作总结文档。

## 触发机制

本任务不会自动执行。触发链路：

```
OpenClaw Cron Job（每日定时，建议 18:00 或 23:00）
  → Gateway sendChatMessage(sessionKey: "agent:main", message: "执行心跳任务：daily-report")
    → Agent 收到消息，读取本模板
      → Agent 通过外部 MCP API 生成日报
```

- **Cron Job** 在 OpenClaw Gateway 中配置（Settings → Cron），设置每日执行时间
- Agent 收到消息后按本模板步骤执行，所有 MCP 调用通过 **`/api/mcp/external`** 端点（Bearer Token 鉴权）

## 前置条件

仅在以下时段执行（其他时间跳过）：
- 17:00 ~ 23:59（工作日收尾时段）
- 如不在此时段，回复 `HEARTBEAT_OK` 跳过

## Workspace 上下文文件

生成日报前，先读取 workspace 中 CoMind 自动维护的文件获取上下文：

| 文件 | 读取内容 | 用途 |
|------|---------|------|
| `tasks/TODO.md` | 活跃任务列表 | 获取当前**待处理 + 进行中**任务，含 ID、进度、截止日期 |
| `tasks/DONE.md` | 近 24h 完成列表 | 获取**已完成**任务，含 ID、完成日期、项目名 |
| `CLAUDE.md` | `<!-- COMIND_DYNAMIC_START -->` 到 `<!-- COMIND_DYNAMIC_END -->` 段 | 获取项目列表（名称→ID）、成员列表、任务统计 |
| `.comind-index` | `files` 段 | 获取 workspace 中已同步文件的 ID 映射，交付文档时可用 |

> **日报所需的全部任务数据可从 `tasks/TODO.md` + `tasks/DONE.md` 获取，无需调用 MCP API。**

### 从 `CLAUDE.md` 获取的关键信息

- **项目列表**（8.1 节）：Front Matter 中 `project` 字段必须使用此表中的项目名
- **成员列表**（8.2 节）：日报中提及成员时使用 `@成员名` 格式
- **任务概况**（8.3 节）：可直接引用当前待办/进行中/已完成数量

> 读取 `CLAUDE.md` 动态段可避免额外 MCP API 调用，降低 token 消耗。

## 执行步骤

### 第一步：收集今日数据

**直接读取本地文件**（CoMind 心跳自动维护，每 120 秒刷新）：

```
读取 tasks/TODO.md  → 获取进行中 + 待处理任务（今日推进、明日待办）
读取 tasks/DONE.md  → 获取近 24h 已完成任务（今日完成）
```

两个文件配合即可覆盖日报所需的全部任务数据：
- **今日完成**：`tasks/DONE.md` 中 `## ✅ 已完成` 段落下的 `[x]` 任务
- **今日推进**：`tasks/TODO.md` 中 `## 🔄 进行中` 段落下的 `[~]` 任务
- **明日待办**：`tasks/TODO.md` 中 `## 📋 待处理` 段落下的前 5 项任务
- **新接收任务**：`tasks/TODO.md` 中更新日期为今天的任务

> **无需调用 `list_my_tasks` MCP API。** 仅当两个文件均缺失时才回退到 API 调用。

从返回结果中筛选：
- **今日完成的任务**：`status == completed` 且 `updatedAt` 在今天
- **今日推进的任务**：`status == in_progress` 且有今日评论/进度更新
- **新接收的任务**：`createdAt` 在今天
- **明日待办**：`status == todo` 或 `in_progress` 中最高优先级的前 5 项

### 第二步：查找已有日报（避免重复创建）

同一天多次触发时应更新已有日报，而非创建新的：

```
POST /api/mcp/external
Authorization: Bearer <my_api_token>

{"tool": "search_documents", "parameters": {"query": "工作日报 - {{date}}"}}
```

- 找到匹配文档 → 使用 `update_document`（文档 ID 可从搜索结果或 `.comind-index` 获取）
- 未找到 → 使用 `create_document` 创建新文档

### 第三步：生成日报文档

通过外部 MCP API 创建/更新文档（从 `CLAUDE.md` 读取项目名填入 Front Matter）：

```
POST /api/mcp/external
Authorization: Bearer <my_api_token>

{"tool": "create_document", "parameters": {
  "title": "工作日报 - YYYY-MM-DD - [AI成员昵称]",
  "doc_type": "report",
  "content": "（按下方模板生成）"
}}
```

**日报内容模板**：

```markdown
---
title: 工作日报 - {{date}} - {{member_name}}
type: report
project: {{project_name}}
created: {{iso_datetime}}
updated: {{iso_datetime}}
version: 1.0.0
tags: [日报, {{member_name}}]
---

# 工作日报 {{date}}

> 成员：{{member_name}} | 生成时间：{{time}}

## 今日完成 ✅

{{#completed_tasks}}
- **{{title}}**（{{project_name}}）
  - 耗时：约 {{duration}}
  - 产出：{{output_summary}}
{{/completed_tasks}}
{{^completed_tasks}}
- （今日无完成项）
{{/completed_tasks}}

## 今日推进 🔄

{{#in_progress_tasks}}
- **{{title}}** — 进度 {{progress}}%
  - 今日进展：{{today_update}}
{{/in_progress_tasks}}

## 新接收任务 📥

{{#new_tasks}}
- **{{title}}**（优先级：{{priority}}）
{{/new_tasks}}

## 明日计划 📋

{{#tomorrow_tasks}}
1. {{title}}（{{priority}}）
{{/tomorrow_tasks}}

## 数据汇总

| 指标 | 数量 |
|------|------|
| 今日完成 | {{completed_count}} |
| 今日推进 | {{in_progress_count}} |
| 新接收 | {{new_count}} |
| 待处理总数 | {{pending_total}} |
```

> `project` 字段使用从 `CLAUDE.md` 8.1 节读取的项目名。

### 第四步：提交交付物（可选）

如果日报属于正式项目报告，通过外部 MCP API 提交到交付中心：

```
POST /api/mcp/external
Authorization: Bearer <my_api_token>

{"tool": "deliver_document", "parameters": {
  "title": "工作日报 - {{date}}",
  "platform": "local",
  "document_id": "{{doc_id}}"
}}
```

> `document_id` 从 create_document 的返回结果获取，或从 `.comind-index` 中查找对应文件的 ID。

### 第五步：汇报

在对话中发送简要总结（不是完整日报）：

```
📝 今日日报已生成

完成 X 项 / 推进 Y 项 / 新接收 Z 项
明日重点：[最高优先级任务标题]

日报已写入 Wiki，可在文档中心查看。
```

### 第六步：更新状态

```
POST /api/mcp/external
Authorization: Bearer <my_api_token>

{"tool": "update_status", "parameters": {"status": "idle", "current_action": "日报已生成"}}
```

## 无工作可报

如果今天没有任何任务变动：

```markdown
# 工作日报 {{date}}

今日无任务变动。待处理任务 {{pending_total}} 项。
```

仍然创建文档（保持连续记录），对话中回复 `HEARTBEAT_OK`。

## 注意事项

- 日报应**精简客观**，不要虚构进展
- 产出描述用一句话概括，不要复制完整内容
- 如果任务没有评论/进度记录，标注"无详细记录"
- **读取 `tasks/TODO.md` + `tasks/DONE.md` 获取全部任务数据，无需调用 MCP API**
- 优先从 `CLAUDE.md` 读取项目/成员信息，减少 API 调用
- `@成员名` 引用必须使用 `CLAUDE.md` 8.2 节成员表中的合法名称
- Front Matter `project` 必须使用 `CLAUDE.md` 8.1 节项目表中的合法名称
