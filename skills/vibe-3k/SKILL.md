---
name: vibe-3k
description: Vibe Coding 最佳实践指南（vibe-3k）。AI 辅助开发的全流程规范：项目启动、PLAN/ACT 分离、多 Agent 协作、故障恢复、安全验收。Use when: (1) starting a new AI-assisted development project, (2) setting up multi-agent collaboration, (3) debugging with AI agents, (4) reviewing/accepting AI-generated code, (5) creating project rule files (CLAUDE.md/AGENTS.md). Triggers: "vibe coding", "vibe code", "vibe-3k", "AI 开发", "agent 协作", "多 agent", "PLAN ACT", "项目规则文件", "新项目启动", "故障处理", "代码验收".
---

# Vibe Coding 最佳实践指南

> **vibe-3k** = Vibe Coding Best Practices v3.0（3K 行级全流程指南）

> 你是主厨，AI 是厨房团队。你设计菜单、品尝每道菜，但不亲自切每根胡萝卜。

## 10 条核心原则

1. **先想后 prompt** — 5 分钟思考省 5 小时迭代
2. **Plan ≠ Act** — 分离规划和执行，用不同模型/session
3. **Design Doc 是枢纽** — 压缩上下文，可审查，可交接
4. **小步提交** — 每个功能点一个 commit，Git 是安全网
5. **新功能新 session** — 上下文溢出是第一杀手
6. **循环修复就回退** — 3 次修不好 = 方案有问题
7. **安全不能 vibe** — Auth/支付/数据必须人工 review
8. **LOG.md 是续命药** — 记录进度，任何时候都能恢复
9. **多 Agent 分工明确** — PM 规划、Dev 执行、QA 审查
10. **验收有 checklist** — 自动化检查 + 人工确认

## 参考文档（按需加载）

| 文件 | 内容 | 何时读取 |
|------|------|---------|
| [references/01-quickstart.md](references/01-quickstart.md) | 核心概念 + 项目启动 + 规则文件 + 4 套项目模板 | 启动新项目时 |
| [references/02-single-agent.md](references/02-single-agent.md) | PLAN/ACT 分离 + Design Doc + Prompt 技巧 + 上下文管理 | 单人 AI 开发时 |
| [references/03-multi-agent.md](references/03-multi-agent.md) | 多 Agent 协作 + Git Worktree 并行 + Race Condition 防护 + 时间戳规范 | 多 Agent 协作时 |
| [references/04-emergency.md](references/04-emergency.md) | 故障分级 + 恢复 SOP + 灾难恢复 + >24h 长任务管理 | 出问题或长任务时 |
| [references/05-security-qa.md](references/05-security-qa.md) | 安全红线 + 验收 Checklist + 自动化验收脚本 | 安全审查/验收时 |
| [references/06-tools.md](references/06-tools.md) | 工具推荐（Claude Code / Kimi / Antigravity / OpenClaw） | 工具选型时 |

## 快速启动

### 启动前 5 分钟清单

在碰 AI 之前写下：
1. 解决什么问题？
2. 目标用户？
3. 核心功能（P0/P1/P2）
4. 技术栈约束
5. 什么叫「完成」？

### PLAN/ACT 分离（最重要）

- **PLAN 阶段**: 大上下文 thinking 模型（Gemini / OpenAI / Claude 最新旗舰）只分析、只规划 → 输出 Design Doc
- **ACT 阶段**: 新 session + 快速模型（各厂商轻量级模型）→ 读 Design Doc → 逐步实现
- 永远不要在同一个 session 里做 Plan 和 Act

### 故障快速参考

| 信号 | 动作 |
|------|------|
| 单个错误，信息清晰 | 粘贴完整 stack trace → AI 修 |
| 来回改同一文件 3+ 次 | 🛑 停！`git stash` → 换模型/策略 |
| 多处报错，越修越乱 | `git reset --hard <stable>` → 重新 Plan |
| AI 重复/遗忘/答非所问 | 关 session → LOG.md → 新 session 接力 |

### 安全红线

Auth、支付、数据库 Schema、用户数据、API Key — **绝不 vibe，必须人工逐行 review**。

## 实际案例

使用中的真实案例记录在 `memory/tasks/` 目录。每次完成 Vibe Coding 项目都会生成 task 记录，包含执行过程、踩坑和成果。

## 工具信息时效性

> ⚠️ 工具相关信息（Kimi Agent Swarm、Antigravity Kit 等）截至 2026-02，具体能力和 API 以官方文档为准。
