---
name: dev-pipeline
description: 版本化开发流水线 —— 与 version-manager 和 project-manager 集成的完整开发流程
license: Proprietary
---

# Dev Pipeline - 版本化开发流水线

## 概述

与 version-manager 和 project-manager 深度集成，提供标准化的开发流程。

## 集成关系

```
dev-pipeline
    │
    ├── calls ──► version-manager
    │               - version-check
    │               - version-prepare
    │               - version-validate
    │               - version-archive
    │
    ├── calls ──► project-manager
    │               - project-update
    │               - project-changelog
    │
    └── calls ──► Claude Opus 4.6 (via oracle)
                    - analyze
                    - write
                    - review
                    - fix
```

## 工作流程

```
init → analyze → [pending_confirm] → confirm → write → review → (fix → review) → deploy → seal
  │                           ↑                                              │
  └──── version-prepare ──────┘                                              └──── version-archive
                                                            project-update
                                                            project-changelog
```

---

## 📋 命令规范

### init <version> [--from <base-version>]

初始化新版本开发任务。

```bash
# 自动检测最新版本作为基础
dev-pipeline init v1.3.5

# 指定基础版本
dev-pipeline init v1.3.5 --from v1.3.4
```

执行：
1. `version-check <project>` - 检查当前状态
2. `version-prepare <project> <base-version>` - 准备代码
3. `project-update <project> --version <version> --status "🟢 迭代中"` - 更新看板
4. 创建版本目录结构和文档

---

### analyze

执行架构分析。

```bash
dev-pipeline analyze
```

**功能**：
- 读取 REQUIREMENTS.md
- 调用 Claude Opus 4.6 生成 DEV_PLAN.md
- **状态: pending_confirm（等待用户确认）**

**Opus Prompt 规范**：
```
你是一个资深全栈架构师。请基于需求文档，生成详细的开发执行方案。

【输出格式要求】
必须按以下结构输出 Markdown：

# 项目开发方案

## 1. 需求理解
- 业务目标
- 核心业务流程
- 关键技术特性

## 2. 技术架构
- 整体架构图（ASCII）
- 技术选型表格
- 目录结构设计

## 3. 数据库设计
- 完整的 SQL 建表语句
- 索引设计
- 外键约束

## 4. API 接口设计
- 每个接口的 Method/Path
- Request/Response 格式（JSON Schema）
- 错误码定义

## 5. 任务清单（关键！必须可被解析）

### 阶段一：基础设施（P0）
| 任务ID | 任务名称 | 优先级 | 依赖 | 预估工时 | 输出文件 |
|--------|---------|--------|------|---------|----------|
| T001 | 项目初始化 | P0 | 无 | 2h | package.json, .gitignore |
| T002 | 数据库模块 | P0 | T001 | 3h | shared/db.js |

### 阶段二：xxx（P0）
...

## 6. 风险评估
- 技术风险表格
- 缓解措施

【要求】
1. 所有 SQL 语句必须完整可执行
2. API 设计必须包含完整的请求/响应示例
3. 任务清单必须包含具体的输出文件列表
4. 任务ID格式：T001, T002, ...
```

---

### confirm / revise

```bash
dev-pipeline confirm           # 确认方案，进入编码阶段
dev-pipeline revise "修改意见"  # 根据反馈重新分析
```

---

### write [--task-id <id>]

**编写代码 - 核心功能，必须严格规范返回格式。**

```bash
dev-pipeline write              # 写入当前任务
dev-pipeline write --task-id T001  # 写入指定任务
```

#### 🎯 Opus Prompt 规范（关键！）

```
你是一个专业的高级软件工程师。请基于开发计划，编写高质量的代码。

当前任务：[TASK_ID] [TASK_NAME]

## 📁 文件输出格式（必须严格遵守）

对于每个需要创建的文件，必须按以下格式输出：

### FILE: [相对路径]
**操作类型**: [create | overwrite | append]
**描述**: [该文件的用途说明]

```[语言]
[完整的文件代码内容]
```

---

### 示例输出：

### FILE: package.json
**操作类型**: create
**描述**: Node.js 项目配置文件

```json
{
  "name": "my-project",
  "version": "1.0.0",
  "dependencies": {
    "express": "^4.18.0"
  }
}
```

---

### FILE: src/server.js
**操作类型**: create
**描述**: Express 服务器入口

```javascript
const express = require('express');
const app = express();

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

---

## ⚠️ 格式规则

1. **每个文件必须以 `### FILE: 路径` 开头**
2. **操作类型必须明确**：
   - `create` - 新建文件（文件不存在）
   - `overwrite` - 覆盖文件（文件已存在，需要替换）
   - `append` - 追加内容（在文件末尾添加）
3. **代码块必须完整**：包含所有必要的导入、配置、实现
4. **路径使用相对路径**：相对于项目根目录
5. **不要省略任何文件**：任务要求的所有文件都必须输出

## 📋 任务要求

基于以下开发计划生成代码：
[DEV_PLAN.md 内容]

当前任务详情：
- 任务ID: [TASK_ID]
- 任务名称: [TASK_NAME]
- 输出文件: [FILE_LIST]
- 依赖任务: [DEPENDENCIES]

请生成完整可运行的代码。
```

#### 📥 解析逻辑

`write` 命令的解析器会：
1. 读取 Opus 返回的文本
2. 使用正则匹配 `### FILE: (.*)` 提取文件路径
3. 提取操作类型（create/overwrite/append）
4. 提取代码块内容（``` 之间的内容）
5. 根据操作类型写入文件：
   - `create`: 检查文件不存在，创建新文件
   - `overwrite`: 直接覆盖现有文件
   - `append`: 在文件末尾追加内容
6. 更新 `.state.json` 中的任务状态

---

### review

执行代码审查。

```bash
dev-pipeline review
```

#### 🎯 Opus Prompt 规范

```
你是一个严格的代码审查员。请对以下代码进行全面审查。

## 📋 审查报告格式（必须严格遵守）

```markdown
# 代码审查报告

## 基本信息
| 项目 | 内容 |
|------|------|
| 任务编号 | [TASK_ID] |
| 任务名称 | [TASK_NAME] |
| 审查日期 | [日期] |

## 审查发现

### 🔴 严重问题（必须修复）
1. **[问题类型]** [问题描述]
   - **位置**: [文件路径]:[行号]
   - **影响**: [影响描述]
   - **修复建议**: [具体建议]

### 🟡 警告（建议修复）
1. **[问题类型]** [问题描述]
   - **位置**: [文件路径]:[行号]
   - **建议**: [改进建议]

### 🟢 建议（可选优化）
1. **[问题类型]** [问题描述]
   - **建议**: [优化建议]

## 代码质量评分

| 维度 | 评分 | 说明 |
|------|------|------|
| 功能完整性 | [0-10] | |
| 代码规范 | [0-10] | |
| 安全性 | [0-10] | |
| 性能 | [0-10] | |
| 可维护性 | [0-10] | |
| **总分** | **[0-10]** | |

## 审查结论

[✅ 通过 / ❌ 不通过]

**原因**:
[详细说明]

**下一步行动**:
- 如果通过：进入下一阶段
- 如果不通过：执行 `dev-pipeline fix` 修复问题
```

## ⚠️ 评分规则

- 总分 >= 7.0：✅ 通过
- 总分 < 7.0 或有 🔴 严重问题：❌ 不通过

## 📁 审查文件列表

[列出需要审查的文件路径和内容]
```

#### 📥 解析逻辑

1. 提取评分表格，计算总分
2. 检查是否有 🔴 严重问题
3. 生成审查报告文件：`versions/vX.X.X/docs/REVIEW_TASK_[ID].md`
4. 更新任务状态：
   - 通过：`review_passed`
   - 不通过：`needs_fix`

---

### fix

修复代码问题。

```bash
dev-pipeline fix
```

#### 🎯 Opus Prompt 规范

```
你是一个专业的高级软件工程师。请根据审查报告修复代码问题。

## 审查报告
[REVIEW_TASK_XXX.md 内容]

## 📁 修复输出格式

与 `write` 命令相同，使用：

### FILE: [路径]
**操作类型**: [overwrite | append]
**修复说明**: [修复了什么问题]

```[语言]
[修复后的代码]
```

---

## ⚠️ 要求

1. 必须解决所有 🔴 严重问题
2. 尽可能解决 🟡 警告
3. 保留原有代码结构，只做必要修改
4. 每个修改都要有明确的修复说明
```

---

### deploy [--force]

部署到生产环境。

```bash
dev-pipeline deploy
```

执行：
1. `version-validate <project>` - 验证代码完整性
2. 红线检查（文件大小差异>20%停止）
3. 备份线上代码
4. 部署
5. `project-update <project> --status "🟢 已部署"`

---

### seal

封版归档。

```bash
dev-pipeline seal
```

执行：
1. `version-archive <project> <version>` - 归档全量代码
2. `project-update <project> --version <version> --status "🟢 已封版"` - 更新看板
3. `project-changelog <project> release --version <version>` - 标记发布
4. 更新 .state.json

---

## 📊 状态机

```json
{
  "version": "v1.3.5",
  "status": "writing",
  "current_task": "T001",
  "architecture_confirmed": true,
  "tasks": [...]
}
```

| 状态 | 说明 | 可执行命令 |
|------|------|-----------|
| `initialized` | 刚初始化 | analyze |
| `pending_confirm` | 分析完成，等待确认 | confirm, revise |
| `confirmed` | 已确认 | write |
| `writing` | 编码中 | - |
| `written` | 编码完成 | review |
| `review_passed` | 审查通过 | write(下一任务) / deploy |
| `needs_fix` | 需要修复 | fix |
| `all_done` | 所有任务完成 | deploy |
| `deployed` | 已部署 | seal |
| `sealed` | 已封版 | - |

---

## ⚙️ 配置

`.dev-pipeline/config.json`：

```json
{
  "project": {
    "name": "gemini-agent",
    "repo_path": "."
  },
  "oracle": {
    "model": "claude-opus-4-6",
    "engine": "op46"
  },
  "output": {
    "encoding": "utf-8",
    "lineEnding": "lf"
  }
}
```

---

## 🔒 安全规则

1. **init 时必须 version-prepare** - 确保代码来源正确
2. **deploy 时必须 version-validate** - 确保代码完整性
3. **seal 时必须 version-archive** - 确保全量归档
4. **所有状态变更必须通过 project-update** - 确保看板同步

---

## 🤖 Sub-agent 协作模式（推荐）

为解决 main session token 累积问题，dev-pipeline 支持通过 `sessions_spawn` 在子 agent 中执行，main session 仅作为调度者。

### 架构

```
Main Session (调度者)
    │ 发送任务上下文
    ▼
sessions_spawn --task "dev-pipeline analyze" \
               --agent-id skill-runner \
               --mode run
    │
    ▼
Skill Runner Agent (执行者)
    │ 执行 heavy-lifting 任务
    │ 调用 Claude Opus、读写文件
    │
    ▼
返回结构化结果
    │
    ▼
Main Session (接收摘要，决策下一步)
```

### 优势

- **Main session 上下文干净**：只接收结构化结果，不收代码原文
- **子 agent 即抛即用**：执行完即销毁，token 不累积
- **长时间保持高效**：避免 9w+ token 后的幻觉问题
- **并行潜力**：可同时启动多个子 agent 处理不同任务

### Main Session 调用示例

```bash
# 1. 初始化版本（轻量，可直接执行）
dev-pipeline init v1.3.5

# 2. 架构分析（重型任务，交给子 agent）
sessions_spawn \
  --task "cd /path/to/project && dev-pipeline analyze" \
  --agent-id skill-runner \
  --mode run \
  --run-timeout-seconds 350

# 子 agent 返回：
# {
#   "status": "pending_confirm",
#   "action": "analyze",
#   "summary": "架构分析完成，生成 DEV_PLAN.md，包含 12 个任务",
#   "details": { "tasks_count": 12, "file": "versions/v1.3.5/docs/DEV_PLAN.md" }
# }

# [用户确认方案]

# 3. 代码编写（重型任务，交给子 agent）
sessions_spawn \
  --task "cd /path/to/project && dev-pipeline confirm && dev-pipeline write" \
  --agent-id skill-runner \
  --mode run \
  --run-timeout-seconds 600

# 4. 代码审查（重型任务，交给子 agent）
sessions_spawn \
  --task "cd /path/to/project && dev-pipeline review" \
  --agent-id skill-runner \
  --mode run \
  --run-timeout-seconds 350

# 5. 部署（轻量，可直接执行）
dev-pipeline deploy

# 6. 封版（轻量，可直接执行）
dev-pipeline seal
```

### 子 agent 返回格式

子 agent 必须返回 JSON 格式的执行结果：

```json
{
  "status": "success|error|pending_confirm|review_passed|needs_fix",
  "action": "analyze|write|review|fix|deploy|seal",
  "summary": "中文执行摘要（不超过 1000 字）",
  "details": {
    "files_created": ["path/to/file1.js", "path/to/file2.js"],
    "files_modified": [],
    "review_score": 8.5,
    "critical_issues": 0,
    "output_preview": "关键输出片段（不超过 500 字符）"
  },
  "next_action": "需要 main session 决策的下一步",
  "logs": "/path/to/detailed.log"
}
```

### 任务分类建议

| 任务类型 | 推荐执行方式 | 原因 |
|---------|------------|------|
| init | Main session | 轻量，需要确认项目根目录 |
| analyze | **Sub-agent** | 调用 Opus，返回大量内容 |
| confirm | Main session | 只是状态变更 |
| write | **Sub-agent** | 调用 Opus，生成大量代码 |
| review | **Sub-agent** | 调用 Opus，分析大量代码 |
| fix | **Sub-agent** | 调用 Opus，修复代码 |
| deploy | Main session | 需要 SSH 权限，可能需确认 |
| seal | Main session | 轻量状态变更 |

### 配置 Sub-agent 环境

子 agent 需要预装：
- Python 3 + dev-pipeline CLI
- Node.js + npm（用于 Node 项目）
- 访问 project root 的权限
- Claude API 环境变量

### 进阶：Persistent Sub-agent

对于需要连续迭代的开发流程，可启动持久化子 agent：

```bash
# 启动持久化 skill-runner
sessions_spawn \
  --label "dev-helper-v1.3.5" \
  --agent-id skill-runner \
  --mode session

# 然后多次发送任务
sessions_send --label "dev-helper-v1.3.5" --message "执行 analyze"
sessions_send --label "dev-helper-v1.3.5" --message "执行 write"

# 完成后销毁
sessions_send --label "dev-helper-v1.3.5" --message "exit"
```

---

## 📝 完整开发流程示例

### 传统模式（Main session 执行）

```bash
dev-pipeline init v1.3.5
# ...
dev-pipeline analyze  # ← token 累积点
dev-pipeline confirm
dev-pipeline write    # ← token 累积点
dev-pipeline review   # ← token 累积点
dev-pipeline deploy
dev-pipeline seal
```

### Sub-agent 协作模式（推荐）

```bash
# 轻量任务：Main session
dev-pipeline init v1.3.5

# 重型任务：Sub-agent
sessions_spawn --task "dev-pipeline analyze" --agent-id skill-runner --mode run
# Main: 接收摘要，等待用户确认

sessions_spawn --task "dev-pipeline write" --agent-id skill-runner --mode run
# Main: 接收文件列表

sessions_spawn --task "dev-pipeline review" --agent-id skill-runner --mode run
# Main: 接收评分和审查结论

# 轻量任务：Main session
dev-pipeline deploy
dev-pipeline seal
```