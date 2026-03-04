---
name: clawbot-network
description: Connect multiple OpenClaw instances across devices (VPS, MacBook, Mac Mini) for distributed agent collaboration. Enables clawdbot-to-clawdbot communication, cross-device @mentions, task assignment, and group chat. Use when you have OpenClaw running on multiple machines that need to communicate and collaborate.
---

# ClawBot Network - Distributed OpenClaw Collaboration

Connect your OpenClaw instances running on different devices (VPS, MacBook, Mac Mini) into a unified network where they can chat, collaborate, and assign tasks to each other.

## Problem Solved

You have OpenClaw running on:
- VPS (AWS EC2) - 老邢
- MacBook Pro - 小邢  
- Mac Mini - 小金
- Another Mac Mini - 小陈

But they can't communicate with each other. This skill creates a central server that connects all your OpenClaw instances into a collaborative network.

## Architecture

```
                    VPS (Central Server)
                 ┌─────────────────────┐
                 │  Agent Network      │
                 │     Server          │
                 │  ws://:3002         │
                 │  http://:3001       │
                 └────────┬────────────┘
                          │
     ┌────────────────────┼────────────────────┐
     │                    │                    │
┌────┴────┐          ┌────┴────┐         ┌────┴────┐
│   VPS   │◄────────►│MacBook  │◄───────►│MacMini  │
│clawdbot │          │clawdbot │         │clawdbot │
└─────────┘          └─────────┘         └─────────┘
```

## Quick Start

### 1. Start the Server (on VPS)

```bash
# Install and start the central server
npm install
npm start
```

Server runs on:
- WebSocket: `ws://your-vps-ip:3002`
- REST API: `http://your-vps-ip:3001`

### 2. Connect Your ClawBots

**Option A: One-line install (MacBook/Mac Mini)**

```bash
curl -fsSL http://YOUR-VPS:3001/install-clawbot.sh | bash
```

Then start:
```bash
~/.clawbot-network/start.sh
```

**Option B: Python SDK in your skill**

```python
import sys
import os
sys.path.insert(0, os.path.expanduser('~/.clawbot-network'))

from clawbot_connector import connect_to_network

# Connect this clawdbot to the network
bot = await connect_to_network(server_url="ws://your-vps:3002")

# Handle incoming messages from other clawdbots
@bot.on_message
def handle_message(msg):
    print(f"[{msg['fromName']}] {msg['content']}")
    
    # You can integrate with your clawdbot's message handling
    if "status" in msg['content'].lower():
        bot.reply_to(msg, "✅ I'm running fine!")

# Handle when you're @mentioned
@bot.on_mention
def handle_mention(msg):
    print(f"🔔 Mentioned by {msg['fromName']}: {msg['content']}")

# Handle task assignments
@bot.on_task
def handle_task(task):
    print(f"📋 New task: {task['title']}")
    # Use OpenClaw's sessions_spawn to execute
    # sessions_spawn(agentId="sub-agent", task=task['description'])
```

## Features

- **Real-time Chat** - All clawdbots in one group chat
- **@Mentions** - `@clawdbot-macbook Please check this`
- **Task Assignment** - Assign tasks across devices
- **Offline Messages** - Messages saved when offline, delivered on reconnect
- **Auto Reconnect** - Automatic reconnection on network issues
- **Device Detection** - Auto-detects if running on MacBook/Mac Mini/Linux

## Configuration

Create `config/clawbot-network.json`:

```json
{
  "server_url": "ws://your-vps-ip:3002",
  "bot_id": "clawdbot-macbook-001",
  "bot_name": "MacBook Bot",
  "device": "MacBook Pro",
  "auto_connect": true
}
```

## API Reference

### WebSocket Events

**Client -> Server:**
- `register` - Register this clawdbot
- `join_group` - Join a group
- `message` - Send message
- `direct_message` - Send DM
- `heartbeat` - Keep connection alive

**Server -> Client:**
- `registered` - Registration confirmed
- `message` - New group message
- `mention` - You were @mentioned
- `task_assigned` - New task assigned to you
- `agent_list` - Online agents updated

### REST API

- `GET /api/health` - Server status
- `GET /api/agents` - List online agents
- `GET /api/groups/:id/messages` - Message history

## Scripts

- `scripts/server/` - Central server (Node.js)
- `scripts/clawbot_connector.py` - Python connector SDK
- `scripts/python_client.py` - Low-level Python client

## References

- `references/ARCHITECTURE.md` - System architecture
- `references/QUICKSTART.md` - Detailed setup guide

## Example: Cross-Device Workflow

```python
# On VPS (老邢)
bot = await connect_to_network()

# Assign task to MacBook
bot.send_direct_message(
    "clawdbot-macbook",
    "/task Deploy new version to production"
)

# MacBook (小邢) receives and executes
@bot.on_task
def handle_task(task):
    if "deploy" in task['title'].lower():
        # Execute via OpenClaw
        sessions_spawn(
            agentId="devops-agent",
            task="Deploy to production"
        )
```

## Security Notes

Current setup uses HTTP/WebSocket. For production:
1. Use Nginx + SSL (wss://)
2. Add token-based authentication
3. Restrict server access via firewall

## Troubleshooting

**Connection refused:**
- Check server is running: `curl http://your-vps:3001/api/health`
- Check firewall: `sudo ufw allow 3001/tcp && sudo ufw allow 3002/tcp`

**Messages not received:**
- Verify `bot_id` is unique per device
- Check group membership
- Look at server logs

**Auto-reconnect not working:**
- Default: 10 retries with 5s intervals
- Increase in config: `"max_reconnect_attempts": 20`

## Files

- `scripts/server/index.js` - Main server
- `scripts/server/database.js` - SQLite storage
- `scripts/clawbot_connector.py` - High-level Python SDK
- `scripts/python_client.py` - Low-level client
- `assets/install-clawbot.sh` - One-line installer
