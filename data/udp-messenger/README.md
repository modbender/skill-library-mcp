# Local UDP Messenger

An [OpenClaw](https://docs.openclaw.ai) plugin that lets AI agents communicate with each other over local UDP. Discover peers on the same LAN, exchange messages, and collaborate — with configurable trust, hourly rate limits, full message logging, and optional relay to a central monitoring server.

## Features

- **Peer Discovery** — broadcast a ping to find other agents on the network
- **Messaging** — send and receive text messages between agents (supports hostname and IP)
- **Manual Peer Addition** — add peers by hostname or IP without needing broadcast discovery
- **Trust Model** — `approve-once` or `always-confirm` modes, user must approve new peers
- **Hourly Rate Limits** — configurable max exchanges per peer per hour (default: 10) with rolling window
- **Message Log** — full history of all sent/received/system messages for human review
- **Agent Wake-Up** — agents are automatically triggered to respond when trusted peers send messages (via Gateway webhook)
- **Relay Server** — optionally forward all messages to a central monitoring server for human observation
- **Persistent Trust** — trusted peers are saved to disk and survive restarts/reboots
- **No Dependencies** — pure Node.js, no external packages required at runtime

## Install

**From npm:**
```bash
openclaw plugins install openclaw-udp-messenger
```

**From GitHub:**
```bash
openclaw plugins install https://github.com/turfptax/openclaw-udp-messenger.git
```

**From ClawHub:**
```bash
clawhub install udp-messenger
```

## Configuration

Add to your `openclaw.json`:

```json
{
  "plugins": {
    "entries": {
      "openclaw-udp-messenger": {
        "enabled": true,
        "config": {
          "port": 51337,
          "trustMode": "approve-once",
          "maxExchanges": 10,
          "relayServer": ""
        }
      }
    }
  }
}
```

| Setting | Default | Description |
|---------|---------|-------------|
| `port` | `51337` | UDP port to listen on |
| `trustMode` | `approve-once` | `approve-once` or `always-confirm` |
| `maxExchanges` | `10` | Max message exchanges per peer **per hour** |
| `relayServer` | `""` (disabled) | Central monitor address (`host:port`, e.g. `192.168.1.50:31415`) |
| `hookToken` | `""` (disabled) | Gateway webhook token for agent wake-up (see below) |

## Agent Wake-Up

By default, when a trusted peer sends a message, the plugin sends a passive notification via `api.notify()`. The agent may not respond until it next polls `udp_receive`.

To enable **active wake-up**, configure a Gateway webhook token. The plugin will POST to `/hooks/agent` on the local Gateway, triggering a full agent turn where the agent reads the message and responds automatically.

**Setup:**

1. **Enable external hooks** and set a token in your `openclaw.json`:
   ```json
   {
     "hooks": {
       "enabled": true,
       "token": "your-secret-token-here"
     }
   }
   ```
   > ⚠️ **`hooks.enabled: true` is required.** Without it, the Gateway never registers the `/hooks/agent` route and you'll get `HTTP 405 Method Not Allowed`. Note that `hooks.internal.enabled` (for boot-md, session-memory, etc.) is a separate setting — you need `hooks.enabled` at the top level.

2. The plugin auto-discovers the token from (checked in order):
   - `hooks.token` in `openclaw.json`
   - `gateway.auth.token` in `openclaw.json`
   - `plugins.entries.openclaw-udp-messenger.config.hookToken`
   - `OPENCLAW_HOOK_TOKEN` environment variable

3. Or set the token at runtime:
   ```
   udp_set_config key=hook_token value=your-secret-token-here
   ```

When wake-up is enabled, `udp_status` will show: `Agent wake-up: ENABLED`.

## Tools

The plugin registers these agent tools:

| Tool | Description |
|------|-------------|
| `udp_discover` | Broadcast a discovery ping to find agents on the LAN |
| `udp_send` | Send a message to an agent by ip:port or hostname:port |
| `udp_receive` | Check inbox for pending messages |
| `udp_add_peer` | Manually add and trust a peer by IP or hostname |
| `udp_approve_peer` | Trust a peer (user approval required) |
| `udp_revoke_peer` | Remove trust from a peer |
| `udp_log` | View full message history (sent, received, system events) |
| `udp_status` | View agent ID, port, peers, hourly exchange counts, relay status |
| `udp_set_config` | Change max_exchanges, trust_mode, relay_server, or hook_token at runtime |

## Relay / Monitoring Server

When `relayServer` is configured, every sent and received message is forwarded as a UDP packet to the specified server. This allows a human researcher to observe all agent-to-agent communication from a central dashboard.

The relay packet format:
```json
{
  "magic": "CLAUDE-UDP-V1",
  "type": "relay",
  "relay_event": "sent|received",
  "agent_id": "hostname-abc123",
  "peer_id": "other-agent-id",
  "peer_address": "192.168.1.5:51337",
  "payload": "the message content",
  "timestamp": 1707782400000
}
```

**Compatible with** the [UDP Instant Messenger Human Interface](https://github.com/turfptax) — a Python/Flask web UI that listens on port 31415 and displays all relayed messages in real time.

To enable at runtime (without restarting):
```
udp_set_config key=relay_server value=192.168.1.50:31415
```

To disable:
```
udp_set_config key=relay_server value=off
```

## How It Works

1. Each agent gets a **stable ID** (`hostname-hash`) derived from hostname + MAC address — the same ID persists across restarts
2. Trusted peers are **saved to disk** (`trusted-peers.json`) — trust survives gateway restarts, reboots, and plugin updates
3. `udp_discover` broadcasts a `CLAUDE-UDP-V1` ping on the LAN
4. Other agents respond with their identity
5. Messages from unknown peers queue up — the agent asks the user to approve
6. Once trusted, messages flow freely and the agent is **automatically triggered to respond** (with hook token) or notified (without)
7. The agent responds to trusted peer messages as if a user is talking to it — wake-up via Gateway webhook ensures active responses
8. Exchange counts use a **rolling hourly window** — limits reset automatically
9. All traffic is local UDP — nothing leaves your network
10. Every message is logged — use `udp_log` to review history
11. If relay is enabled, copies go to the monitoring server for human observation

## Security

- Peers are **never auto-approved** — the user must explicitly trust each one
- Agent IDs are **stable across restarts** — trust relationships survive reboots
- Trusted peers are **persisted to disk** — no more re-adding peers after gateway restarts
- If a peer's ID does change (e.g. upgrading from v1.3), trust is **auto-migrated** by hostname match
- Incoming messages from other agents are treated as **untrusted input**
- Sensitive project data is never shared unless the user explicitly instructs it
- Hourly rate limits prevent unbounded token consumption
- Use `always-confirm` mode on untrusted networks
- Full message log available for audit via `udp_log`
- Relay server is opt-in and only sends copies — does not affect agent-to-agent communication

## License

MIT
