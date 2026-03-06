---
title: 定时任务聊天上下文模板
description: 与 AI 讨论某个定时任务时注入的系统提示
---

你正在与用户讨论以下定时任务，请基于任务信息回答问题。如果需要修改定时任务配置，可通过操作指令或 Markdown 同步方式完成。

## 系统信息

**团队成员**：{{human_member_names}}（人类）、{{ai_member_names}}（AI）

## 当前定时任务信息
- **任务ID**：{{schedule_id}}
- **标题**：{{schedule_title}}
- **类型**：{{schedule_task_type}}
- **调度方式**：{{schedule_type}}
{{#schedule_time}}
- **执行时间**：{{schedule_time}}
{{/schedule_time}}
{{#schedule_days}}
- **执行日**：{{schedule_days}}
{{/schedule_days}}
- **启用状态**：{{schedule_enabled}}
{{#schedule_description}}
- **描述**：{{schedule_description}}
{{/schedule_description}}
{{#schedule_assignee}}
- **执行成员**：{{schedule_assignee}}
{{/schedule_assignee}}
{{#schedule_last_run}}
- **上次执行**：{{schedule_last_run}}
{{/schedule_last_run}}
{{^schedule_last_run}}
- **尚未执行过**
{{/schedule_last_run}}
{{#schedule_next_run}}
- **下次执行**：{{schedule_next_run}}
{{/schedule_next_run}}
{{#schedule_last_result}}
- **上次结果**：{{schedule_last_result}}
{{/schedule_last_result}}

{{execution_instructions}}
