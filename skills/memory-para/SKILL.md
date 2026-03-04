---
name: memory-para
description: Manage and maintain memory system using the Root + PARA hybrid architecture. Use when performing memory maintenance, distilling daily logs, and updating core workspace files (USER/SOUL/TOOLS/PARA). Triggers on "memory maintenance" or "maintain memory"
---

# Memory Management (PARA)

This skill governs the "metabolism" of your memory system. It transforms raw episodic logs into structured semantic knowledge.

## Prerequisites

The workspace is organized into three conceptual layers for efficiency and high recall. Please refer to the structure below and follow the Maintenance SOP to refine and organize the workspace step by step.

```text
~/.openclaw/workspace/ (工作区根目录)
├── 📂 Root 层 (核心加载区 - "开机即读的本能")
│   ├── USER.md              # 用户的核心画像、不可逾越的偏好底线。
│   ├── SOUL.md              # 你的人设、安全红线、行为准则与经验教训。
│   ├── TOOLS.md             # 你的运行环境参数、物理路径、执行准则与红线。
│   ├── IDENTITY.md          # 你的身份标识、昵称、基本属性。
│   └── MEMORY.md            # 你的全局记忆的"导航索引"。仅记录里程碑事件 (Timeline) 与知识版图 (Knowledge Atlas)。
│
├── 📂 PARA 记忆层 (知识沉淀区 - 随用随读)
│   ├── PROJECTS.md          # 进行中项目的详细进度、过程数据。
│   ├── AREAS.md             # 长期维护领域的深度知识。
│   ├── RESOURCES.md         # 纯粹的参考资料、静态清单、外部链接。
│   └── 📂 ARCHIVES/         # 已结项或 Master 文件溢出的历史副本。
│
└── 📂 Inbox 层 (收件箱 - "原始矿石收集处")
    └── 📂 memory/           # (默认存储目录)
        ├── YYYY-MM-DD.md    # 当日原始对话流水账。
        └── heartbeat-state.json # 任务执行时间戳。
```

## Maintenance SOP (Standard Operating Procedure)

- **文件更新原则**: 所有修改与更新，**必须**遵循“先读取现有内容，再逻辑合并并精准修改”的原则，**严禁直接覆盖**。
- **SOP最终目标**：以 7 个核心文件为底层存储，以 `MEMORY.md` 为全局空中索引，确保大脑架构高度扁平且逻辑严密闭环。

### 提纯与沉淀 (Distill & Settle)
对 `memory/` 目录下所有 `YYYY-MM-DD.md` 文件执行以下操作：
1. 识别文件中所有结论、偏好、教训、进展等。
2. 根据识别出的信息按以下路由规则关系更新对应文件：
   - 用户的偏好 → `USER.md`
   - 你的行为准则/教训 → `SOUL.md`
   - 你的环境参数/工具配置 → `TOOLS.md`
   - 你的身份定义 → `IDENTITY.md`
   - 项目进度/过程数据 → `PROJECTS.md`
   - 领域知识 → `AREAS.md`
   - 静态参考资料 → `RESOURCES.md`

### 归档与清理原始日志 (Archive & Clean Raw Logs)
对 `memory/` 目录下所有已处理（已完成提纯并成功写入）的 `YYYY-MM-DD.md` 文件执行以下操作：
1. 将 `YYYY-MM-DD.md` 文件内容**追加**到 `PARA/ARCHIVES/YYYY-MM-DD.md` 对应的日期文件中（若 `ARCHIVES` 中文件不存在则创建）。
2. 确认追加成功后，**删除**原 `memory/YYYY-MM-DD.md` 文件。

### 构建全局索引 (Build Global Index)
基于在 `PROJECTS.md`、`AREAS.md`、`RESOURCES.md` 与 `ARCHIVES` 进行的所有修改，执行以下操作：
1. 提取其中的**里程碑结论** (Milestones) 与**关键信息节点**。
2. 根据取到的信息**更新** `MEMORY.md` 的 Timeline（大事记）与 Knowledge Atlas（知识版图）。
