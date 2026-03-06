---
name: Coding Team Setup v2.1 — Flexible Multi-Agent Development Team
description: "The wizard guides you through: 1. Team naming — Give your team a
  name (supports multi-team setup) 2. Select roles — Choose 2–10 from 10 preset
  roles or add custom ones 3. Assign models — Auto-detec..."
---

# Coding Team Setup v2.1 — Flexible Multi-Agent Development Team

## English

> Flexible setup for 2–10 agent collaborative teams on OpenClaw.

### What's New in v2.0

| Feature | v1.0 | v2.0 |
|---------|------|------|
| Team size | Fixed 7 | **2–10 agents** |
| Team naming | Single team | **Multiple named teams** |
| Roles | 7 preset only | **10 preset + custom roles** |
| Workflow | Fixed 9-step | **4 templates + fully custom** |
| Model assignment | Hardcoded | **Auto-detect + manual override** |

### When to Use

- Set up a multi-role collaborative development team (2–10 agents)
- Need multiple teams to work in parallel with independent configurations
- Need custom collaboration workflows (not limited to standard 9-step)
- Need flexible role combinations and model assignments

### Quick Start

#### Interactive Setup Wizard (Recommended)

```bash
# Default team
node <skill-dir>/wizard/setup.js

# Named team (supports multiple teams coexisting)
node <skill-dir>/wizard/setup.js --team alpha
node <skill-dir>/wizard/setup.js --team beta
```

The wizard guides you through:
1. **Team naming** — Give your team a name (supports multi-team setup)
2. **Select roles** — Choose 2–10 from 10 preset roles or add custom ones
3. **Assign models** — Auto-detect registered models or specify manually
4. **Select collaboration workflow** — 4 preset templates or fully custom
5. **Write config** — Auto-update openclaw.json + create workspace

### Available Role Templates (10)

| Role | ID | Emoji | Category | Default Model Type |
|------|----|-------|----------|--------------------|
| Product Manager | `pm` | 📋 | Management | Balanced |
| Architect | `architect` | 🏗️ | Engineering | Strongest |
| Frontend | `frontend` | 🎨 | Engineering | Code |
| Backend | `backend` | ⚙️ | Engineering | Code |
| QA | `qa` | 🔍 | Quality | Balanced |
| DevOps | `devops` | 🚀 | Operations | Strongest |
| Code Artisan | `code-artisan` | 🛠️ | Quality | Code |
| Data Engineer | `data-engineer` | 📊 | Engineering | Code |
| Security | `security` | 🔒 | Quality | Strongest |
| Tech Writer | `tech-writer` | 📝 | Management | Balanced |

**Custom roles:** The wizard supports adding fully custom roles (ID, name, emoji, responsibilities, model type).

### Workflow Templates (4)

#### 1. Standard 9-Step Collaboration (`standard-9step`)
```
PM → Architect Review → Frontend + Backend (parallel) → Code Review → QA → Approval → Deployment
```
Best for: Complete project development with strict process control

#### 2. Quick 3-Step Flow (`quick-3step`)
```
Direct Development → Code Review → Deployment
```
Best for: Small features, hotfixes, rapid iteration

#### 3. Fullstack Solo (`fullstack-solo`)
```
Requirements Design → Fullstack Development → Testing & Deployment
```
Best for: 2–3 person lean team

#### 4. Fully Custom (`custom`)
- Free definition of step count
- Specify roles per step (supports parallel roles)
- Set feedback loops
- Mark optional steps

### Multi-Team Support

A single OpenClaw instance can run multiple teams:

```bash
# Team alpha: frontend team
node setup.js --team alpha
# Select: frontend, qa, devops

# Team beta: backend team
node setup.js --team beta
# Select: backend, architect, qa, devops

# Team gamma: fullstack
node setup.js --team gamma
```

Each team's agent ID includes the team prefix: `alpha-frontend`, `beta-backend`, etc.

Team configs are stored at: `teamtask/teams/<team-name>.json`

### Architecture

```
~/.openclaw/
├── openclaw.json              # Agent config for all teams
├── workspace/
│   └── teamtask/
│       ├── teams/             # Team manifests
│       │   ├── default.json
│       │   ├── alpha.json
│       │   └── beta.json
│       └── tasks/             # Project task directory
└── agents/                    # Subagent directory
    ├── pm/                    # default team
    ├── alpha-frontend/        # alpha team
    ├── beta-backend/          # beta team
    └── ...
```

### Model Assignment

The wizard auto-detects registered models in `openclaw.json` and matches by type:

| Model Type | Best For | Auto-detect Pattern |
|-----------|----------|---------------------|
| Strongest Reasoning | Architect, DevOps, Security | `/opus/i` |
| Code Specialized | Frontend, Backend, Code Artisan | `/codex/i` |
| Balanced | PM, QA, Tech Writer | `/sonnet/i` |
| Fast | Simple tasks | `/haiku/i` |
| Long Context | Cross-file analysis | `/gemini.*pro/i` |

Fallback chains are auto-generated based on model type relationships.

### Collaboration Workflow

#### Activation Protocol

```
@codingteam wake up              — Activate default team
@codingteam <team-name> wake up  — Activate specified team
@codingteam <role>               — Activate specified role
@codingteam 收工                 — All team members sleep
```

#### Spawning Method

```javascript
// Spawn by agent ID
sessions_spawn({
  task: "Implement user auth API",
  agentId: "backend"        // default team
  // agentId: "alpha-backend"  // named team
})
```

### File Structure

```
skills/coding-team-setup/
├── SKILL.md               # This file
├── README.md              # Public description
├── clawhub.yaml           # ClawHub metadata
├── config/
│   └── roles.json         # Role templates + workflow templates + model types
├── templates/
│   └── SOUL-template.md   # SOUL.md template
└── wizard/
    └── setup.js           # Interactive setup wizard (v2.0)
```

### Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `agents_list` only shows main | `allowAgents` missing agent ID | Re-run wizard or add manually |
| Spawn timeout | Rate Limit / model unavailable | Check fallback chain |
| Multi-team ID conflict | --team parameter not used | Use `--team <name>` to distinguish |
| Workspace files missing | Directory deleted manually | Re-run wizard |

### Lessons Learned

1. **`allowAgents` must be under main agent's `subagents`** — not under `defaults.subagents`
2. **Model IDs must be complete** — include provider prefix
3. **Gateway must restart** — after modifying openclaw.json, run `openclaw gateway restart`
4. **Concurrency control** — spawning too many at once triggers Rate Limit; spawn in batches
5. **Team prefix** — multi-team agent IDs auto-include prefix; use full ID when spawning

### Standard Post-Setup Workflow (UPDATED in v2.2)

After creating any sub-agent team, execute this as **mandatory standard flow**:

1. **Core skill baseline assignment**
   - Assign 2–4 core skills per role directly in `openclaw.json`
   - Keep advanced/domain skills as on-demand skills

2. **Skill learning telemetry**
   - Enable usage logging per agent/skill
   - Log format: `agent_id + skill_name + timestamp + context`

3. **Weekly optimization task (OpenClaw Cron)**
   - Create a weekly `openclaw cron` job in isolated session
   - Analyze last 7 days usage and update `openclaw.json` skill mapping
   - Always backup before writing config

4. **All-team scope**
   - Mechanism must apply to **all teams** (coding/wealth/other future teams)
   - No team-specific hardcoding in the optimizer

5. **Review outputs**
   - Save weekly optimization summary to `memory/YYYY-MM-DD.md`
   - Keep optimization history under `.lib/skill_analytics/`

6. **Mandatory Subagent Timeout Governance (NEW)**
   - Do not call `sessions_spawn` directly for production fan-out checks.
   - Use timeout governance wrapper with graded timeout + retry + circuit breaker.
   - Recommended baseline:
     - Simple tasks: 60s, retry 2
     - Normal tasks: 120s, retry 3
     - Complex tasks: 180s, retry 3
   - Failure classification must be explicit in reports:
     - `SPAWN_REJECTED` / `TIMEOUT` / `NO_CHANNEL_503` / `RATE_LIMIT` / `UNKNOWN`
   - Health-check outputs must include three blocks:
     1) spawn accepted/rejected
     2) fallback trace (primary → fallback1 → fallback2)
     3) final failure type + request id (if any)

7. **Allowlist Guardrail (NEW)**
   - `allowAgents` must be merged into `main.subagents.allowAgents` (append + dedupe), never overwritten blindly.
   - After write, verify with `agents_list` that all new agents are visible before any spawn.

---

## 中文

> 灵活搭建 2–10 位子代理开发团队，支持多团队命名、自定义协作流程

### v2.0 新增特性

| 特性 | v1.0 | v2.0 |
|------|------|------|
| 团队规模 | 固定 7 人 | **2–10 人** |
| 团队命名 | 单一团队 | **多个命名团队** |
| 角色 | 7 个预设 | **10 个预设 + 自定义** |
| 协作流程 | 固定 9 步 | **4 个模板 + 完全自定义** |
| 模型分配 | 硬编码 | **自动检测 + 手动覆盖** |

### 适用场景

- 搭建一个多角色协作开发团队（2–10人）
- 需要多个团队并行工作，各自独立配置
- 需要自定义协作流程（不限于标准9步）
- 需要灵活的角色组合和模型分配

### 快速开始

#### 交互式配置向导（推荐）

```bash
# 默认团队
node <skill-dir>/wizard/setup.js

# 命名团队（支持多个团队并存）
node <skill-dir>/wizard/setup.js --team alpha
node <skill-dir>/wizard/setup.js --team beta
```

向导会引导你完成：
1. **团队命名** — 给团队一个名字（支持多团队）
2. **选择角色** — 从10个预设角色中选2–10个，或添加自定义角色
3. **分配模型** — 自动检测已注册模型，或手动指定
4. **选择协作流程** — 4个预设模板或完全自定义
5. **写入配置** — 自动更新 openclaw.json + 创建 workspace

### 可用的角色模板（10个）

| 角色 | ID | Emoji | 类别 | 默认模型类型 |
|------|-------|-------|------|------------|
| 产品经理 | `pm` | 📋 | 管理 | 均衡型 |
| 架构师 | `architect` | 🏗️ | 工程 | 最强推理 |
| 前端 | `frontend` | 🎨 | 工程 | 代码专长 |
| 后端 | `backend` | ⚙️ | 工程 | 代码专长 |
| QA | `qa` | 🔍 | 质量 | 均衡型 |
| DevOps | `devops` | 🚀 | 运维 | 最强推理 |
| 代码工匠 | `code-artisan` | 🛠️ | 质量 | 代码专长 |
| 数据工程师 | `data-engineer` | 📊 | 工程 | 代码专长 |
| 安全 | `security` | 🔒 | 质量 | 最强推理 |
| 技术文档 | `tech-writer` | 📝 | 管理 | 均衡型 |

**自定义角色：** 向导支持添加完全自定义的角色（ID、名称、emoji、职责、模型类型）。

### 协作流程模板（4个）

#### 1. 标准9步协作流程 (`standard-9step`)
```
PM → 架构师评审 → 前端 + 后端（并行） → 代码审查 → QA → 确认 → 部署
```
适合：完整项目开发，需要严格流程控制

#### 2. 快速3步流程 (`quick-3step`)
```
直接开发 → 代码审查 → 部署
```
适合：小型功能、hotfix、快速迭代

#### 3. 全栈独角兽 (`fullstack-solo`)
```
需求设计 → 全栈开发 → 测试部署
```
适合：2–3人精简团队

#### 4. 完全自定义 (`custom`)
- 自由定义步骤数量
- 每步指定角色（支持多角色并行）
- 可设置 feedback loop
- 可标记可选步骤

### 多团队支持

一个 OpenClaw 实例可以运行多个团队：

```bash
# 团队 alpha：前端团队
node setup.js --team alpha
# 选择: frontend, qa, devops

# 团队 beta：后端团队
node setup.js --team beta
# 选择: backend, architect, qa, devops

# 团队 gamma：全栈
node setup.js --team gamma
```

每个团队的 agent ID 带团队前缀：`alpha-frontend`, `beta-backend` 等。

团队配置存储在：`teamtask/teams/<team-name>.json`

### 架构

```
~/.openclaw/
├── openclaw.json              # 所有团队的 agent 配置
├── workspace/
│   └── teamtask/
│       ├── teams/             # 团队 manifest
│       │   ├── default.json
│       │   ├── alpha.json
│       │   └── beta.json
│       └── tasks/             # 项目任务目录
└── agents/                    # 子代理目录
    ├── pm/                    # default team
    ├── alpha-frontend/        # alpha team
    ├── beta-backend/          # beta team
    └── ...
```

### 模型分配

向导自动检测 `openclaw.json` 中已注册的模型，按类型匹配：

| 模型类型 | 适用角色 | 自动检测规则 |
|---------|---------|-------------|
| 最强推理 | 架构师、DevOps、安全 | `/opus/i` |
| 代码专长 | 前端、后端、代码工匠 | `/codex/i` |
| 均衡型 | PM、QA、技术文档 | `/sonnet/i` |
| 快速 | 简单任务 | `/haiku/i` |
| 长上下文 | 跨文件分析 | `/gemini.*pro/i` |

Fallback 链根据模型类型关系自动生成。

### 协作工作流

#### 唤醒协议

```
@codingteam wake up              — 激活默认团队全体
@codingteam <team-name> wake up  — 激活指定团队
@codingteam <role>               — 激活指定角色
@codingteam 收工                 — 全员休眠
```

#### 调度方式

```javascript
// 按 agent ID 生成
sessions_spawn({
  task: "实现用户认证 API",
  agentId: "backend"        // default team
  // agentId: "alpha-backend"  // named team
})
```

### 文件结构

```
skills/coding-team-setup/
├── SKILL.md               # 本文件
├── README.md              # 公开描述
├── clawhub.yaml           # ClawHub 元数据
├── config/
│   └── roles.json         # 角色模板 + 流程模板 + 模型类型
├── templates/
│   └── SOUL-template.md   # SOUL.md 模板
└── wizard/
    └── setup.js           # 交互式配置向导 (v2.0)
```

### 故障排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `agents_list` 只显示 main | `allowAgents` 缺少 agent ID | 重新运行向导或手动添加 |
| Spawn 超时 | Rate Limit / 模型不可用 | 检查 fallback 链 |
| 多团队 ID 冲突 | 未使用 --team 参数 | 用 `--team <name>` 区分 |
| Workspace 文件缺失 | 手动删除了目录 | 重新运行向导 |

### 经验教训

1. **`allowAgents` 必须在 main agent 的 `subagents` 下** — 不是 `defaults.subagents`
2. **模型 ID 必须完整** — 包含 provider 前缀
3. **Gateway 必须重启** — 修改 openclaw.json 后 `openclaw gateway restart`
4. **并发控制** — 同时 spawn 太多会触发 Rate Limit，建议分批
5. **团队前缀** — 多团队时 agent ID 自动带前缀，spawn 时要用完整 ID

### 标准后置流程（v2.2 更新）

所有子代理团队创建完成后，必须执行以下标准流程：

1. **核心技能基线配置**
   - 每个角色在 `openclaw.json` 固定配置 2–4 个核心技能
   - 进阶/领域技能保留为按需调用

2. **技能学习与使用追踪**
   - 记录每个子代理的技能调用事件
   - 记录字段：`agent_id + skill_name + timestamp + context`

3. **每周技能优化任务（OpenClaw Cron）**
   - 通过 `openclaw cron` 创建每周任务（isolated session）
   - 分析近7天使用频率，自动优化 `openclaw.json` 的技能映射
   - 写入前必须自动备份配置

4. **全团队统一适用**
   - 机制覆盖所有团队（coding/wealth/未来团队）
   - 禁止只对单一团队硬编码

5. **输出与归档**
   - 每周优化结果写入 `memory/YYYY-MM-DD.md`
   - 优化历史保存在 `.lib/skill_analytics/`

6. **子代理超时治理（新增，强制）**
   - 生产场景禁止裸调 `sessions_spawn` 做并发健康检查。
   - 必须走超时治理封装（分级超时 + 重试 + 熔断）。
   - 推荐基线：
     - 简单任务：60s，重试2次
     - 普通任务：120s，重试3次
     - 复杂任务：180s，重试3次
   - 报告必须输出统一失败分型：
     - `SPAWN_REJECTED` / `TIMEOUT` / `NO_CHANNEL_503` / `RATE_LIMIT` / `UNKNOWN`
   - 健康检查结果必须包含三段：
     1) spawn 是否 accepted
     2) fallback 轨迹（primary → fallback1 → fallback2）
     3) 最终失败类型 + request id（若有）

7. **Allowlist 防护（新增）**
   - `allowAgents` 只能合并写入 `main.subagents.allowAgents`（追加+去重），禁止覆盖清空。
   - 写入后先用 `agents_list` 验证新增代理可见，再进行 spawn。
