# FastClaw Relay — Architecture

## Overview

The relay is a Node.js process that bridges the local OpenClaw Gateway WebSocket
to Convex cloud, enabling the FastClaw iOS app to communicate with OpenClaw from anywhere.

## Components

### 1. Relay Process (`scripts/relay.mjs`)

Long-running Node.js script that:

1. **Connects to local Gateway WS** (`ws://127.0.0.1:18789`) as an operator client
2. **Connects to Convex** using the deployment URL + auth
3. **Syncs bidirectionally:**
   - Gateway → Convex: session list, new messages, status heartbeat
   - Convex → Gateway: user messages from FastClaw app

#### Gateway Connection
- Uses OpenClaw Gateway WS protocol v3
- Role: `operator` with scopes `["operator.read", "operator.write"]`
- Authenticates with the local gateway token
- Subscribes to session events and message events

#### Convex Connection
- Uses `convex` npm package (ConvexHttpClient or ConvexClient for subscriptions)
- Pushes gateway messages via `messages:pushFromGateway`
- Subscribes to `messages:getUnsyncedFromApp` for app→gateway messages
- Sends heartbeat every 30s via `sessions:heartbeat`

#### Message Flow (App → Gateway)
1. App writes to Convex `messages` table (source: "fastclaw", synced: false)
2. Relay subscribes to unsynced messages
3. Relay sends message to Gateway via WS (`sessions.send` or equivalent method)
4. Relay marks message as synced via `messages:markSynced`

#### Message Flow (Gateway → App)
1. Gateway processes a message (from any channel or the relay itself)
2. Relay receives session update event via WS
3. Relay fetches new messages from Gateway
4. Relay pushes to Convex via `messages:pushFromGateway`
5. App receives real-time update via Convex subscription

### 2. Pairing CLI (`scripts/pair.mjs`)

One-shot script for QR code pairing:

1. Generates/reads instance ID from `~/.openclaw/fastclaw/config.json`
2. Calls `pairing:createPairingCode` on Convex
3. Displays QR code in terminal (using `qrcode-terminal` npm package)
4. Polls `pairing:checkPairingStatus` until claimed or expired
5. On success, saves pairing state and starts/restarts relay

### 3. Config Storage

`~/.openclaw/fastclaw/config.json`:
```json
{
  "instanceId": "uuid-v4",
  "instanceName": "James's Mac Mini",
  "convexUrl": "https://xyz.convex.cloud",
  "gatewayUrl": "ws://127.0.0.1:18789",
  "gatewayToken": "from-openclaw-config"
}
```

## Dependencies

- `convex` — Convex client SDK
- `ws` — WebSocket client for Gateway connection
- `qrcode-terminal` — Terminal QR code display
- `uuid` — Instance ID generation
