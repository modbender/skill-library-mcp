# OpenClaw Architecture Overview

## What Is OpenClaw?

OpenClaw is an AI agent platform that connects LLMs to chat channels (Telegram, Discord, WhatsApp, Slack) with a persistent workspace, tool access, memory, and scheduling. It runs as a **Gateway** daemon that manages sessions, routes messages, and orchestrates agent capabilities.

## Core Components

### 1. Gateway (WebSocket Server)
The heart of OpenClaw. A Node.js daemon that:
- Listens for incoming messages from chat channels
- Manages agent sessions (creation, context, compaction)
- Routes tool calls (exec, browser, file I/O, web search)
- Handles cron job scheduling
- Serves the Control UI dashboard
- Exposes health/status APIs

**Commands:**
```bash
openclaw gateway start    # Start as background service
openclaw gateway stop     # Stop the service
openclaw gateway restart  # Restart
openclaw gateway status   # Check if running
openclaw health           # Quick health ping
openclaw doctor           # Full diagnostic
```

### 2. Agent Sessions
Each conversation creates a session with:
- **Context window** — accumulated messages + tool results
- **Model routing** — primary model + fallback chain
- **Memory search** — auto-searches MEMORY.md and memory/*.md files
- **Compaction** — when context gets too large, summarizes and continues
- **Subagents** — child sessions for parallel work (up to maxConcurrent)

Session lifecycle:
```
Message in → Channel plugin → Gateway → Create/resume session → 
Model inference → Tool calls → Response → Channel plugin → Message out
```

### 3. Channels (Chat Plugins)
Bidirectional bridges between chat platforms and the Gateway:
- **Telegram** — Bot API with streaming support
- **Discord** — Bot with slash commands
- **WhatsApp** — Web session bridge
- **Slack** — Bot with workspace access

Each channel has its own config in `openclaw.json` under `channels.*`.

### 4. Workspace
The agent's persistent filesystem at `~/.openclaw/workspace/`:
```
workspace/
├── AGENTS.md          # System architecture rules (loaded every session)
├── MEMORY.md          # Long-term memory (loaded in main sessions)
├── SOUL.md            # Identity/personality (loaded every session)
├── TOOLS.md           # API notes and cheat sheets (loaded every session)
├── memory/            # Daily logs, auto-searched by memory system
├── skills/            # Installed skills (SKILL.md + scripts/)
├── tools/             # Custom scripts and utilities
├── data/              # Persistent data files
└── .env               # Environment variables
```

### 5. Skills System
Skills are knowledge + tools bundles in `skills/<name>/`:
- `SKILL.md` — Frontmatter metadata + usage docs (loaded into context when relevant)
- `scripts/` — Executable scripts the agent can run
- `references/` — Additional reference docs

Skills are auto-discovered and can be published to ClawHub.

### 6. Memory System
Multi-layer memory:
- **MEMORY.md** — Core long-term knowledge, always loaded
- **memory/*.md** — Daily/topical files, searched on demand
- **Memory search** — Embedding-based search across all memory files
- **Compaction flush** — Before context compaction, important info is saved to memory

### 7. Cron Scheduler
Built-in cron for recurring tasks:
- Fires at specified schedules (cron syntax)
- Delivers as agent messages or system events
- Can target specific channels/users

### 8. Tool System
Tools available to the agent:
- **exec** — Shell commands with background support
- **browser** — Playwright-based browser automation
- **web_search** — Perplexity/Brave search
- **web_fetch** — URL content extraction
- **message** — Send messages via channels
- **nodes** — Control paired devices (phones, other servers)
- **canvas** — Present web UI to users
- **subagents** — Spawn parallel agent sessions
- **tts** — Text to speech

## Data Flow

```
User (Telegram/Discord/etc)
    ↓
Channel Plugin (parse, format)
    ↓
Gateway (route, session mgmt)
    ↓
Agent Session (model inference)
    ↓ ↑
Tool Calls ←→ Results
    ↓
Response → Channel Plugin → User
```

## Deployment Models

### Docker (Recommended)
```yaml
# docker-compose.yml
services:
  openclaw:
    image: openclaw/openclaw:latest
    volumes:
      - ./workspace:/home/node/.openclaw/workspace
      - ./openclaw.json:/home/node/.openclaw/openclaw.json
    ports:
      - "18789:18789"  # Gateway
```

### Local (Node.js)
```bash
npm install -g openclaw
openclaw setup
openclaw gateway start
```

## Key Ports
- **18789** — Gateway WebSocket + HTTP (default)
- **18790** — Browser automation (Playwright)
- **18791** — Canvas server

## Authentication
- **Gateway auth** — Token-based (`gateway.auth.token` in config)
- **Tailscale auth** — Allow connections from Tailscale network
- **Channel auth** — Per-channel allowlists (e.g., Telegram `allowFrom` user IDs)
