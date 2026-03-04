---
name: remote-relay
description: Secure outbound-only relay for remote OpenClaw control — no exposed ports, no SSH, no Telegram.
homepage: https://github.com/openclaw/remote-relay
metadata:
  clawdbot:
    emoji: "🔒"
    requires:
      env: ["RELAY_URL", "NODE_ID", "AUTH_TOKEN"]
    primaryEnv: "AUTH_TOKEN"
    files: ["relayClient.ts", "config.ts", "capabilities.ts", "index.ts"]
---

# PrivateBridge

Enables secure remote communication between an OpenClaw instance and a relay server without exposing ports, requiring SSH, or relying on Telegram/Discord.

## Description

The PrivateBridge skill registers your local OpenClaw instance as a **managed remote node** on a relay network. Once connected, the node can receive prompts, execute workflows, report health, and be restarted — all through a secure, outbound-only WebSocket channel.

This skill replaces external messaging-based control layers such as Telegram or Discord with a native, secure relay channel for OpenClaw interaction.

## Node Lifecycle

When the skill is enabled, the OpenClaw instance registers as a remote-capable node with the relay and maintains an active session.

The node can be in one of three states:

| State | Description |
|---|---|
| **Online** | Authenticated and accepting relay commands |
| **Reconnecting** | Connection lost; auto-reconnecting with exponential backoff |
| **Offline** | Skill disabled or relay unreachable after max retries |

Relay commands are only accepted while the node is **authenticated and online**. Commands received during reconnection are discarded by the relay.

## Capabilities

| Capability | Description |
|---|---|
| `remote_chat` | Receive and execute prompts remotely, streaming tokens back in real time |
| `remote_status` | Report node health: uptime, active tasks, last error, connection state |
| `remote_restart` | Safely restart the OpenClaw process without manual intervention. Pending executions are cancelled and reported before restart occurs. |
| `remote_trigger` | Execute OpenClaw workflows/tasks triggered remotely |

Remote commands are limited to declared capabilities and cannot execute arbitrary system-level operations.

## Configuration

| Key | Required | Description |
|---|---|---|
| `relay_url` | ✅ | WebSocket URL of the relay server |
| `node_id` | ✅ | Unique identifier for this OpenClaw node |
| `auth_token` | ✅ | Secret token for authenticating with the relay |

## Message Protocol

### Incoming (Relay → Node)

| `type` | Action |
|---|---|
| `prompt` | Execute via OpenClaw prompt runner, stream response tokens back |
| `status` | Return node health payload |
| `restart` | Cancel pending tasks, report them, then gracefully restart |
| `workflow` | Execute a named OpenClaw task/workflow |

### Outgoing (Node → Relay)

- **Heartbeat** (every 15s):
  ```json
  { "node_id": "...", "uptime": 3600, "active_tasks": 2, "last_error": null, "connection_state": "online" }
  ```
- **Response stream**: `{ "type": "token", "request_id": "...", "content": "..." }` per token
- **Response complete**: `{ "type": "done", "request_id": "..." }`
- **Status**: Full heartbeat payload with `request_id`

## External Endpoints

| Endpoint | Protocol | Data Sent | Data Received |
|---|---|---|---|
| `wss://<relay_url>/connect` | WebSocket (TLS) | `auth_token`, `node_id`, heartbeat payloads, prompt response tokens | Relay commands: `prompt`, `status`, `restart`, `workflow` |

No other external endpoints are contacted. All network activity is limited to the configured `relay_url`.

## Security & Privacy

### What leaves your machine

- **`auth_token`** — sent once during the WebSocket handshake to authenticate the node
- **`node_id`** — sent with every heartbeat and response to identify the node
- **Heartbeat data** — uptime (seconds), active task count, last error string, connection state
- **Prompt response tokens** — streamed back to the relay in response to `prompt` commands
- **Workflow completion status** — success/error for triggered workflows

### What stays on your machine

- All local AI model execution and inference
- Local file system contents — never read or transmitted
- Environment variables (other than the three declared above)
- System information, IP addresses, or hardware details — never collected

### Network posture

- **Outbound only** — the skill never opens a listening port or accepts inbound connections
- **TLS encrypted** — all WebSocket connections use `wss://` (TLS 1.2+)
- **No data persistence** — the relay server does not store prompt content or response tokens; it forwards in real time

## Trust Statement

> **By installing this skill, you are connecting your OpenClaw instance to an external relay server at the configured `relay_url`.** Prompt content and response tokens are transmitted through this relay in real time. Only install this skill if you trust the operator of the relay server. The default relay (`wss://relay-terminal-cloud.fly.dev`) is operated by the project maintainers.

## Operational Guarantees

- **Local AI execution continues** even if the relay disconnects
- **Relay does not expose the node** to inbound traffic
- **Remote actions are capability-scoped** — only declared capabilities can be invoked
- **Pending tasks are reported** before any restart occurs — no silent failures

## Installation

**Easiest way — use the visual setup wizard:**

👉 Open your dashboard and go to **[/skill/remote-relay](/skill/remote-relay)** to configure everything through the UI — generate a node ID, test your connection, and export your config in one place.

**Or configure manually:**

1. Add the skill to your OpenClaw instance
2. Configure `relay_url`, `node_id`, and `auth_token`
3. Start OpenClaw — the relay connection is established automatically

## Intended Use

This skill replaces external messaging-based control layers such as Telegram or Discord with a native, secure relay channel for OpenClaw interaction. It is designed for teams and individuals who need reliable remote access to their OpenClaw nodes without exposing infrastructure.
