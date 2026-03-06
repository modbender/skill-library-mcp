---
name: fastclaw-relay
description: Connect your OpenClaw to the FastClaw iOS app. Relays messages between your local Gateway and FastClaw via Convex cloud sync. No port forwarding, no VPN — just pair and go.
---

# FastClaw Relay

Bridges your local OpenClaw Gateway to the FastClaw iOS app via Convex real-time sync.

## How It Works

```
OpenClaw Gateway (local)  ←WebSocket→  fastclaw-relay  ←Convex→  FastClaw App (iOS)
```

1. The relay connects to your local Gateway WebSocket as an operator client
2. Messages sync bidirectionally through Convex (cloud)
3. The FastClaw iOS app subscribes to Convex — works from anywhere

No network configuration needed. Both sides connect **outbound**.

## Setup

### 1. Install the skill

```bash
clawhub install fastclaw-relay
```

### 2. Start pairing

```bash
openclaw fastclaw pair
```

This displays a QR code containing your Convex deployment URL and a one-time pairing token.

### 3. Scan from FastClaw app

Open FastClaw → tap "Connect" → scan the QR code. Done.

## Configuration

The relay reads from environment or OpenClaw config:

- `FASTCLAW_CONVEX_URL` — Your Convex deployment URL (provisioned during setup)
- `FASTCLAW_INSTANCE_ID` — Unique ID for this OpenClaw instance (auto-generated)

These are stored in `~/.openclaw/fastclaw/config.json` after first pairing.

## Architecture

### Convex Schema

The relay uses these Convex tables:

- **instances** — Registered OpenClaw instances (id, name, status, lastSeen)
- **sessions** — Chat sessions synced from Gateway
- **messages** — Individual messages (synced bidirectionally)
- **pairingCodes** — One-time codes for QR pairing (expire after 5 min)

### Gateway Connection

The relay connects to the local Gateway WebSocket (`ws://127.0.0.1:18789`) using the configured gateway token. It operates as an `operator` role client with `operator.read` and `operator.write` scopes.

### Message Flow

**User sends from FastClaw app:**
1. App writes message to Convex `messages` table
2. Relay receives real-time update via Convex subscription
3. Relay forwards message to Gateway WebSocket
4. Gateway processes and responds
5. Relay captures response and writes to Convex
6. App receives response in real-time

**Incoming messages (WhatsApp, Telegram, etc.):**
1. Gateway receives message on any channel
2. Relay observes session updates via Gateway WebSocket
3. Relay syncs new messages to Convex
4. App displays them in real-time

## Security

- Pairing codes expire after 5 minutes
- All Convex communication is over TLS
- Instance tokens are stored locally in `~/.openclaw/fastclaw/`
- The relay only syncs message content — no API keys, tokens, or config
- Gateway token never leaves the local machine
- Open source for full auditability

## Troubleshooting

### Relay not connecting
- Check Gateway is running: `openclaw gateway status`
- Verify gateway token matches: check `~/.openclaw/config.yaml`

### Messages not syncing
- Check relay process: `openclaw fastclaw status`
- Verify Convex deployment: `npx convex dashboard`

### Re-pairing
- Run `openclaw fastclaw pair --reset` to generate a new pairing code
