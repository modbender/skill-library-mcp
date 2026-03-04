---
name: memU-lite
description: Lightweight structured memory system for OpenClaw - inspired by memU, zero external dependencies. Provides atomic memory storage with categories (preferences/knowledge/relationships/tasks/skills), tag-based indexing, and fast retrieval.
read_when:
  - Need to remember user preferences across sessions
  - Building long-term context about users or projects
  - Implementing structured knowledge management
  - Creating persistent agent memory without external dependencies
metadata: {"clawdbot":{"emoji":"🧠","tags":["memory","knowledge","organization"]}}
allowed-tools: Bash(memu-lite:*)
---

# memU-lite - 轻量级结构化记忆系统

> 灵感来自 memU，零外部依赖，纯 Markdown + OpenClaw 原生工具实现

## 核心理念

memU-lite 将 Agent 记忆分为三层：

```
┌─────────────────────────────────────────┐
│  Category Layer: MEMORY.md (概览索引)    │
├─────────────────────────────────────────┤
│  Item Layer: items/{category}/ (原子记忆) │
├─────────────────────────────────────────┤
│  Resource Layer: raw/ (原始记录)         │
└─────────────────────────────────────────┘
```

## 安装

### 方式一：ClawHub (推荐)

```bash
openclaw skills install memu-lite
```

### 方式二：手动安装

```bash
git clone https://github.com/yoo-unison/memu-lite.git
cp -r memu-lite/memory ~/.openclaw/workspace/
```

## 快速开始

### 1. 初始化记忆结构

```bash
# 使用提供的初始化脚本
./memu-lite/init.sh
```

或手动创建：

```bash
mkdir -p ~/.openclaw/workspace/memory/{raw,items/{preferences,knowledge,relationships,tasks,skills},indexes}
```

### 2. 创建第一条记忆

在 `items/preferences/` 下创建文件：

```markdown
## P-20260302-001 用户决策风格偏好

- **类型**: preference
- **来源**: 2026-03-02 对话
- **日期**: 2026-03-02
- **置信度**: high
- **标签**: #偏好 #决策风格
- **内容**: 
  用户要求独立评估，不盲目跟风，偏好轻量方案。
- **关联**: [[R-20260302-001]]
```

### 3. 更新 MEMORY.md 索引

编辑 `MEMORY.md` 添加记忆条目到索引表格。

## 记忆类型

| 类型 | 目录 | 前缀 | 用途 |
|------|------|------|------|
| `preference` | `items/preferences/` | P | 用户偏好、习惯、风格 |
| `knowledge` | `items/knowledge/` | K | 领域知识、事实信息 |
| `relationship` | `items/relationships/` | R | 人际关系、组织上下文 |
| `task` | `items/tasks/` | T | 待办事项、项目 |
| `skill` | `items/skills/` | S | 技能、方法、流程 |

## 记忆 ID 规则

格式：`<类型字母>-<日期>-<序号>`

示例：
- `P-20260302-001` (Preference, 2026-03-02, 第 1 条)
- `K-20260302-002` (Knowledge, 2026-03-02, 第 2 条)

## 记忆文件格式

```markdown
## [ID] 记忆标题

- **类型**: preference|knowledge|relationship|task|skill
- **来源**: 对话/文档链接
- **日期**: YYYY-MM-DD
- **置信度**: high|medium|low
- **标签**: #标签 1 #标签 2
- **内容**: 
  详细描述...

- **关联**: [[其他记忆 ID]]
- **状态**: active|archived|completed (仅 task 类型需要)
```

## 自动化工具（新增）

memU-lite 提供了一套自动化工具脚本，位于 `tools/` 目录：

### memu-add.sh - 交互式创建记忆

```bash
./tools/memu-add.sh
```

**功能：**
- 交互式输入记忆内容
- 自动选择记忆类型
- 自动生成 ID
- 自动更新 MEMORY.md 索引

**示例：**
```
🧠 memU-lite - 添加新记忆
==========================

选择记忆类型:
  1) preference  - 用户偏好、习惯
  2) knowledge   - 领域知识、事实
  ...

请输入类型编号 (1-5): 1
记忆标题: 用户决策风格偏好
内容摘要: 要求独立评估，不盲目跟风
来源 (如: 对话/文档/链接): 2026-03-02 对话
标签 (用空格分隔，如: #偏好 #AI): #偏好 #决策风格
关联记忆 ID (可选): 

✅ 记忆创建成功!
ID: P-20260302-001
文件: items/preferences/P-20260302-001-用户决策风格偏好.md
```

### memu-search.sh - 搜索记忆

```bash
# 按关键词搜索
./tools/memu-search.sh 偏好

# 按标签搜索
./tools/memu-search.sh -t "#AI"

# 按 ID 搜索
./tools/memu-search.sh -i P-20260302-001

# 列出所有记忆
./tools/memu-search.sh -l
```

### memu-backup.sh - 备份与恢复

```bash
# 创建备份
./tools/memu-backup.sh

# 列出所有备份
./tools/memu-backup.sh -l

# 恢复备份
./tools/memu-backup.sh -r memory-20260302-143022.tar.gz

# 清理 7 天前的备份
./tools/memu-backup.sh -c 7
```

### memu-tags.sh - 标签索引生成

```bash
./tools/memu-tags.sh
```

**功能：**
- 自动扫描所有记忆文件的标签
- 生成标签统计报告
- 更新 `indexes/tags.md`

### memu-clean.sh - 过期清理

```bash
# 扫描过期记忆
./tools/memu-clean.sh

# 归档过期记忆（推荐）
./tools/memu-clean.sh -a

# 查看已归档记忆
./tools/memu-clean.sh -l
```

**过期机制：**
在记忆模板中添加 `过期日期` 字段：
```markdown
- **过期日期**: 2026-03-31
```

到期后会被自动归档到 `archive/` 目录。

## 核心工作流

### 对话结束后自动记录

1. 提取关键信息（偏好/知识/任务等）
2. 创建原子记忆文件到对应 `items/<category>/`
3. 更新 `MEMORY.md` 索引

### 检索记忆

```bash
# 快速概览 - 查看 MEMORY.md
cat ~/.openclaw/workspace/memory/MEMORY.md

# 语义搜索 - 使用 OpenClaw memory_search 工具
memory_search "用户偏好"

# 精确读取 - 使用 OpenClaw memory_get 工具
memory_get --path ~/.openclaw/workspace/memory/items/preferences/P-20260302-001.md
```

### 每日收尾

- 汇总当日记忆到 `MEMORY.md` 时间线
- 更新标签索引 `indexes/tags.md`

## 目录结构

```
memory/
├── MEMORY.md                 # 顶层索引 + 快速概览
├── memu-lite-guide.md        # 使用指南
├── raw/                      # 原始对话记录
│   └── YYYY-MM-DD.md
├── items/                    # 原子化记忆单元
│   ├── TEMPLATE.md           # 记忆模板
│   ├── preferences/          # 用户偏好
│   ├── knowledge/            # 领域知识
│   ├── relationships/        # 人际关系
│   ├── tasks/                # 待办事项
│   └── skills/               # 技能方法
└── indexes/                  # 检索辅助
    ├── tags.md               # 标签索引
    └── timeline.md           # 时间线索引
```

## 最佳实践

### 1. 原子化

每条记忆只包含一个独立事实：

✅ 好：`P-20260302-001 决策风格偏好`
❌ 差：`P-20260302-001 所有用户信息`

### 2. 及时更新

对话结束后立即记录，避免遗忘关键细节。

### 3. 标签具体

使用具体标签便于后续检索：

✅ 好：`#项目 Alpha #技术栈 #后端`
❌ 差：`#知识 #信息`

### 4. 建立关联

相关记忆互相链接：

```markdown
- **关联**: [[K-20260302-001]], [[S-20260302-001]]
```

### 5. 定期维护

- 每周回顾：合并过期任务，更新状态
- 每月清理：归档旧记忆，提炼核心

## 与原始 memU 对比

| 特性 | memU | memU-lite |
|------|------|-----------|
| 自动提取 | ✅ AI 自动 | ⚠️ 需 AI 主动记录 |
| 主动预判 | ✅ 后台持续运行 | ❌ 被动响应 |
| 向量检索 | ✅ 语义搜索 | ⚠️ 依赖 memory_search |
| 外部依赖 | Postgres + API | ❌ 无 |
| 部署复杂度 | 中 | 低 |
| Token 优化 | 70%+ 压缩 | 依赖模型上下文 |

## 示例记忆

### 用户偏好 (Preference)

```markdown
## P-20260302-001 用户决策风格偏好

- **类型**: preference
- **来源**: 2026-03-02 对话
- **日期**: 2026-03-02
- **置信度**: high
- **标签**: #偏好 #决策风格 #AI 使用
- **内容**: 
  1. 要求独立评估 - 不盲目接受外部建议
  2. 借鉴思路而非照搬 - 适配自身情况
  3. 偏好轻量方案 - 无外部依赖
  4. 重视实用性 - 关注实际效果
- **关联**: [[R-20260302-001]]
```

### 领域知识 (Knowledge)

```markdown
## K-20260302-001 编程语言偏好

- **类型**: knowledge
- **来源**: 2026-03-02 对话
- **日期**: 2026-03-02
- **置信度**: high
- **标签**: #技术 #编程语言 #偏好
- **内容**: 
  用户主要使用 Python 和 JavaScript 进行开发。
  偏好简洁、可读性强的代码风格。
- **关联**: [[S-20260302-001]]
```

### 技能方法 (Skill)

```markdown
## S-20260302-001 代码审查清单

- **类型**: skill
- **来源**: 通用最佳实践
- **日期**: 2026-03-02
- **置信度**: high
- **标签**: #技能 #代码审查 #开发流程
- **内容**: 
  Step 1: 检查代码规范和风格
  Step 2: 验证功能逻辑正确性
  Step 3: 确认错误处理完善
  Step 4: 检查性能优化点
  Step 5: 确认测试覆盖关键路径
- **关联**: [[K-20260302-001]]
```

## 迁移路径

如果未来需要升级到完整 memU：

1. `items/` 目录结构可直接映射到 memU Item Layer
2. `MEMORY.md` 可作为初始知识库导入
3. 记忆 ID 和标签系统保持一致

## 脚本工具

### init.sh - 初始化记忆结构

```bash
#!/bin/bash
mkdir -p ~/.openclaw/workspace/memory/{raw,items/{preferences,knowledge,relationships,tasks,skills},indexes}
echo "memU-lite 记忆结构已创建"
```

### backup.sh - 备份记忆

```bash
#!/bin/bash
DATE=$(date +%Y%m%d-%H%M%S)
tar -czf ~/.openclaw/workspace/backups/memory-$DATE.tar.gz ~/.openclaw/workspace/memory/
echo "记忆备份完成：memory-$DATE.tar.gz"
```

## 常见问题

### Q: 记忆文件太多怎么办？

A: 定期归档旧记忆到 `archive/` 目录，保持 `items/` 精简。

### Q: 如何搜索特定标签的记忆？

A: 使用 `grep -r "#标签" ~/.openclaw/workspace/memory/items/`

### Q: 可以和现有 memory-core 共存吗？

A: 可以。memU-lite 使用相同的 `memory_search`/`memory_get` 工具，只是文件结构更规范。

## 许可证

Apache 2.0

## 项目地址

GitHub: https://github.com/yoo-unison/memu-lite

---

*Inspired by memU (https://github.com/NevaMind-AI/memU)*
