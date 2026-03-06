# Agent Sync | 智能体协作系统

> Universal multi-agent collaboration methodology. Model-tiered cowork + document-driven sync + pattern evolution.
> 通用多智能体协作方法论。模型分层协作 + 文档驱动同步 + 模式自演化。

English | [中文](#中文版)

---

## English Version

### Design Philosophy

Different capability models collaborate like GitHub contributors:
- **Lead** (High-capability model): Architecture, decisions, task breakdown
- **Engineer** (Balanced model): Execution, coding, implementation
- **Maintainer** (Cost-effective model): Archiving, cleanup, weekly reports

Agents don't need real-time communication. **Documents are the collaboration protocol**:
- `TASK.md` = Issue Board
- `CHANGELOG.md` = Commit Log (with #tags + agent identity)
- `CONTEXT.md` = Wiki (decision records + key insights)
- `WEEKLY-REPORT.md` = Sprint Review + Pattern Discovery

### Core Mechanisms

**1. Document-Driven Sync**
Each agent updates TASK + CHANGELOG after work. Other agents read docs to know progress, no need to re-examine code.

**2. On-Demand Retrieval (QMD)**
Don't inject all docs. Use `qmd query` to retrieve relevant fragments by intent. 15k → 1.5k tokens.

**3. Self-Evolution**
#tags in CHANGELOG auto-aggregate in weekly reports. Operations repeated 3+ times enter "candidate skill pool", get formalized later.

**4. Three-Layer Archive**
| Layer | Content | Tokens |
|-------|---------|--------|
| Hot | llms.txt + TASK | ~500t |
| Warm | CHANGELOG + CONTEXT | ~2-3k |
| Cold | archive/ | On-demand |

### Platform Support

Works with any multi-agent system:
- ✅ **Claude Code** (native skill support via SKILL.md)
- ✅ **Cursor Agent Mode**
- ✅ **OpenAI Assistants API**
- ✅ **LangChain / CrewAI**
- ✅ **OpenClaw** (original design target)
- ✅ Manual API orchestration

### Quick Start

```bash
cd your-project
/path/to/agent-sync/scripts/init.sh "ProjectName"
```

For non-Claude Code platforms: manually copy templates from `templates/` and follow `docs/BEST-PRACTICES.md`.

### File Structure

```
agent-sync/
├── SKILL.md              # Claude Code skill definition
├── README.md             # This file
├── docs/
│   └── BEST-PRACTICES.md # Detailed guide (bilingual)
├── scripts/
│   └── init.sh           # Project initializer
├── templates/
│   ├── CHANGELOG.md      # Change log template
│   ├── CONTEXT.md        # Project context template
│   ├── llms.txt          # Machine-readable index
│   ├── TASK.md           # Task board template
│   └── WEEKLY-REPORT.md  # Weekly report + pattern discovery
└── archive/              # Cold storage
```

### What's New in v2

| | v1 | v2 |
|--|----|----|
| Model routing | Custom logic | Platform-native |
| Context | Full injection | QMD on-demand |
| Agent identity | `by Claw` | `by opus` |
| Classification | None | #tag system |
| Evolution | None | Weekly aggregation → candidate skills |
| Weekly report | None | Pattern discovery section |

### License

MIT © 2026 HH & OpenClaw Community

---

## 中文版

### 设计思路

不同能力的模型像 GitHub contributors 一样协作：
- **Lead**（高能力模型）：架构、决策、拆任务
- **Engineer**（均衡模型）：执行、写代码、实现方案
- **Maintainer**（性价比模型）：归档、清理、生成周报

智能体之间不需要实时通信。**文档就是协作协议**：
- `TASK.md` = Issue Board（任务看板）
- `CHANGELOG.md` = Commit Log（提交日志，带 #标签 + 智能体身份）
- `CONTEXT.md` = Wiki（决策记录 + 关键洞察）
- `WEEKLY-REPORT.md` = Sprint Review + 模式发现

### 核心机制

**1. 文档驱动同步**
每个智能体工作后更新 TASK + CHANGELOG。其他智能体读文档即知进度，无需重复查阅代码。

**2. 按需检索（QMD）**
不全量注入所有文档。用 `qmd query` 按意图检索相关片段。15k → 1.5k tokens。

**3. 自演化**
CHANGELOG 中的 #标签 在周报时自动聚合。重复 3+ 次的操作进入"候选技能池"，后续正式封装。

**4. 三层归档**
| 层级 | 内容 | Token |
|------|------|-------|
| 热 | llms.txt + TASK | ~500t |
| 温 | CHANGELOG + CONTEXT | ~2-3k |
| 冷 | archive/ | 按需检索 |

### 平台支持

适用于任何多智能体系统：
- ✅ **Claude Code**（通过 SKILL.md 原生支持）
- ✅ **Cursor Agent Mode**
- ✅ **OpenAI Assistants API**
- ✅ **LangChain / CrewAI**
- ✅ **OpenClaw**（最初设计目标）
- ✅ 手动 API 编排

### 快速开始

```bash
cd your-project
/path/to/agent-sync/scripts/init.sh "项目名"
```

非 Claude Code 平台：手动从 `templates/` 复制模板，参考 `docs/BEST-PRACTICES.md` 使用。

### v2 新增特性

| | v1 | v2 |
|--|----|----|
| 模型路由 | 自建逻辑 | 平台原生 |
| 上下文 | 全量注入 | QMD 按需检索 |
| 智能体身份 | `by Claw` | `by opus` |
| 分类 | 无 | #标签体系 |
| 演化 | 无 | 周报聚合 → 候选技能 |
| 周报 | 无 | 模式发现板块 |

### 开源协议

MIT © 2026 HH & OpenClaw 社区
