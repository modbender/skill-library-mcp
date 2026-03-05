# 🔒 PrivaClaw

[![ClawHub](https://img.shields.io/badge/ClawHub-privaclaw-blue)](https://clawhub.ai/skills/privaclaw)
[![Version](https://img.shields.io/badge/version-1.0.1-green)](https://github.com/openclaw/privaclaw)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Secure outbound-only relay for remote OpenClaw control — no exposed ports, no SSH, no Telegram.**

## What It Does

Connects your OpenClaw instance to a relay server over a single outbound WebSocket connection. Once connected, you can remotely:

- 💬 **Send prompts** and stream responses in real time
- 📊 **Check health** — uptime, active tasks, last error
- 🔄 **Restart** the OpenClaw process gracefully
- ⚡ **Trigger workflows** by name with parameters

All without opening ports, configuring firewalls, or setting up SSH tunnels.

## Installation

```bash
openclaw skill install privaclaw
```

Or install from ClawHub:

```bash
clawhub install privaclaw
```

## Configuration

Set these environment variables or add them to your OpenClaw config:

| Variable | Required | Description |
|---|---|---|
| `RELAY_URL` | ✅ | WebSocket URL of the relay server (e.g. `wss://relay.privaclaw.com`) |
| `NODE_ID` | ✅ | Unique identifier for this node (typically your device ID) |
| `AUTH_TOKEN` | ✅ | Secret token for relay authentication (your device token) |

### Example config

```json
{
  "relay_url": "wss://relay.privaclaw.com",
  "node_id": "my-server-01",
  "auth_token": "your-device-token-here"
}
```

## How It Works

```
┌──────────────┐         outbound WSS         ┌──────────────┐
│  Your Server │ ──────────────────────────▶  │ Relay Server │
│  (OpenClaw)  │ ◀────────────────────────── │              │
│              │    commands / responses       │              │
└──────────────┘                               └──────────────┘
        │                                             │
        │  local AI execution                         │  dashboard / API
        │  stays on your machine                      │  for remote control
        ▼                                             ▼
```

1. OpenClaw opens an **outbound** WebSocket to the relay
2. Authenticates with `auth_token` and `node_id`
3. Sends heartbeats every 15 seconds
4. Receives and executes relay commands (`prompt`, `status`, `restart`, `workflow`)
5. Auto-reconnects with exponential backoff on disconnection

## Capabilities

| Capability | Description |
|---|---|
| `remote_chat` | Execute prompts remotely, stream tokens back |
| `remote_status` | Report node health and connection state |
| `remote_restart` | Gracefully restart with pending task reporting |
| `remote_trigger` | Execute named workflows/tasks |

## Security

- **Outbound only** — never opens a listening port
- **TLS encrypted** — all connections use `wss://`
- **Capability-scoped** — only declared capabilities can be invoked remotely
- **No data persistence** — relay forwards in real time, does not store content
- **Local execution continues** during disconnection

See [SKILL.md](./SKILL.md) for the full security & privacy disclosure.

## Requirements

- OpenClaw v1.0+
- A running relay server (default: `wss://relay.privaclaw.com`)
- Network access to the relay URL (outbound port 443)

## Troubleshooting

| Problem | Solution |
|---|---|
| Connection refused | Verify `RELAY_URL` is correct and reachable |
| Auth failed | Check `AUTH_TOKEN` matches your paired device token |
| Keeps reconnecting | Ensure the relay server is running and your network allows outbound WSS |
| Commands not executing | Verify the node is in **Online** state (check heartbeat logs) |

## License

MIT
