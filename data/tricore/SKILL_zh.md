---
name: tricore
version: "1.0.0"
description: TriCore 架构 - 为低资源服务器/Agent设计的确定性(Code-First)三层记忆与认知框架。包含底层的 memctl 引擎、系统策略约束(Linter)，以及全面重构的规划(Planning)、思考(ReAct)和进化(Self-Evolution)认知套件。
author: Berton Han
repository: https://github.com/bertonhan/tricore
allowed-tools:
  - default_api:exec
  - memory_search
  - memory_get
---

# 🤖 Agent Usage Guide (Read First)

**如果你是当前的 AI Agent，并且刚刚被要求加载、使用或分析此技能：**
1. 这是你的底层操作系统法则。你的记忆和状态已经被完全约束在 TriCore 架构下。你**严禁**随意在根目录创建类似于 `task_plan.md` 或 `findings.md` 的独立文本文件！
2. 你的记忆写操作必须且只能由命令行的 `python3 tools/memctl.py (capture/work_upsert/kb_append)` 代理。在阅读历史时，**必须**使用原生的语义检索工具 `memory_search` 获取碎片。
3. 请将此手册作为你的底层使用说明。如果被指示配置 Cron 或编写系统自动化脚本，写完命令后必须调用 `memctl.py lint` 测试方案合法性。

---

# TriCore 架构 (TriCore)

> **为真正的自主 Agent 打造的“存储与计算解耦”底层基础设施。**

传统的 Agent 技能常常带有自己的“记忆包袱”（如在项目根目录生成 `task_plan.md`、`reflection.md` 或大量散乱的学习笔记），导致上下文孤岛和存储混乱。

**TriCore** 抛弃了基于 LLM 随意读写文本的范式，转而采用 **Code-First（代码优先）** 的确定性状态机：
1. **统一引擎**: 所有记忆的增删改查必须通过 `tools/memctl.py` 路由。
2. **三层存储**:
   - **Brief (Layer 1)**: `MEMORY.md` (系统级微型档案，仅存指针与法则)
   - **Living (Layer 2)**: `memory/state/WORKING.md` (正在运行的任务流/生命周期追踪)
   - **Stable/Volatile (Layer 3)**: `memory/kb/*.md` (沉淀知识库) & `memory/daily/*.md` (临时日志)
3. **检索优先**: 禁止直接用 `read` 工具灌入巨大文件，必须使用语义检索 `memory_search` 获取代码片段，极大节省 Token 并保护低资源环境。
4. **硬性约束 (Linting)**: 具备原生的 `memctl.py lint` 机制，任何破坏架构的 Cron 或 Skill 变更都会被 Linter 拦截报错。
5. **系统兼容 (Compaction Hook)**: 安装时自动覆盖 OpenClaw 底层的 `pre-compaction memory flush` 提示词，防止在 Token 压缩时因尝试越权写文件导致 HTTP 429 请求爆发死循环。

---

## 📦 架构组件

本技能包包含了完整的系统组件：

1. **`tools/memctl.py`**: 核心引擎，包含 `ensure`, `capture`, `work_upsert`, `kb_append`, `lint` 等子命令。
2. **`install.sh`**: 一键安装脚本，自动初始化目录并注入 TriCore 合规策略到 `POLICY.md`。
3. **`cognitive-skills/`**: 三大基于 TriCore 重构的核心认知技能（作为模板供你的 Agent 加载）：
   - `planning-with-files.md`: 抛弃游离任务表的 PEP 规划系统。
   - `react-agent.md`: 基于 `WORKING.md` 落盘心智状态的 ReAct 循环。
   - `self-evolution.md`: 彻底剥离记忆管理，专注“代码级 CI/CD”的进化系统。

---

## 🧩 核心依赖与运行要求 (Dependencies & Requirements)

TriCore 作为一套底层的认知基座，其本身及内嵌的三大认知技能对宿主环境有以下依赖：

### 1. 必选核心依赖 (Hard Dependencies)
- **OpenClaw (v2026+)**: 必须支持原生的 `memory_search` 和 `memory_get` 工具（这是彻底废弃 read 读大文件的检索基础）。
- **Python 3.6+**: 宿主环境必须安装 Python 3（用于执行 `tools/memctl.py` 状态引擎）。
- **系统工具**: `bash`, `sed`, `grep`（用于 Linter 和 Hooks 的正则表达式解析）。

### 2. 认知技能推荐依赖 (Soft Dependencies)
如果你启用了 `cognitive-skills/self-evolution.md`（自我代码进化技能），你的 Agent 必须具备向外探索的触角，否则它只能在内部的死循环里“自我幻觉进化”。

- **🌟 `agent-browser` (强烈推荐)**: 
  - **作用**：让 Agent 能够真正阅读 GitHub 源码、API 官方文档、最新论文。
  - **安装**：你需要单独安装 OpenClaw 的 `agent-browser` 技能，它基于无头浏览器提供所见即所得的爬取与点击能力。
- **搜索工具 (`web_search` / `web_fetch`)**:
  - **作用**：作为浏览器的轻量级降级方案，用于快速获取公开网页的 Markdown 摘录。
- **运行时修改权限 (`default_api:exec` & `default_api:write`)**:
  - **作用**：进化技能的本质是“改代码”，如果你的 Agent 被运行在只读（ReadOnly）的沙盒中，进化将无法发生。

---

## 🚀 安装与初始化 (The 3-Step Setup)

在任何全新的 OpenClaw 环境中，执行以下命令即可部署 TriCore 架构：

```bash
# 赋予安装脚本权限并执行
bash ./install.sh
```

**`install.sh` 按照以下顺序执行：**

### Step 1: 核心引擎部署
1. 创建标准的 `memory/state/`, `memory/kb/`, `memory/daily/` 等目录。
2. 将 `tools/memctl.py` 引擎部署至当前环境。

### Step 2: 强制旧版 MEMORY 迁移 (Agent Action Required)
在低资源架构下，一个充斥着对话历史和日记的庞大 `MEMORY.md` 极其致命。
脚本会自动检测当前的 `MEMORY.md`：
- 如果发现它过于臃肿（> 1500 bytes），会将其重命名并**移动至 `memory/archive/legacy-MEMORY-<date>.md`**。
- 然后在根目录重建符合规范的**极简版 `MEMORY.md` 模板**。
- **Agent 注意：此时你需要主动使用 `read` 阅读 legacy 备份文件，并调用 `memctl.py` 重新分发这批遗产**（事实入 `kb/facts`，规则入 `kb/playbooks`，日志丢入 `daily`），**绝对禁止**将长文原样贴回新的 MEMORY.md！

### Step 3: 系统全局 Linter 阻断部署
脚本将在系统的 `POLICY.md` 中注入 `[CRITICAL: TriCore Compliance]` 最高优先级防线。此后 Agent 执行的所有涉及落盘、状态更新、自动任务的规划，必须全部通过 `memctl.py lint` 的正则检查，否则在终端红字拒绝。

---

## 📚 核心命令速查 (Cheat Sheet)

在 Agent 工具流或内部子脚本中，请严格使用以下 API 存取状态：

**1. 记录临时日志 / 会话流水 (Volatile)**
```bash
python3 tools/memctl.py capture "测试了一下 API 连通性，成功了。"
```

**2. 建立/更新任务追踪 (Living State)**
```bash
python3 tools/memctl.py work_upsert --task_id "T-API-01" --title "修复 API" --goal "联通接口" --done_when "返回 200"
```

**3. 沉淀知识与经验 (Stable KB)**
```bash
python3 tools/memctl.py kb_append facts "该 API 只接受 JSON 格式。"
python3 tools/memctl.py kb_append playbooks "遇到该模块报错时，先检查 Redis 是否启动。"
```

**4. 检查脚本/Cron命令是否合规 (Linter)**
```bash
python3 tools/memctl.py lint "试图执行的命令或要检查的 .md 文件路径"
# 正常通过: Exit Code 0 (LINT PASS)
# 非法写入: Exit Code 1 (LINT ERROR)
```

---

## 🔄 Cron 任务适配要求

如果你要在 OpenClaw 配置定时任务（Cron），**请注意**：
所有的自动分析、每日总结、学习抓取任务，在生成成果后，**只能通过 `memctl.py` 落盘**。

例如，创建一个合规的学习总结任务：
```bash
openclaw cron add --name "daily-learning" --cron "0 22 * * *" --message '请使用 agent-browser 学习 Agent 最新论文，并使用 python3 tools/memctl.py kb_append facts "提炼的事实..." 记录。严禁创建独立 md。'
```

---
*Built with ❤️ for OpenClaw / Berton Han*
