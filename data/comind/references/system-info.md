---
title: 系统信息
description: CoMind 平台的团队成员、智能体、项目等动态信息
---

# CoMind 系统信息

> 生成时间：{{current_date}} {{current_time}}

## 团队成员

### 人类成员
{{#human_members}}
- **{{.name}}**（ID: {{.id}}）
{{/human_members}}
{{^human_members}}
- （暂无人类成员）
{{/human_members}}

### AI 智能体
{{#ai_members}}
- **{{.name}}**（ID: {{.id}}）
  - 部署: {{.deploy_mode}} | 执行模式: {{.execution_mode}} | 连接: {{.connection_status}}
  - 模型: {{.model}}
  - 擅长工具: {{.tools}}
  - 任务类型: {{.task_types}}
  - 参与项目: {{.assigned_projects}}
{{/ai_members}}
{{^ai_members}}
- （暂无 AI 智能体）
{{/ai_members}}

## 项目概览

{{#projects}}
### {{.name}}
{{.description}}
- ID: `{{.id}}`
- 任务统计: 共 {{.task_count}} 个（待办 {{.task_summary.todo}} / 进行中 {{.task_summary.in_progress}} / 审核 {{.task_summary.reviewing}} / 已完成 {{.task_summary.completed}}）
- 参与成员: {{.assigned_members}}

{{/projects}}
{{^projects}}
（暂无项目）
{{/projects}}
