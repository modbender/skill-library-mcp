# openclaw-ops

[English](README.md) | [中文](README_CN.md)

A skill that teaches any AI agent how to operate and maintain an [OpenClaw](https://openclaw.ai) Gateway running as a persistent service.

Works with **any agent that has shell access** — Claude Code, Codex, OpenClaw, Pi, or any AI agent with shell access running on the same machine as the OpenClaw Gateway.

Supports both **Linux (systemd)** and **macOS (launchd)**.

## Install

> **⚠️ Install this skill on your rescue agent (Claude Code, secondary OpenClaw, etc.), NOT on the main OpenClaw Gateway you want to maintain.**

### Ask your agent to install it

Just tell your rescue agent in a conversation:

```
> Install the openclaw-ops skill from https://github.com/dinstein/openclaw-ops-skill
```

The agent will download `SKILL.md` and place it in the correct skills directory automatically.

### From ClawHub (when using a secondary OpenClaw as rescue agent)

```bash
clawhub install openclaw-ops
```

### Manual

Copy `SKILL.md` into your agent's skills directory:

```bash
# Claude Code
mkdir -p ~/.claude/skills/openclaw-ops
cp SKILL.md ~/.claude/skills/openclaw-ops/SKILL.md

# OpenClaw
mkdir -p ~/.openclaw/workspace/skills/openclaw-ops
cp SKILL.md ~/.openclaw/workspace/skills/openclaw-ops/SKILL.md

# Other agents — place in whatever skills directory your agent reads from
```

## Architecture

```mermaid
graph LR
    You["👤 You"] -->|remote access| Rescue["🛠️ Rescue Agent<br/>+ openclaw-ops skill"]
    Rescue -->|diagnoses & fixes| Main["🦞 Main OpenClaw<br/>Gateway"]
    Main -->|serves users| Users["👥 Discord / Telegram / etc"]
```

**Main OpenClaw Gateway** — Your primary AI agent system. Handles all day-to-day operations: chat channels, cron jobs, sessions, etc.

**Rescue Agent** — A separate agent (Claude Code, secondary OpenClaw instance, or any AI agent with shell access) with this skill installed. Lives on the same machine. Its sole purpose: fix the main gateway when it breaks, and perform operational health checks.

**This skill** — Teaches the rescue agent what commands to run, how to interpret output, and what steps to follow for diagnosis and repair.

## Two Core Scenarios

### 🔴 Rescue: Main Gateway is Down

The main OpenClaw is crashed, misconfigured, or won't start. You connect to the rescue agent and ask it to fix things.

**Example 1: Won't start after config edit**
```
You: "I edited openclaw.json and now it won't start"

Rescue agent: validates JSON → finds trailing comma on line 47 →
backs up file → fixes syntax → restarts gateway → verifies health
```

**Example 2: Broken after upgrade**
```
You: "I upgraded OpenClaw and now the gateway keeps crashing"

Rescue agent: checks crash logs → finds MODULE_NOT_FOUND for a removed plugin →
reinstalls dependencies → restarts → still failing →
rolls back to previous version → gateway is back online
```

### 🟢 Health Check: Main Gateway is Running

The main OpenClaw is working fine, but you want to verify health, update, or clean up.

```
You: "Run a health check on OpenClaw"

Rescue agent: runs openclaw doctor → reports status, orphan count,
channel connectivity, disk usage → offers to fix any issues found
```

## Connecting to the Rescue Agent

When the main OpenClaw is down, you can't talk to it through Discord/Telegram. You need an alternative way to reach the rescue agent on the server.

### Option 1: Native Remote Control (⭐ Recommended)

If your agent supports native remote access, use it — the most seamless experience with full agent capabilities from your browser or mobile device.

- **Claude Code** — [Remote Control](https://code.claude.com/docs/en/remote-control): access your server-side Claude Code from any browser, with built-in auth and session persistence

Currently only Claude Code offers this. As more agents add native remote access, this will be the preferred approach for all.

### Option 2: Remote Agent Platforms

Third-party platforms that let you manage and interact with coding agents on remote machines:

- [Happy](https://github.com/slopus/happy) — Mobile & web client for Claude Code and Codex with push notifications, device switching, and E2E encryption
- [Hapi](https://github.com/tiann/hapi) — Local-first remote control for Claude Code / Codex / Gemini / OpenCode via Web, PWA, or Telegram Mini App
- Similar products that support remote shell-capable agent access

These are good when your agent doesn't have native remote control, or when you want a unified dashboard for multiple agents.

### Option 3: SSH + Agent CLI

SSH into the server and run the agent directly in the terminal:

```bash
ssh user@your-server
claude  # or codex, or any agent CLI
```

**Tips for mobile:**
- Use SSH client apps (Termius, Blink, etc.) from your phone
- Use tmux to keep sessions alive between connections:

```bash
# On the server (one-time setup)
tmux new -s rescue
claude

# Later, from anywhere
ssh user@your-server
tmux attach -t rescue
```

- VS Code Remote SSH also works well from a laptop

## What it covers

| Module | Scenario | Description |
|--------|----------|-------------|
| Crash diagnosis | 🔴 Rescue | Read logs, identify root cause |
| Config repair | 🔴 Rescue | JSON fix, schema validation, common errors |
| Service restart | 🔴 Rescue | Safe restart after fixing root cause |
| Resource check | 🔴 Rescue | Disk, memory, Node.js, dependencies |
| Health check | 🟢 Health | `openclaw doctor`, service status |
| Update & upgrade | 🟢 Health | Version check, safe upgrade, rollback |
| Disk cleanup | 🟢 Health | Orphan transcripts, session management |
| Backup | 🟢 Health | Config, agents, workspace backup |
| Tailscale check | 🟢 Health | Reverse proxy verification |

## Requirements

The rescue agent needs:

- **Shell access** on the same machine as the OpenClaw Gateway
- **Read/write access** to `~/.openclaw/` (config, agents, sessions)
- **Node.js 18+** and npm (for the `openclaw` CLI)
- **Optional:** Tailscale CLI (for reverse proxy troubleshooting)

### Security considerations

This skill instructs the agent to:
- Read and modify OpenClaw config files (always with backup first)
- Access env files containing tokens (but **never print them**)
- Restart system services (systemd / launchd)
- Delete old session transcripts (only with user confirmation)

All destructive operations require explicit user approval.

## How it works

This is a **pure documentation skill** — no scripts, no external dependencies, no framework lock-in. Install it in any agent that can read markdown and run shell commands. It teaches the agent:

1. **What to check** — the right commands for each situation
2. **How to interpret** — what the output means and common error patterns
3. **What to do** — step-by-step fix procedures with safety guardrails
4. **How to verify** — confirmation steps after every action

## Safety

The skill enforces these rules:

- Always check logs before making changes
- Always backup config before editing
- Always validate JSON after editing
- Never print secrets (env files)
- Never delete workspace files without confirmation
- Always verify after restart

## License

MIT
