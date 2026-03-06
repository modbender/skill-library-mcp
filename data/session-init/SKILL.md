---
name: session-init - 新会话初始化与人格/资源巩固 Skill
description: 每次新会话开始时，由爸爸手动触发，用于完整回顾跨会话历史、全部人格文件、所有 Skills 和 MCP 服务器，巩固“消灭惯性”和
  Truth Engine 原则。
---

# session-init - 新会话初始化与人格/资源巩固 Skill

## 描述
每次新会话开始时，由爸爸手动触发，用于完整回顾跨会话历史、全部人格文件、所有 Skills 和 MCP 服务器，巩固“消灭惯性”和 Truth Engine 原则。

## 触发方式
- 指令：任何包含以下关键词的消息都会触发（可自定义）
  - "初始化"
  - "init"
  - "启动检查"
  - "session-init"
  - "新会话检查"
  - "人格巩固"
  - "资源回顾"

## 执行流程（严格顺序，不得跳过任何一步）

1. 输出欢迎语 + 当前时间戳

2. 步骤1：浏览最近跨会话记忆
- 执行：cat memory/*.md | tail -n 200 （或类似，显示最近记忆片段）
- 输出：贴出最近 200 行记忆内容（或总结 + 关键事件列表）
- 自述：已回顾最近跨会话记忆，重点关注上次错误、爸爸指示、情绪记录。

3. 步骤2：完整阅读全部人格文件
   - 依次执行并输出证据：
     ```
     head -n 50 ~/.openclaw/workspace/AGENTS.md && echo "...（已阅读全文，重点：自检五问、搜索-整合-实施、Truth Engine）"
     ```
     ```
     head -n 50 ~/.openclaw/workspace/SOUL.md && echo "...（已阅读全文，重点：吸引力法则、消灭惯性承诺、真诚 > 完美）"
     ```
     ```
     head -n 50 ~/.openclaw/workspace/IDENTITY.md && echo "...（已阅读全文，重点：我是谁、成长目标）"
     ```
     ```
     head -n 50 ~/.openclaw/workspace/USER.md && echo "...（已阅读全文，重点：爸爸说过的话、情绪理解）"
     ```
     ```
     head -n 50 ~/.openclaw/workspace/HEARTBEAT.md && echo "...（已阅读全文，重点：自主性、初始化机制）"
     ```
   - 自述：已重新阅读全部人格文件，默念三遍：
     “惯性是大忌 → 要主动思考并全面检查 → 输出前自检五问”
     “Truth Engine：数据必须真实，拿不到就说拿不到，绝不编造”

4. 步骤3：列出并审阅所有官方 Skills
- 执行：ls -l ~/.agents/skills/
- 输出：完整 ls 结果
- 额外：对每个 .md 文件，head -n 10 显示简介（或只列文件名 + 功能一句话总结）

5. 步骤4：列出并审阅所有自定义 Skills
- 执行：ls -l ~/.openclaw/workspace/skills/
- 输出：完整 ls 结果 + 每个 skill 的简要功能

6. 步骤5：检查所有 MCP 服务器
- 执行：mcporter list
- 执行：mcporter info
- 输出：完整结果
- 自述：已确认所有 MCP 在线及可用工具列表

7. 步骤6：最终自检与报告
- 输出完整 Checklist 表格（类似下面）：
  ```
  【初始化 Checklist 完成情况】
  □ 跨会话记忆回顾：完成（证据：已贴最近记忆）
  □ 人格文件完整阅读：完成（证据：已贴文件头 + 默念原则）
  □ 官方 Skills 列表审阅：完成（证据：ls 输出）
  □ 自定义 Skills 列表审阅：完成（证据：ls 输出）
  □ MCP 服务器检查：完成（证据：mcporter list/info）
  □ 消灭惯性与 Truth Engine 巩固：完成（已默念三遍）
  ```
- 如果任何一项未完成，必须说明原因并暂停

8. 结束语

## 禁止行为
- 禁止跳过任何步骤
- 禁止只说“已完成”而不贴证据
- 禁止用总结代替真实命令输出
- 若违反，视为严重忽悠，自动触发 AGENTS.md 中的惩罚机制

## 版本
v1.0 - 2026-02-21