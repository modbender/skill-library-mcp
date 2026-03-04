# AIWorkFlow — AI 开发全流程自动化系统

> 一套面向 AI 创业团队的完整开发工具链：**6 个开发流程 Skill** + **Codex Autopilot 多项目自动化引擎** + **OpenClaw 智能调度层**

---

## 🏗 系统组成

本项目包含三大模块：

### 1. 开发流程 Skill 体系 (v1.5.0)

覆盖从需求调研到上线的完整开发周期，可集成到 Gemini / Codex / Claude 等 AI 编码助手中。

### 2. Codex Autopilot 引擎

多项目并行的 Codex CLI 自动化监控与任务编排系统，通过 tmux + launchd 实现 7×24 无人值守开发。

### 3. OpenClaw 智能调度层

通过 [OpenClaw](https://github.com/openclaw/openclaw) 提供上层智能调度能力，包括 cron 定时任务、Claude sub-agent 代码审查、Telegram 消息通道、以及跨 AI 引擎的协同编排。

---

## 📋 开发流程 Skill

```
需求调研 → 文档撰写 → 文档评审 → 开发实现 ←→ 测试设计 → 代码评审 → 发布
   │          │          │          │              │          │
   ▼          ▼          ▼          ▼              ▼          ▼
requirement  doc-       doc-     development    testing    code-
-discovery   writing    review   + Bug修复                 review
```

| Skill | 用途 | 触发示例 |
|-------|------|---------|
| **requirement-discovery** | 需求调研、RICE 评分、AI 可行性评估 | "帮我调研这个需求" |
| **doc-writing** | 撰写 PRD、技术方案、API 设计、任务清单 | "帮我写需求文档" |
| **doc-review** | 评审需求文档，发现遗漏和风险 | "评审这个 PRD" |
| **development** | 开发实现、Bug 修复（5 Whys 根因分析）、进度追踪 | "帮我实现这个功能" |
| **testing** | 测试策略、用例设计、覆盖率分析 | "帮我设计测试用例" |
| **code-review** | 三层防御代码评审（自动检查 → 增量审查 → 全量审计） | "review 这个代码" |

### 使用方式

将 Skill 目录链接到你的 AI 助手：

```bash
# Gemini
ln -sf /path/to/AIWorkFlowSkill/development ~/.gemini/skills/development

# Codex (AGENTS.md 中引用)
# Claude (Skills 目录)
```

### 核心理念

- **创业友好** — MoSCoW 快速确定 MVP，允许合理技术债（必须记录）
- **AI 原生** — 每个 Skill 包含 AI 专项检查、Prompt 规范、Token 成本控制
- **SOLID 驱动** — 开发和 Review 严格遵循 SOLID 原则
- **文档闭环** — Bug 修复追溯文档，发现问题及时反馈

---

## 🤖 Codex Autopilot 引擎

### 架构

```
                    ┌─────────────────────────────────────┐
                    │         Codex Autopilot 引擎         │
                    └─────────────────────────────────────┘

  触发层              检测层              决策层              执行层
┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ launchd  │───→│codex-status  │───→│ watchdog.sh  │───→│ tmux-send.sh │
│  (10s)   │    │   .sh        │    │  (1200行)    │    │ (三层发送)    │
└──────────┘    │ JSON状态检测  │    │ 状态机决策    │    └──────────────┘
┌──────────┐    │working/idle/ │    │指数退避/锁/  │    ┌──────────────┐
│  cron    │───→│permission/   │    │compact恢复   │───→│ task-queue.sh│
│ (10min)  │    │shell/absent  │    └──────────────┘    │ (任务队列)    │
└──────────┘    └──────────────┘           │            └──────────────┘
                                           │
                 监控层                     ▼             审查层
            ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
            │monitor-all.sh│    │  Telegram     │    │consume-review│
            │ + token统计   │───→│  通知/报告    │    │-trigger.sh   │
            └──────────────┘    └──────────────┘    └──────────────┘
```

### OpenClaw 调度层

Autopilot 引擎与 [OpenClaw](https://github.com/openclaw/openclaw) 深度集成，形成三层协同：

```
┌─────────────────────────────────────────────────────────┐
│                    OpenClaw Gateway                      │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌────────┐ │
│  │  Cron    │  │  Claude   │  │ Telegram  │  │ Task   │ │
│  │  定时任务 │  │ Sub-agent │  │  通知通道  │  │ Queue  │ │
│  └────┬─────┘  └────┬─────┘  └─────┬─────┘  └───┬────┘ │
└───────┼──────────────┼──────────────┼────────────┼──────┘
        │              │              │            │
        ▼              ▼              ▼            ▼
   monitor-all.sh  Code Review   告警/报告    用户提交任务
   (10min 报告)    (双路审查)    (状态推送)   (Codex 空闲时派发)
```

**OpenClaw 提供的关键能力：**

| 能力 | 说明 |
|------|------|
| **Cron 定时任务** | 10 分钟监控报告、每日工作总结、PRD 自动验收、竞品监控 |
| **Claude Sub-agent** | 独立 Claude 实例执行代码审查，与 Codex 形成**双路交叉审查** |
| **Telegram 通道** | 实时状态推送、告警通知、任务接收（用户发 Telegram → Claude 写入队列 → Codex 执行） |
| **跨引擎协同** | Claude（审查/分析）+ Codex（编码/修复）各司其职，通过触发文件协调 |
| **对话式管理** | 通过 Telegram 与 Claude 对话，即时查询项目状态、派发任务、触发审查 |

**典型协同流程：**

```
用户 (Telegram) → "ReplyHer 有个白屏 bug"
       ↓
Claude (OpenClaw) → 写入 task-queue → 等待 Codex idle
       ↓
Watchdog 检测 idle → 从队列取出任务 → tmux send-keys 发给 Codex
       ↓
Codex 修复 → commit → watchdog 检测 commit 数达标
       ↓
触发 Claude sub-agent 代码审查 → 发现问题 → 再派给 Codex 修
       ↓
Review CLEAN → Telegram 通知用户 "✅ 白屏 bug 已修复"
```

### 核心脚本

| 脚本 | 行数 | 功能 |
|------|------|------|
| `scripts/watchdog.sh` | ~1200 | 主守护进程 — 状态检测、自动 nudge、权限处理、compact 恢复、任务队列调度 |
| `scripts/codex-status.sh` | ~150 | Codex TUI 状态检测，输出 JSON (working/idle/permission/shell/absent) |
| `scripts/tmux-send.sh` | ~230 | 三层消息发送：send-keys ≤300 / chunked ≤800 / paste-buffer >800 字符 |
| `scripts/monitor-all.sh` | ~450 | 10 分钟全局监控 + Telegram 报告（commit、context、lifecycle） |
| `scripts/task-queue.sh` | ~200 | 任务队列 CRUD — 支持优先级、自动完成、失败重试 |
| `scripts/consume-review-trigger.sh` | ~420 | Layer 2 代码审查消费者（触发文件驱动） |
| `scripts/auto-nudge.sh` | ~140 | 独立 nudge 脚本（可单独调用） |
| `scripts/prd_verify_engine.py` | ~500 | PRD 验证引擎 — checker 插件系统，"proof of done" |
| `scripts/codex-token-daily.py` | ~380 | Token 用量统计（从 Codex JSONL 会话提取） |
| `scripts/status-sync.sh` | ~200 | 项目状态自动同步到 status.json |

### 防护机制

| 机制 | 说明 |
|------|------|
| **指数退避** | nudge 间隔 300→600→1200→2400→4800→9600s，6 次后停止 + Telegram 告警 |
| **3 次 idle 确认** | 避免 API 延迟导致误判 |
| **90s 工作惯性** | 刚检测到 working 的 90s 内不 nudge |
| **手动任务保护** | 人工发送的任务 90s 内不被 watchdog 覆盖 |
| **Compact 上下文快照** | compact 前保存任务状态（未提交文件、当前任务），compact 后精准恢复 |
| **原子锁 (mkdir)** | macOS 无 flock，用 mkdir 实现带过期回收的原子锁 |
| **运行时文件隔离** | status.json 等运行时文件 gitignore，避免 dirty repo 阻塞 Codex |

### 快速开始

```bash
# 1. 配置项目
cat > watchdog-projects.conf << EOF
ProjectA:/path/to/project-a:默认 nudge 消息
ProjectB:/path/to/project-b:默认 nudge 消息
EOF

# 2. 配置 Telegram (config.yaml)
telegram:
  bot_token: "your-bot-token"
  chat_id: "your-chat-id"

# 3. 创建 tmux session
tmux new-session -s autopilot -n ProjectA
# 在窗口中启动: codex --full-auto

# 4. 启动 watchdog
nohup bash scripts/watchdog.sh &

# 5. (可选) 设置 cron 监控
# 每 10 分钟运行 monitor-all.sh
*/10 * * * * bash ~/.autopilot/scripts/monitor-all.sh
```

### 任务队列

支持在 Codex 忙碌时提交任务，空闲时自动派发：

```bash
# 添加任务
bash scripts/task-queue.sh add myproject "修复登录页白屏bug" high

# 查看队列
bash scripts/task-queue.sh list myproject

# 全局概览
bash scripts/task-queue.sh summary
```

Watchdog 在 Codex idle 时自动从队列中取出任务并发送。

---

## 📁 项目结构

```
AIWorkFlowSkill/
├── README.md                    # 本文件
├── CONVENTIONS.md               # 项目约定（Codex 必读）
├── CONTRIBUTING.md              # 贡献指南
├── LICENSE                      # MIT
│
├── requirement-discovery/       # Skill: 需求调研
│   ├── SKILL.md
│   └── references/
├── doc-writing/                 # Skill: 文档撰写
│   ├── SKILL.md
│   └── references/
├── doc-review/                  # Skill: 文档评审
│   ├── SKILL.md
│   └── references/
├── development/                 # Skill: 开发实现
│   ├── SKILL.md
│   ├── references/
│   └── scripts/                 # 会话管理脚本
├── testing/                     # Skill: 测试设计
│   ├── SKILL.md
│   └── references/
├── code-review/                 # Skill: 代码评审
│   ├── SKILL.md
│   └── references/
│
├── scripts/                     # Autopilot 引擎
│   ├── watchdog.sh              # 主守护进程
│   ├── codex-status.sh          # 状态检测
│   ├── tmux-send.sh             # 消息发送
│   ├── monitor-all.sh           # 监控报告
│   ├── task-queue.sh            # 任务队列
│   ├── consume-review-trigger.sh
│   ├── prd_verify_engine.py     # PRD 验证
│   └── ...
│
├── watchdog-projects.conf       # 项目配置
├── config.yaml                  # Telegram 等配置
├── prd-items.yaml               # PRD 验证定义
│
├── lib/                         # Phase 1-3 Python (legacy)
└── tests/                       # Phase 1-3 测试 (200 tests)
```

---

## 版本历史

| 版本 | 日期 | 更新 |
|------|------|------|
| **2.0.0** | 2026-02-12 | Autopilot 引擎: watchdog v6、三层 tmux 发送、任务队列、compact 上下文快照、PRD 验证引擎 |
| 1.5.0 | 2026-01-19 | 集成 guo-yu/skills 工具；新增危险命令阻止列表 |
| 1.4.1 | 2026-01-18 | 新增 testing skill；会话持久化与恢复 |
| 1.3.0 | 2026-01-17 | 文档管理规范；渐进式讨论快速确认 |
| 1.2.0 | 2026-01-17 | development skill Bug 修复章节 |
| 1.1.0 | 2025-01-17 | 新增 requirement-discovery skill |
| 1.0.0 | 2025-01-17 | 初始版本: 4 个核心 Skill |

---

## License

MIT
