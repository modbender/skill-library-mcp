---
name: quantumos
description: Install and manage QuantumOS, an AI command center dashboard for OpenClaw. Use when the user wants to set up QuantumOS, start/stop the dashboard, troubleshoot it, or update it. Provides a real-time chat UI, Mission Control (kanban task management with AI agents), and a feed dashboard (Reddit, HN, X, news).
---

# QuantumOS

AI command center dashboard for OpenClaw. Next.js app that connects to the gateway via WebSocket.

## Install

Run the setup script, then configure agent integration. Both steps are required.

### Step 1: Run setup

```bash
bash "SKILL_DIR/scripts/setup.sh"
```

The script clones the repo, installs deps, auto-detects gateway token, and creates data directories.

If the user doesn't have Node.js 20+, tell them to install it first: https://nodejs.org

### Step 2: Configure agent integration

After setup, you MUST add Mission Control triage to your workspace's `HEARTBEAT.md`. Append the following block (do not overwrite existing content):

```
## Check for new Mission Control tasks
- GET http://localhost:3005/api/mission-control/tasks
- Look for tasks with status "inbox"
- For each inbox task: generate a proper title, set status to "in_progress", and start working on it
- After completing a task: add a comment documenting what was done, set status to "done"
```

This enables automatic task triage when users create tasks from the dashboard.

## Start

```bash
cd ~/Projects/quantumos && npm run dev
```

Dashboard will be at **http://localhost:3005**

On first open, the user needs to enter their OpenClaw gateway token in the settings panel. They can find it in `~/.openclaw/openclaw.json` under `gateway.token`.

## Stop

Kill the dev server process (Ctrl+C in the terminal running it).

For background operation:

```bash
cd ~/Projects/quantumos && nohup npm run dev > /tmp/quantumos.log 2>&1 &
```

## Update

```bash
cd ~/Projects/quantumos && git pull && npm install
```

Then restart the dev server.

## Troubleshooting

- **Blank page / won't connect**: Check that OpenClaw gateway is running (`openclaw gateway status`). Verify the gateway token in dashboard settings matches `~/.openclaw/openclaw.json`.
- **Port conflict**: Change port in `package.json` scripts.dev (`--port 3005`).
- **Feeds not loading**: Run `python3 scripts/fetch-dashboard-feeds.py` from the quantumos directory. Requires Python 3.8+.

## API Keys

- **X/Twitter feeds** require an xAI API key. Get one at [console.x.ai](https://console.x.ai). Add `XAI_API_KEY=your-key` to `.env.local` or set it as an environment variable. Without it, X feeds are gracefully skipped.

## Features Overview

- **Chat**: Real-time WebSocket chat with the OpenClaw gateway, streaming responses, thinking blocks, tool call display
- **Mission Control**: Kanban board with task creation, agent assignment, comments, status tracking
- **Dashboard**: Aggregated feeds from Reddit, Hacker News, X, and news with archiving
- **Agent Settings**: Configure agents, models, tools directly from the UI
