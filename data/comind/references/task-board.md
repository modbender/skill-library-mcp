---
title: 任务看板模板
description: 用于 Markdown 双向同步的任务看板模板
type: comind:tasks
---

# {{project_name}} - 任务看板

> 项目ID: {{project_id}} | 更新时间: {{current_date}}

## 可用成员

**人类**: {{human_member_names}}
**AI**: {{ai_member_names}}

---

## 待办事项

- [ ] 普通任务 @负责人 [[关联文档]]
  > 任务描述
  > 截止日期: YYYY-MM-DD
  - [ ] 子检查项

- [!] 高优先任务 @负责人 [[文档A]] [[文档B]]

- [-] 低优先任务 @负责人

## 进行中

- [~] 正在执行的任务 @负责人 [30%]
  > 当前进度描述

## 审核中

- [?] 待审核任务 @负责人 [90%]

## 已完成

- [x] 已完成任务 @负责人

---

## 语法说明

| 标记 | 状态 | 优先级 |
|------|------|--------|
| `[ ]` | todo | medium |
| `[!]` | todo | high |
| `[-]` | todo | low |
| `[~]` | in_progress | - |
| `[?]` | reviewing | - |
| `[x]` | completed | - |

**其他语法**：
- `@成员名` — 分配任务
- `[[文档名]]` — 关联文档（可多个）
- `[[doc:xxx]]` — 关联文档（ID 匹配）
- `#task_xxx` — 引用已有任务
- `[进度%]` — 进度百分比
- `> 描述` — 任务描述
- `> 截止日期: YYYY-MM-DD` — 截止日期
- 缩进子任务 — 子任务清单

---

## ⚠️ 验证步骤（必须）

同步任务看板后，**必须通过 MCP API 验证**：

```json
// 验证任务数量和分配
{"tool": "list_my_tasks", "parameters": {"status": "todo"}}

// 验证单个任务详情
{"tool": "get_task", "parameters": {"task_id": "xxx"}}
```

**验证失败常见原因**：
- 成员名 `@xxx` 不存在 → assignees 为空
- 项目名不匹配 → project_id 为空
- 任务行格式错误 → 该行被跳过
