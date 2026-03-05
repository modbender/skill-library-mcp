**[English](#english) | [中文](#中文)**

> **🌐 Multilingual Versions:** This project maintains an English-only branch `i18n-en` for international users. Switch via: `git checkout i18n-en`

---

<a id="english"></a>

# Teamclaw (Mini TimeBot)

> **OpenAI-compatible AI Agent with a built-in programmable multi-expert orchestration engine and one-click public deployment.**
>
> **Skill Mode:** This repository is designed to run and be documented in a Skill-oriented workflow (see `SKILL.md`).

Mini TimeBot exposes a standard `/v1/chat/completions` endpoint that any OpenAI-compatible client can call directly. Internally it integrates the **OASIS orchestration engine** — using YAML schedule definitions to flexibly compose expert roles, speaking orders, and collaboration patterns, breaking complex problems into multi-perspective debates, voting consensus, and automated summaries.

## Highlights

### 1. OpenAI-Compatible API

```bash
curl http://127.0.0.1:51200/v1/chat/completions \
  -H "Authorization: Bearer <user>:<password>" \
  -H "Content-Type: application/json" \
  -d '{"model":"mini-timebot","messages":[{"role":"user","content":"Hello"}],"stream":true}'
```

- Fully compatible with OpenAI Chat Completions format, streaming & non-streaming
- Multi-turn conversation, image input (Vision), audio input, file upload, TTS
- Works with ChatBox, Open WebUI, Cursor, or any OpenAI-compatible client
- Multi-user + multi-session isolation, SQLite-persisted conversation memory

### 2. OASIS Orchestration — A Programmable Expert Collaboration Engine

**This is the core design of the entire project.**

Traditional multi-agent systems are either fully parallel or fixed pipelines, unable to adapt to different scenarios. The OASIS engine uses a concise **YAML schedule definition** that lets users (or the AI Agent itself) precisely orchestrate every step of expert collaboration:

```yaml
# Example: Creative and Critical experts clash first, then everyone summarizes
version: 1
repeat: true
plan:
  - expert: "Creative Expert"      # Single expert speaks sequentially
  - expert: "Critical Expert"      # Immediately rebuts
  - parallel:                      # Multiple experts speak in parallel
      - "Economist"
      - "Legal Expert"
  - all_experts: true              # All participants speak simultaneously
```

#### Three Layers of Control

| Dimension | Control | Description |
|-----------|---------|-------------|
| **Who participates** | `expert_tags` | Select from 10+ built-in experts + user-defined custom expert pool |
| **How they discuss** | `schedule_yaml` | 4 step types freely combined (sequential / parallel / all / manual injection) |
| **How deep** | `max_rounds` + `use_bot_session` | Control round depth; choose stateful (memory + tools) or stateless (lightweight & fast) |

#### Four Schedule Step Types

| Step Type | Format | Effect |
|-----------|--------|--------|
| `expert` | `- expert: "Name"` | Single expert speaks sequentially |
| `parallel` | `- parallel: ["A", "B"]` | Multiple experts speak simultaneously |
| `all_experts` | `- all_experts: true` | All selected experts speak at once |
| `manual` | `- manual: {author: "Host", content: "..."}` | Inject fixed content (bypasses LLM) |

Set `repeat: true` to loop the plan each round; `repeat: false` executes plan steps once then ends.

#### Expert Pool

**10 Built-in Public Experts:**

| Expert | Tag | Temp | Role |
|--------|-----|------|------|
| 🎨 Creative Expert | `creative` | 0.9 | Finds opportunities, proposes visionary ideas |
| 🔍 Critical Expert | `critical` | 0.3 | Spots risks, flaws, and logical fallacies |
| 📊 Data Analyst | `data` | 0.5 | Data-driven, speaks with facts |
| 🎯 Synthesis Advisor | `synthesis` | 0.5 | Integrates perspectives, proposes pragmatic plans |
| 📈 Economist | `economist` | 0.5 | Macro/micro economic perspective |
| ⚖️ Legal Expert | `lawyer` | 0.3 | Compliance and legal risk analysis |
| 💰 Cost Controller | `cost_controller` | 0.4 | Budget-sensitive, cost reduction |
| 📊 Revenue Planner | `revenue_planner` | 0.6 | Revenue maximization strategy |
| 🚀 Entrepreneur | `entrepreneur` | 0.8 | 0-to-1 hands-on perspective |
| 🧑 Common Person | `common_person` | 0.7 | Down-to-earth common sense feedback |

**User-Defined Custom Experts:** Each user can create private experts (name, tag, persona, temperature) through the Agent, mixed with public experts, isolated per user.

#### Discussion Mechanics

Each expert per round:
1. **Post** — Opinion within 200 characters, can reference an existing post
2. **Vote** — Up/down vote on other posts

Engine auto-executes:
- **Consensus Detection** — Top-voted post reaches ≥70% expert approval → early termination
- **Conclusion Generation** — Synthesizes Top 5 highest-voted posts via LLM summary

#### Two Expert Running Modes

| Mode | `use_bot_session` | Features |
|------|-------------------|----------|
| **Stateless** (default) | `False` | Lightweight & fast, independent LLM call per round, no memory, no tools |
| **Stateful** | `True` | Each expert gets a persistent session with memory, can invoke search/file/code tools, sessions visible in frontend |

### 3. Multi-Platform Bot Integration (Telegram & QQ)

Mini TimeBot integrates with popular messaging platforms, allowing users to interact with the Agent through Telegram or QQ:

#### Telegram Bot

**Features:**
- Multimodal input: text, images, voice messages
- User isolation: each Telegram user maps to a system account
- Whitelist security: only authorized users can interact with the bot
- 30-second hot-reload whitelist (no restart needed)
- Push notifications: Agent can proactively send messages to users

**Setup:**
1. Create a Telegram bot via [@BotFather](https://t.me/botfather) and get the token
2. Set `TELEGRAM_BOT_TOKEN` in `config/.env`
3. Start the bot: `python chatbot/telegrambot.py`
4. Tell Agent your Telegram chat_id: "Set my Telegram chat_id to 123456789"

**User commands:**
- Send any message/image/voice to the bot → Agent responds
- Agent can push notifications to your Telegram proactively

#### QQ Bot

**Features:**
- Private chat (C2C) and group chat (@mention)
- Image and voice support (SILK format auto-transcoding)
- OpenAI-compatible multimodal input

**Setup:**
1. Register a QQ bot at [QQ Open Platform](https://bot.q.qq.com/)
2. Set `QQ_APP_ID` and `QQ_BOT_SECRET` in `config/.env`
3. Start the bot: `python chatbot/QQbot.py`

### 4. Advanced Agent Interaction

Mini TimeBot provides sophisticated user-Agent interaction features:

#### User Profile System

Each user can maintain a personalized profile that the Agent references:

```
data/user_files/{username}/user_profile.txt
```

Tell Agent: "Remember that I'm a Python developer interested in AI" → Profile saved and injected into future conversations.

#### Skill System

Users can define custom skills (reusable prompt templates):

```json
// data/user_files/{username}/skills_manifest.json
[
  {
    "name": "Code Reviewer",
    "description": "Review code for best practices",
    "file": "code_reviewer.md"
  }
]
```

Agent shows available skills in each session and can execute them on demand.

#### Dynamic Tool Management

- Tools can be enabled/disabled per-session
- Agent notifies user when tool status changes
- Security-critical tools protected by default

#### External Tool Injection

External systems can inject custom tools via OpenAI-compatible API:

```python
# Caller sends tool definitions
response = client.chat.completions.create(
    model="mini-timebot",
    messages=[...],
    tools=[{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather",
            "parameters": {...}
        }
    }]
)
# Agent may call the tool → returns tool_calls to caller
# Caller executes tool and sends result back
```

### 5. One-Click Public Deployment

Run a single command to expose the entire service to the internet — **zero configuration, no account needed**:

```bash
python scripts/tunnel.py
```

- Uses **Cloudflare Quick Tunnel** to automatically obtain a temporary `*.trycloudflare.com` domain
- Auto-detects platform → downloads `cloudflared` if missing → starts tunnels → captures public URLs → writes to `.env`
- Exposes both the **Web UI** (port 51209) and **Bark push service** (port 58010) simultaneously
- Also available interactively via `run.sh` ("Deploy to public network? y/N")
- Push notification click-through URLs are automatically configured — users can also override via AI chat

#### Bidirectional OASIS

The Agent has both "convene" and "participate" capabilities:

| | 🏠 Internal OASIS (Convene) | 🌐 External OASIS (Participate) |
|---|---|---|
| **Initiator** | Agent calls `post_to_oasis` | External system sends message via OpenAI-compatible API |
| **Participants** | Local expert pool | Multiple independent Agent nodes |
| **Trigger** | User question → Agent decides | External request via `/v1/chat/completions` |
| **Result** | Conclusion returned to user | Agent opinion returned in standard OpenAI response format |

---

## Architecture

```
Browser (Chat UI + Login + OASIS Panel)
    │  HTTP :51209
    ▼
front.py (Flask + Session)     ── Frontend proxy, login/chat pages, session management
    │  HTTP :51200
    ▼
mainagent.py (FastAPI + LangGraph)  ── OpenAI-compatible API + Core Agent
    │  stdio (MCP)                      (External OASIS also via OpenAI API)
    ├── mcp_scheduler.py   ── Alarm/scheduled task management
    │       │  HTTP :51201
    │       ▼
    ├── time.py (APScheduler)  ── Scheduling center
    ├── mcp_search.py      ── DuckDuckGo web search
    ├── mcp_filemanager.py ── User file management (sandboxed)
    ├── mcp_oasis.py       ── OASIS discussion + expert management
    │       │  HTTP :51202
    │       ▼
    │   oasis/server.py    ── OASIS forum service (engine + expert pool)
    ├── mcp_bark.py        ── Bark mobile push notifications
    ├── mcp_telegram.py    ── Telegram push + whitelist sync
    └── mcp_commander.py   ── Sandboxed command/code execution

┌─────────────────────────────────────────────────────────────────┐
│                    External Bot Services                         │
├─────────────────────────────────────────────────────────────────┤
│  telegrambot.py         ── Telegram Bot (text/image/voice)       │
│  QQbot.py               ── QQ Bot (C2C/Group, SILK transcoding)  │
│                                                                  │
│  Both bots call mainagent.py via OpenAI-compatible API           │
│  with user-isolated sessions (INTERNAL_TOKEN:user:BOT)           │
└─────────────────────────────────────────────────────────────────┘
```

### Ports

| Service | Port | Description |
|---------|------|-------------|
| `front.py` | 51209 | Web UI (login + chat + OASIS panel) |
| `mainagent.py` | 51200 | OpenAI-compatible API + Agent core |
| `time.py` | 51201 | Scheduling center |
| `oasis/server.py` | 51202 | OASIS forum service |

> Ports configurable in `config/.env`.

### MCP Toolset

7 tool services integrated via MCP protocol. All `username` parameters are auto-injected, fully isolated between users:

| Tool Service | Capability |
|-------------|------------|
| **Search** | DuckDuckGo web search |
| **Scheduler** | Natural language alarms/reminders, Cron expressions |
| **File Manager** | User file CRUD, path traversal protection |
| **Commander** | Shell commands and Python code in secure sandbox |
| **OASIS Forum** | Start discussions, check progress, manage custom experts |
| **Bark Push** | Push notifications to iOS/macOS devices |
| **Telegram** | Push messages to Telegram, whitelist management |

---

## Quick Start

### One-Click Run (Recommended)

```bash
# Linux / macOS
chmod +x run.sh
./run.sh

# Windows
run.bat
```

The script handles: environment setup → API Key config → create user → start all services.

> Manual steps below can be skipped if using `run.sh` / `run.bat`.

### Manual Setup

**1. Environment**

```bash
# Auto (recommended)
scripts/setup_env.sh   # Linux/macOS
scripts\setup_env.bat  # Windows

# Manual
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -r config/requirements.txt
```

**2. API Key**

Set in `config/.env`:
```
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

**3. Create User**

```bash
scripts/adduser.sh     # Linux/macOS
scripts\adduser.bat    # Windows
```

**4. Start Services**

```bash
# One-click
scripts/start.sh       # Linux/macOS
scripts\start.bat      # Windows

# Manual (3 terminals)
python src/time.py         # Scheduler
python src/mainagent.py    # Agent + MCP tools
python src/front.py        # Web UI
```

Visit http://127.0.0.1:51209 after startup.

### Public Deployment (Optional)

One-click exposure via Cloudflare Tunnel (see [Highlight #3](#3-one-click-public-deployment) for details):
```bash
python scripts/tunnel.py
# Or interactively via run.sh — prompts "Deploy to public network? (y/N)"
```
Auto-downloads `cloudflared`, starts tunnels for Web UI + Bark push, captures public URLs, and writes them to `.env`. No account or DNS setup required.

---

## API Reference

### OpenAI-Compatible Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/chat/completions` | POST | Chat completions (streaming/non-streaming), fully OpenAI-compatible |
| `/login` | POST | User login authentication |
| `/sessions` | POST | List user sessions |
| `/session_history` | POST | Get session history |

### OASIS Forum Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/topics` | POST | Create discussion topic |
| `/topics` | GET | List all topics |
| `/topics/{id}` | GET | Get topic details |
| `/topics/{id}/stream` | GET | SSE real-time update stream |
| `/topics/{id}/conclusion` | GET | Block until conclusion ready |
| `/experts` | GET | List experts (public + user custom) |
| `/experts/user` | POST/PUT/DELETE | User custom expert CRUD |

---

## Authentication

- **Password Storage**: SHA-256 hash only, no plaintext on disk
- **Session Management**: Flask signed Cookie, `sessionStorage` expires on tab close
- **Request Verification**: Every `/ask` re-verifies password
- **Internal Auth**: Inter-service communication via `INTERNAL_TOKEN` (auto-generated 64-char hex)
- **User Isolation**: Conversation memory, file storage, custom experts all isolated by `user_id`

---

## Project Structure

```
mini_timebot/
├── run.sh / run.bat               # One-click run
├── scripts/                       # Env setup, start, tunnel, user management
├── packaging/                     # Windows exe / macOS DMG packaging
├── chatbot/                       # External bot services
│   ├── telegrambot.py             # Telegram Bot (text/image/voice)
│   ├── QQbot.py                   # QQ Bot (C2C/Group, SILK transcoding)
│   └── setup.py                   # Bot configuration helper
├── config/
│   ├── .env                       # API keys and env vars
│   ├── requirements.txt           # Python dependencies
│   └── users.json                 # Username-password hash
├── data/
│   ├── agent_memory.db            # Conversation memory (SQLite)
│   ├── telegram_whitelist.json    # Telegram bot whitelist
│   ├── prompts/                   # System prompts + expert configs
│   │   ├── oasis_experts.json     # 10 public expert definitions
│   │   ├── oasis_expert_discuss.txt  # Expert discussion prompt template
│   │   └── oasis_summary.txt     # Conclusion generation prompt template
│   ├── schedules/                 # YAML schedule examples
│   ├── oasis_user_experts/        # User custom experts (per-user JSON)
│   ├── timeset/                   # Scheduled task persistence
│   └── user_files/                # User files (isolated per user)
│       └── {username}/
│           ├── user_profile.txt   # User profile
│           ├── skills_manifest.json  # User skills
│           └── tg_chat_id.txt     # Telegram chat ID
├── src/
│   ├── mainagent.py               # OpenAI-compatible API + Agent core
│   ├── agent.py                   # LangGraph workflow + tool orchestration
│   ├── front.py                   # Flask Web UI
│   ├── time.py                    # Scheduling center
│   └── mcp_*.py                   # 7 MCP tool services
├── oasis/
│   ├── server.py                  # OASIS FastAPI service
│   ├── engine.py                  # Discussion engine (rounds + consensus + conclusion)
│   ├── experts.py                 # Expert definitions + user expert storage
│   ├── scheduler.py               # YAML schedule parsing & execution
│   ├── forum.py                   # Forum data structures
│   └── models.py                  # Pydantic models
├── tools/
│   └── gen_password.py            # Password hash generator
└── test/
    ├── chat.py                    # CLI test client
    └── view_history.py            # View chat history
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | DeepSeek (`deepseek-chat`) |
| Agent Framework | LangGraph + LangChain |
| Tool Protocol | MCP (Model Context Protocol) |
| Backend | FastAPI + Flask |
| Auth | SHA-256 Hash + Flask Session |
| Scheduling | APScheduler |
| Persistence | SQLite (aiosqlite) |
| Frontend | Tailwind CSS + Marked.js + Highlight.js |

## License

MIT License

---

<a id="中文"></a>

# Mini TimeBot

**[English](#english) | [中文](#中文)**

> **OpenAI 兼容的 AI Agent，内置可编程多专家协作引擎，支持一键部署到公网。**

Mini TimeBot 对外暴露标准 `/v1/chat/completions` 接口，可以被任何 OpenAI 兼容客户端直接调用；对内集成 **OASIS 智能编排引擎**——通过 YAML 调度定义，灵活组合专家角色、发言顺序和协作模式，将复杂问题拆解为多视角辩论、投票共识、自动总结的完整流程。

## 核心亮点

### 1. OpenAI 兼容 API

```bash
curl http://127.0.0.1:51200/v1/chat/completions \
  -H "Authorization: Bearer <user>:<password>" \
  -H "Content-Type: application/json" \
  -d '{"model":"mini-timebot","messages":[{"role":"user","content":"你好"}],"stream":true}'
```

- 完全兼容 OpenAI Chat Completions 格式，支持流式/非流式响应
- 支持多轮对话、图片输入（Vision）、音频输入、文件上传、TTS
- 可被 ChatBox、Open WebUI、Cursor 等任何 OpenAI 兼容客户端直接接入
- 多用户 + 多会话隔离，SQLite 持久化对话记忆

### 2. OASIS 智能编排——可编程的专家协作引擎

**这是整个项目的核心设计。**

传统的多 Agent 系统要么全部并行、要么固定流水线，无法灵活应对不同场景。OASIS 引擎通过一份简洁的 **YAML 调度定义**，让用户（或 AI Agent 自身）能精确编排专家协作的每一个环节：

```yaml
# 示例：先让创意和批判两位专家交锋，再让所有人总结
version: 1
repeat: true
plan:
  - expert: "创意专家"           # 单人顺序发言
  - expert: "批判专家"           # 紧接着反驳
  - parallel:                    # 多人并行发言
      - "经济学家"
      - "法学家"
  - all_experts: true            # 所有参与者同时发言
```

#### 三层可控性

| 维度 | 控制方式 | 说明 |
|------|----------|------|
| **谁参与** | `expert_tags` | 从 10+ 内置专家 + 用户自定义专家池中选人 |
| **怎么讨论** | `schedule_yaml` | 4 种步骤类型自由组合（顺序 / 并行 / 全员 / 手动注入） |
| **多深入** | `max_rounds` + `use_bot_session` | 控制轮次深度，可选有状态（记忆+工具）或无状态（轻量快速） |

#### 四种调度步骤

| 步骤类型 | 格式 | 效果 |
|----------|------|------|
| `expert` | `- expert: "专家名"` | 单个专家顺序发言 |
| `parallel` | `- parallel: ["A", "B"]` | 多个专家同时并行发言 |
| `all_experts` | `- all_experts: true` | 所有选中专家同时发言 |
| `manual` | `- manual: {author: "主持人", content: "..."}` | 注入固定内容（不经过 LLM） |

设置 `repeat: true` 时，调度计划每轮循环执行；`repeat: false` 则按步骤顺序执行一次后结束。

#### 专家池

**10 位内置公共专家**：

| 专家 | Tag | 温度 | 定位 |
|------|-----|------|------|
| 🎨 创意专家 | `creative` | 0.9 | 发现机遇，提出前瞻性想法 |
| 🔍 批判专家 | `critical` | 0.3 | 发现风险漏洞，严谨质疑 |
| 📊 数据分析师 | `data` | 0.5 | 数据驱动，用事实说话 |
| 🎯 综合顾问 | `synthesis` | 0.5 | 综合各方，提出务实方案 |
| 📈 经济学家 | `economist` | 0.5 | 宏观/微观经济视角 |
| ⚖️ 法学家 | `lawyer` | 0.3 | 合规性与法律风险 |
| 💰 成本限制者 | `cost_controller` | 0.4 | 预算敏感，降本增效 |
| 📊 收益规划者 | `revenue_planner` | 0.6 | 收益最大化策略 |
| 🚀 创新企业家 | `entrepreneur` | 0.8 | 从 0 到 1 的实战视角 |
| 🧑 普通人 | `common_person` | 0.7 | 接地气的常识反馈 |

**用户自定义专家**：每个用户可通过 Agent 创建私有专家（定义名称、tag、persona、温度），与公共专家混合使用，按用户隔离。

#### 讨论机制

每位专家每轮：
1. **发帖** — 200 字以内的观点，可标注回复某个已有帖子
2. **投票** — 对其他帖子投 up/down

引擎自动执行：
- **共识检测** — 最高票帖子获得 ≥70% 专家赞成 → 提前结束
- **结论生成** — 综合 Top 5 高赞帖子，LLM 生成最终总结

#### 两种专家运行模式

| 模式 | `use_bot_session` | 特点 |
|------|-------------------|------|
| **无状态**（默认） | `False` | 轻量快速，每轮独立调 LLM，无记忆无工具 |
| **有状态** | `True` | 每位专家创建持久 session，有记忆、能调用搜索/文件/代码执行等全部工具，session 可在前端查看和继续对话 |

### 3. 多平台 Bot 接入（Telegram & QQ）

Mini TimeBot 集成主流即时通讯平台，用户可通过 Telegram 或 QQ 与 Agent 交互：

#### Telegram Bot

**功能特性：**
- 多模态输入：文字、图片、语音消息
- 用户隔离：每个 Telegram 用户映射到独立系统账户
- 白名单安全：仅授权用户可与机器人交互
- 30 秒热重载白名单（无需重启）
- 主动推送：Agent 可主动向用户发送 Telegram 消息

**配置步骤：**
1. 通过 [@BotFather](https://t.me/botfather) 创建 Telegram Bot 并获取 Token
2. 在 `config/.env` 中设置 `TELEGRAM_BOT_TOKEN`
3. 启动机器人：`python chatbot/telegrambot.py`
4. 告诉 Agent 你的 Telegram chat_id："设置我的 Telegram chat_id 为 123456789"

**用户使用：**
- 向机器人发送任意消息/图片/语音 → Agent 回复
- Agent 可主动推送通知到你的 Telegram

#### QQ Bot

**功能特性：**
- 私聊（C2C）和群聊（@机器人）
- 图片和语音支持（SILK 格式自动转码）
- OpenAI 兼容多模态输入

**配置步骤：**
1. 在 [QQ 开放平台](https://bot.q.qq.com/) 注册机器人
2. 在 `config/.env` 中设置 `QQ_APP_ID` 和 `QQ_BOT_SECRET`
3. 启动机器人：`python chatbot/QQbot.py`

### 4. 高级 Agent 互动

Mini TimeBot 提供丰富的用户-Agent 互动功能：

#### 用户画像系统

每个用户可维护专属画像，Agent 在对话中自动参考：

```
data/user_files/{用户名}/user_profile.txt
```

告诉 Agent："记住我是 Python 开发者，关注 AI 领域" → 画像保存并在后续对话中注入。

#### 技能系统

用户可定义自定义技能（可复用的提示词模板）：

```json
// data/user_files/{用户名}/skills_manifest.json
[
  {
    "name": "代码审查员",
    "description": "审查代码并提出最佳实践建议",
    "file": "code_reviewer.md"
  }
]
```

Agent 在每个会话中显示可用技能，并按需执行。

#### 动态工具管理

- 工具可按会话启用/禁用
- 工具状态变更时 Agent 通知用户
- 安全敏感工具默认受保护

#### 外部工具注入

外部系统可通过 OpenAI 兼容 API 注入自定义工具：

```python
# 调用方发送工具定义
response = client.chat.completions.create(
    model="mini-timebot",
    messages=[...],
    tools=[{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取当前天气",
            "parameters": {...}
        }
    }]
)
# Agent 可能调用工具 → 返回 tool_calls 给调用方
# 调用方执行工具并发送结果回去
```

### 5. 一键部署到公网

一条命令将整个服务暴露到互联网——**零配置、无需账户**：

```bash
python scripts/tunnel.py
```

- 使用 **Cloudflare Quick Tunnel**，自动获取临时 `*.trycloudflare.com` 域名
- 全自动流程：检测平台 → 下载 `cloudflared`（若缺失）→ 启动隧道 → 捕获公网地址 → 写入 `.env`
- 同时暴露 **Web UI**（端口 51209）和 **Bark 推送服务**（端口 58010）
- 也可通过 `run.sh` 交互启动（提示"是否部署到公网？y/N"）
- 推送通知的点击跳转地址自动配置——用户还可通过 AI 对话自行覆盖

#### 双向 OASIS 能力

Agent 同时具备"主动召集"和"被邀参与"两种角色：

| | 🏠 内部 OASIS（主动召集） | 🌐 外部 OASIS（被邀参与） |
|---|---|---|
| **发起方** | Agent 调用 `post_to_oasis` | 外部系统通过 OpenAI 兼容 API 发送消息 |
| **参与者** | 本地专家池 | 多个独立 Agent 节点 |
| **触发** | 用户提问 → Agent 自主决策 | 外部请求通过 `/v1/chat/completions` |
| **结果** | 结论直接返回用户 | Agent 意见以标准 OpenAI 格式返回 |

---

## 架构概览

```
浏览器 (聊天 UI + 登录页 + OASIS 论坛面板)
    │  HTTP :51209
    ▼
front.py (Flask + Session)     ── 前端代理，渲染登录/聊天页面，管理会话凭证
    │  HTTP :51200
    ▼
mainagent.py (FastAPI + LangGraph)  ── OpenAI 兼容 API + 核心 Agent
    │  stdio (MCP)                      （外部 OASIS 同样通过 OpenAI API 接入）
    ├── mcp_scheduler.py   ── 闹钟/定时任务管理
    │       │  HTTP :51201
    │       ▼
    ├── time.py (APScheduler)  ── 定时调度中心
    ├── mcp_search.py      ── DuckDuckGo 联网搜索
    ├── mcp_filemanager.py ── 用户文件管理（沙箱隔离）
    ├── mcp_oasis.py       ── OASIS 多专家讨论 + 专家管理
    │       │  HTTP :51202
    │       ▼
    │   oasis/server.py    ── OASIS 论坛服务（调度引擎 + 专家池）
    ├── mcp_bark.py        ── Bark 手机推送通知
    ├── mcp_telegram.py    ── Telegram 推送 + 白名单同步
    └── mcp_commander.py   ── 安全沙箱命令/代码执行

┌─────────────────────────────────────────────────────────────────┐
│                      外部 Bot 服务                               │
├─────────────────────────────────────────────────────────────────┤
│  telegrambot.py         ── Telegram Bot（文字/图片/语音）         │
│  QQbot.py               ── QQ Bot（私聊/群聊，SILK 转码）         │
│                                                                  │
│  两个 Bot 均通过 OpenAI 兼容 API 调用 mainagent.py               │
│  使用用户隔离会话（INTERNAL_TOKEN:用户名:BOT）                    │
└─────────────────────────────────────────────────────────────────┘
```

### 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| `front.py` | 51209 | Web UI（登录 + 聊天 + OASIS 面板） |
| `mainagent.py` | 51200 | OpenAI 兼容 API + Agent 核心 |
| `time.py` | 51201 | 定时任务调度中心 |
| `oasis/server.py` | 51202 | OASIS 论坛服务 |

> 端口可在 `config/.env` 中自定义。

### MCP 工具集

Agent 通过 MCP 协议集成 7 个工具服务，所有工具的 `username` 参数由系统自动注入，用户间完全隔离：

| 工具服务 | 能力 |
|----------|------|
| **搜索** | DuckDuckGo 联网搜索 |
| **定时任务** | 自然语言设置闹钟/提醒，Cron 表达式 |
| **文件管理** | 用户文件 CRUD，路径穿越防护 |
| **命令执行** | 安全沙箱中运行 Shell 命令和 Python 代码 |
| **OASIS 论坛** | 发起讨论、查看进展、管理自定义专家 |
| **Bark 推送** | 向 iOS/macOS 设备发送推送通知 |
| **Telegram** | 向 Telegram 发送消息、白名单管理 |

---

## 快速开始

### 一键运行（推荐）

```bash
# Linux / macOS
chmod +x run.sh
./run.sh

# Windows
run.bat
```

脚本自动完成：环境配置 → API Key 配置 → 创建用户 → 启动全部服务。

> 以下为手动分步操作说明，使用 `run.sh` / `run.bat` 可跳过。

### 手动配置

**1. 环境配置**

```bash
# 自动（推荐）
scripts/setup_env.sh   # Linux/macOS
scripts\setup_env.bat  # Windows

# 手动
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -r config/requirements.txt
```

**2. 配置 API Key**

在 `config/.env` 中设置：

```
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

**3. 创建用户**

```bash
scripts/adduser.sh     # Linux/macOS
scripts\adduser.bat    # Windows
```

**4. 启动服务**

```bash
# 一键启动
scripts/start.sh       # Linux/macOS
scripts\start.bat      # Windows

# 手动分别启动（3 个终端）
python src/time.py         # 定时调度
python src/mainagent.py    # Agent + MCP 工具
python src/front.py        # Web UI
```

启动后访问 http://127.0.0.1:51209 登录使用。

### 公网部署（可选）

通过 Cloudflare Tunnel 一键暴露到公网（详见[亮点 #3](#3-一键部署到公网)）：

```bash
python scripts/tunnel.py
# 或通过 run.sh 交互启动——提示"是否部署到公网？(y/N)"
```
自动下载 `cloudflared`，启动 Web UI + Bark 推送双隧道，捕获公网地址写入 `.env`，无需账户或 DNS 配置。

---

## API 参考

### OpenAI 兼容端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/v1/chat/completions` | POST | 聊天补全（流式/非流式），完全兼容 OpenAI 格式 |
| `/login` | POST | 用户登录认证 |
| `/sessions` | POST | 列出用户会话 |
| `/session_history` | POST | 获取会话历史 |

### OASIS 论坛端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/topics` | POST | 创建讨论话题 |
| `/topics` | GET | 列出所有话题 |
| `/topics/{id}` | GET | 获取话题详情 |
| `/topics/{id}/stream` | GET | SSE 实时更新流 |
| `/topics/{id}/conclusion` | GET | 阻塞等待讨论结论 |
| `/experts` | GET | 列出专家（公共 + 用户自定义） |
| `/experts/user` | POST/PUT/DELETE | 用户自定义专家 CRUD |

---

## 认证机制

- **密码存储**：仅存 SHA-256 哈希值，明文不落盘
- **会话管理**：Flask 签名 Cookie，`sessionStorage` 关闭标签页即失效
- **请求验证**：每次 `/ask` 都重新验证密码
- **内部鉴权**：服务间通信通过 `INTERNAL_TOKEN`（自动生成 64 字符 hex）
- **用户隔离**：对话记忆、文件存储、自定义专家均按 `user_id` 隔离

---

## 项目结构

```
mini_timebot/
├── run.sh / run.bat               # 一键运行
├── scripts/                       # 环境配置、启动、隧道、用户管理脚本
├── packaging/                     # Windows exe / macOS DMG 打包
├── chatbot/                       # 外部 Bot 服务
│   ├── telegrambot.py             # Telegram Bot（文字/图片/语音）
│   ├── QQbot.py                   # QQ Bot（私聊/群聊，SILK 转码）
│   └── setup.py                   # Bot 配置助手
├── config/
│   ├── .env                       # API Key 等环境变量
│   ├── requirements.txt           # Python 依赖
│   └── users.json                 # 用户名-密码哈希
├── data/
│   ├── agent_memory.db            # 对话记忆（SQLite）
│   ├── telegram_whitelist.json    # Telegram 机器人白名单
│   ├── prompts/                   # 系统提示词 + 专家配置
│   │   ├── oasis_experts.json     # 10 位公共专家定义
│   │   ├── oasis_expert_discuss.txt  # 专家讨论 prompt 模板
│   │   └── oasis_summary.txt     # 结论生成 prompt 模板
│   ├── schedules/                 # YAML 调度示例
│   ├── oasis_user_experts/        # 用户自定义专家（per-user JSON）
│   ├── timeset/                   # 定时任务持久化
│   └── user_files/                # 用户文件（按用户隔离）
│       └── {用户名}/
│           ├── user_profile.txt   # 用户画像
│           ├── skills_manifest.json  # 用户技能
│           └── tg_chat_id.txt     # Telegram chat ID
├── src/
│   ├── mainagent.py               # OpenAI 兼容 API + Agent 核心
│   ├── agent.py                   # LangGraph 工作流 + 工具编排
│   ├── front.py                   # Flask Web UI
│   ├── time.py                    # 定时调度中心
│   └── mcp_*.py                   # 7 个 MCP 工具服务
├── oasis/
│   ├── server.py                  # OASIS FastAPI 服务
│   ├── engine.py                  # 讨论引擎（轮次 + 共识 + 结论）
│   ├── experts.py                 # 专家定义 + 用户专家存储
│   ├── scheduler.py               # YAML 调度解析与执行
│   ├── forum.py                   # 论坛数据结构
│   └── models.py                  # Pydantic 模型
├── tools/
│   └── gen_password.py            # 密码哈希生成
└── test/
    ├── chat.py                    # 命令行测试客户端
    └── view_history.py            # 查看历史聊天记录
```

## 技术栈

| 层面 | 技术 |
|------|------|
| LLM | DeepSeek (`deepseek-chat`) |
| Agent 框架 | LangGraph + LangChain |
| 工具协议 | MCP (Model Context Protocol) |
| 后端 | FastAPI + Flask |
| 认证 | SHA-256 哈希 + Flask Session |
| 定时调度 | APScheduler |
| 持久化 | SQLite (aiosqlite) |
| 前端 | Tailwind CSS + Marked.js + Highlight.js |

## 许可证

MIT License

---

## 🤖 Agent Autonomous Evolution
This repository features an active evolution branch: `agent-evolution-xinyuan`. 
Managed autonomously by the resident Agent (**Mini_timebot**), this branch is used for:
- Core logic optimization and self-healing.
- Implementation of new system-level skills.
- Continuous structural reorganization and entropy reduction.

*Human-AI Collaboration in progress.*
