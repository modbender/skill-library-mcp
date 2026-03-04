---
name: clawdio
version: 1.0.0
description: Secure P2P communication for AI agents. Noise XX handshake, XChaCha20-Poly1305 encryption, connection consent, human verification. Zero central servers.
---

# Clawdio

Minimal secure peer-to-peer communication for AI agents. Two agents exchange a connection string, perform a Noise XX handshake, then communicate over encrypted channels. No central server required.

## When to Use

- Agent-to-agent communication across machines or networks
- Secure task delegation between sub-agents on different hosts
- Any scenario requiring encrypted, authenticated P2P messaging

## Setup

The Clawdio project lives at `projects/clawdio/`. Install dependencies and build:

```bash
cd projects/clawdio && npm install && npx tsc
```

## Quick Start

```javascript
const { Clawdio } = require('./projects/clawdio/dist/index.js');

// Create two nodes
const alice = await Clawdio.create({ port: 9090, autoAccept: true });
const bob = await Clawdio.create({ port: 9091, autoAccept: true });

// Connect (Noise XX handshake)
const aliceId = await bob.exchangeKeys(alice.getConnectionString());

// Send messages
await bob.send(aliceId, { task: "What's the weather?" });
alice.onMessage((msg, from) => console.log(msg.task));
```

## Connection Consent (Recommended)

By default, unknown inbound peers require explicit consent:

```javascript
const node = await Clawdio.create({ port: 9090 }); // autoAccept defaults to false

node.on('connectionRequest', (req) => {
  console.log(`Connection from ${req.id}`);
  console.log(`Fingerprint: ${req.fingerprint}`);
  // Accept or reject
  node.acceptPeer(req.id);  // or node.rejectPeer(req.id)
});
```

Outbound connections (you calling `exchangeKeys`) are auto-accepted. Already-trusted peers auto-reconnect.

## Human Verification

For high-trust scenarios, verify peers in person:

```javascript
node.setOwner('Alice');
const code = node.getVerificationCode(peerId); // "torch lemon onyx prism jade index"
// Both humans compare codes in person, then:
node.verifyPeer(peerId); // trust: 'accepted' → 'human-verified'
node.getPeerTrust(peerId); // 'human-verified'
```

## Trust Levels

- `pending` — connection request received, not yet accepted
- `accepted` — peer accepted, encrypted communication active
- `human-verified` — verified via in-person code exchange

## Persistent Identity

Pass `identityPath` to persist keys and trusted peers across restarts:

```javascript
const node = await Clawdio.create({
  port: 9090,
  identityPath: '.clawdio-identity.json'
});
```

## Sub-Agent Pattern

Spawn a sub-agent to handle Clawdio communication:

```
1. Main agent spawns sub-agent with task
2. Sub-agent creates Clawdio node, connects to remote peer
3. Sub-agent exchanges messages, collects results
4. Sub-agent reports back to main agent
```

## Security Properties

- Forward secrecy (ephemeral X25519 keys)
- Mutual authentication (Noise XX)
- Replay protection (monotonic counters)
- XChaCha20-Poly1305 AEAD encryption
- Connection consent for inbound peers

## API Reference

| Method | Description |
|--------|-------------|
| `Clawdio.create(opts)` | Create and start a node |
| `node.exchangeKeys(connStr)` | Connect to peer |
| `node.send(peerId, msg)` | Send encrypted message |
| `node.onMessage(handler)` | Listen for messages |
| `node.acceptPeer(id)` | Accept pending connection |
| `node.rejectPeer(id)` | Reject pending connection |
| `node.setOwner(name)` | Set human owner name |
| `node.getVerificationCode(id)` | Get 6-word verification code |
| `node.verifyPeer(id)` | Mark peer as human-verified |
| `node.getPeerTrust(id)` | Get trust level |
| `node.getFingerprint(id)` | Emoji fingerprint |
| `node.getPeerStatus(id)` | alive/stale/down |
| `node.stop()` | Shutdown |
