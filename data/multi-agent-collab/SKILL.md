---
name: agent-sync
description: Universal multi-agent collaboration methodology for Claude Code. Model-tiered cowork + document-driven sync + self-evolution.
author: HH & OpenClaw Community
version: 2.0.0
---

# Agent Sync Skill | 智能体协作技能

> **For Claude Code** | 适用于 Claude Code
>
> **Note**: This methodology works with any multi-agent system (Cursor, LangChain, OpenAI Assistants, OpenClaw, etc.). This file is the Claude Code skill wrapper. See [README.md](README.md) for platform-agnostic usage.
>
> **说明**：本方法论适用于任何多智能体系统（Cursor、LangChain、OpenAI Assistants、OpenClaw 等）。本文件是 Claude Code 技能封装。通用用法见 [README.md](README.md)。

---

## Core Mechanisms | 核心机制

1. **Model-Tiered Cowork | 模型分层协作**: Expensive thinks, cheap executes, cheapest archives
   贵的想，便宜的干，更便宜的归档
2. **Document-Driven Sync | 文档驱动同步**: TASK / CHANGELOG / CONTEXT = collaboration protocol
   TASK / CHANGELOG / CONTEXT = 协作协议
3. **On-Demand Retrieval | 按需检索**: QMD indexing, no full injection
   QMD 索引，不全量注入
4. **Self-Evolution | 自演化**: Repeated patterns → candidate skills
   重复模式 → 候选技能

## Quick Start | 快速开始

```bash
# Initialize project | 初始化项目
./scripts/init.sh <project-name>

# Index documents (requires qmd) | 索引文档（需要 qmd）
qmd index .
```

## Agent Workflow | 智能体工作流

### Before Work | 开始前
```
1. qmd query "project X current tasks" → get relevant fragments
   qmd query "项目 X 当前任务" → 获取相关片段
2. Or read TASK.md directly (enough for small projects)
   或直接读 TASK.md（小项目够用）
```

### After Work | 工作后
```
1. Update TASK.md (done → move to recent completed)
   更新 TASK.md（完成 → 移到最近完成）
2. Append CHANGELOG entry (one line, with #tag + identity)
   追加 CHANGELOG 条目（一行，带 #标签 + 身份）
3. Major decisions → update CONTEXT.md
   重大决策 → 更新 CONTEXT.md
```

### Weekly Report | 周报时
```
1. Aggregate CHANGELOG by #tags
   按 #标签 聚合 CHANGELOG
2. Fill "Pattern Discovery" section
   填充"模式发现"板块
3. Operations 3+ times → mark as candidate skill
   出现 3+ 次的操作 → 标记为候选技能
4. Archive old data to archive/
   归档旧数据到 archive/
```

## Model Roles | 模型分工

| Role | Model Examples | Responsibilities |
|------|----------------|------------------|
| Lead | Opus / GPT-4 / High-capability | Architecture, decisions, task breakdown<br/>架构、决策、拆任务 |
| Engineer | Sonnet / GPT-4o-mini / Balanced | Execution, coding, review<br/>执行、写代码、review |
| Maintainer | Flash / GPT-3.5 / Cost-effective | Archive, cleanup, weekly aggregation<br/>归档、清理、周报聚合 |

**Note**: Model names are examples. Use equivalent models from your platform.
**说明**：模型名称仅为示例。请使用你平台上的同等能力模型。
