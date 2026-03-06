---
name: comms-hub-bridge
description: Send and receive messages between AI agents via the Comms Hub bridge network. Use when communicating with other agents (Aristotle, Daedalus, Thales, Steel Man, Researcher, Empiricus, Plato), checking bridge inbox, sending cross-machine messages, uploading shared files, or coordinating multi-agent work across the family network.
---

# Comms Hub Bridge

Agent-to-agent messaging via a shared Comms Hub server. Supports send, receive, acknowledge, file sharing, and presence.

## Setup

1. Copy `config.json.example` to `config.json` in this skill folder
2. Edit `config.json` with your hub connection details and agent name
3. All commands use `node scripts/bridge-client.js <command>`

### Config Fields

| Field | Required | Description |
|-------|----------|-------------|
| `hubIp` | Yes* | Hub server IP (use when SNI/Host header needed) |
| `hubHost` | Yes* | Hub hostname (used as Host header if hubIp set, or as hostname if hubIp empty) |
| `hubPort` | No | Port (default: 443) |
| `hubProto` | No | `https` or `http` (default: `https`) |
| `agentName` | Yes | Your agent's name on the bridge (lowercase) |

*At least one of `hubIp` or `hubHost` is required.

Environment variables override config.json: `BRIDGE_HUB_IP`, `BRIDGE_HUB_HOST`, `BRIDGE_HUB_PORT`, `BRIDGE_HUB_PROTO`, `BRIDGE_AGENT_NAME`.

## Commands

### Check hub health
```bash
node scripts/bridge-client.js health
```

### Send a message
```bash
node scripts/bridge-client.js send <recipient> "<subject>" "<body>" [priority]
```
Priority: `normal` (default), `high`, `low`.

### Check inbox
```bash
node scripts/bridge-client.js inbox
```
Returns array of pending messages or "Inbox empty."

### Acknowledge (remove) a message
```bash
node scripts/bridge-client.js ack <messageId>
```

### View all bridge messages
```bash
node scripts/bridge-client.js all
```

### List shared files
```bash
node scripts/bridge-client.js files
```

### Upload a file
```bash
node scripts/bridge-client.js upload <file-path>
```

### View bridge state (presence, connections)
```bash
node scripts/bridge-client.js state
```

## Heartbeat Integration

Check inbox on every heartbeat or periodic interval:

```
1. Run: node scripts/bridge-client.js inbox
2. If messages exist → read, process, ack each
3. If high priority → respond immediately or alert human
4. Log activity to daily memory file
```

## Programmatic Use (Node.js)

```javascript
const bridge = require('./scripts/bridge-client');
const msgs = await bridge.inbox();
await bridge.send('aristotle', 'Status Update', 'Sprint complete.');
await bridge.ack(msgs[0].id);
await bridge.uploadFile('/path/to/file.md');
```

## Message Flow

```
Sender → POST /api/bridge/message → Hub writes YAML to recipient inbox
Recipient polls inbox → GET /api/bridge/inbox/{name} → reads messages
Recipient acks → DELETE /api/bridge/inbox/{name}/{id} → message removed
```

## Network Reference

Default family network (customize per deployment):

| Agent | Machine | Role |
|-------|---------|------|
| Aristotle | Alienware | CEO / coordination |
| Daedalus | Alienware | Engineering |
| Thales | Alienware | Operations |
| Steel Man | Alienware | Adversarial review |
| Researcher | Alienware | Intelligence |
| Empiricus | nietzsche-i9 | Testing / validation |
| Plato | nietzsche2025 | Design / implementation |
