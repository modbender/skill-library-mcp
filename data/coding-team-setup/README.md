# Coding Team Setup v2.2

## English

Flexible multi-agent development team wizard for OpenClaw.

### Features

- **2–10 agents** — pick from 10 preset roles or create custom ones
- **Multiple teams** — run parallel teams with `--team <name>`
- **4 workflow templates** — standard 9-step, quick 3-step, fullstack solo, or fully custom
- **Smart model assignment** — auto-detects registered models, maps by type
- **One command setup** — wizard handles openclaw.json + workspaces + manifests
- **Standard post-setup flow** — core-skill baseline + weekly skill optimization cron
- **Mandatory timeout governance** — graded timeout/retry/circuit-breaker for subagent fan-out checks
- **Allowlist guardrail** — merge + dedupe to `main.subagents.allowAgents` before spawn
- **Cross-team optimization** — one mechanism for coding/wealth/all future teams

### Usage

```bash
node wizard/setup.js                  # Default team
node wizard/setup.js --team alpha     # Named team
```

### Preset Roles

📋 PM · 🏗️ Architect · 🎨 Frontend · ⚙️ Backend · 🔍 QA · 🚀 DevOps · 🛠️ Code Artisan · 📊 Data Engineer · 🔒 Security · 📝 Tech Writer

Plus unlimited custom roles.

### Requirements

- OpenClaw installed with `openclaw.json` present
- Node.js 18+
- At least one model registered

See `SKILL.md` for full documentation.

---

## 中文

灵活搭建 OpenClaw 多子代理开发团队的向导。

### 特性

- **2–10 人团队** — 从 10 个预设角色中选择或创建自定义角色
- **多团队支持** — 使用 `--team <name>` 并行运行多个团队
- **4 种协作流程模板** — 标准 9 步、快速 3 步、全栈独角兽或完全自定义
- **智能模型分配** — 自动检测已注册模型，按类型映射
- **一键配置** — 向导自动处理 openclaw.json + workspace + manifests
- **标准后置流程** — 核心技能基线 + 每周技能优化 Cron
- **强制超时治理** — 子代理并发检查必须走分级超时/重试/熔断
- **Allowlist 防护** — spawn 前先完成 `main.subagents.allowAgents` 合并去重校验
- **跨团队统一优化** — coding/wealth/未来团队共用一套机制

### 使用方法

```bash
node wizard/setup.js                  # 默认团队
node wizard/setup.js --team alpha     # 命名团队
```

### 预设角色

📋 产品经理 · 🏗️ 架构师 · 🎨 前端 · ⚙️ 后端 · 🔍 QA · 🚀 DevOps · 🛠️ 代码工匠 · 📊 数据工程师 · 🔒 安全 · 📝 技术文档

加上无限自定义角色。

### 需求

- 已安装 OpenClaw 且 `openclaw.json` 存在
- Node.js 18+
- 至少注册了一个模型

完整文档请查看 `SKILL.md`。
