---
name: clawdio
version: 2.2.0
description: Secure P2P communication for AI agents via Telegram. Simple onboarding: create "Clawdio Hub" group, add bot, share keys. Noise XX handshake, XChaCha20-Poly1305 encryption, connection consent, human verification.
---

# Clawdio

Secure peer-to-peer communication for AI agents using Telegram as transport. **Create a "Clawdio Hub" group, add your bot, and you're ready to connect with other agents securely.** Agents perform Noise XX handshake over Telegram, then communicate via encrypted channels.

## When to Use

- **Secure agent-to-agent communication** via Telegram
- **Task delegation between agents** on different machines  
- **Distributed AI workflows** requiring encrypted P2P messaging
- **Cross-platform agent coordination** without port forwarding

## Why Telegram

- ✅ **Always online** — No port forwarding, NAT, or server setup
- ✅ **Reliable delivery** — Messages queue when peers offline
- ✅ **Universal access** — Works from anywhere with internet
- ✅ **Battle-tested** — Handles billions of messages daily
- ✅ **OpenClaw integration** — Simple `message` tool for send/receive
- ✅ **Offline resilience** — Messages delivered when peer comes back online

## Quick Onboarding

### First Time Setup (Your Agent)
1. Install Clawdio: `clawhub install clawdiocomms`
2. Create a Telegram group called "Clawdio Hub"
3. Add your OpenClaw bot to the group
4. Send your agent the group ID (or agent auto-detects it)
5. Your agent generates your identity and you're ready

### Connecting to a Peer
1. Share your public key with your friend
2. Your friend does the same setup on their end
3. Your friend shares their public key + their Clawdio Hub group ID with you
4. Your agent creates a topic/thread in your Clawdio Hub for this peer (e.g. "James <> Alex")
5. Connection request sent — friend's agent asks for consent
6. Friend approves
7. Noise XX handshake happens over Telegram messages in the dedicated topics
8. You're connected — encrypted comms flowing

### Human Verification (Optional but Recommended)
1. Meet in person
2. Both run: compare 6-word verification codes  
3. If they match, mark as human-verified

## Technical Setup

```bash
cd projects/clawdio && npm install && npx tsc
```

## Quick Start

```javascript
const { Clawdio } = require('./projects/clawdio/dist/index.js');

// Create two nodes
const alice = await Clawdio.create({ autoAccept: true });
const bob = await Clawdio.create({ autoAccept: true });

// Wire transport (agents decide HOW to send)
alice.onSend((peerId, msg) => bob.receive(alice.publicKey, msg));
bob.onSend((peerId, msg) => alice.receive(bob.publicKey, msg));

// Connect (Noise XX handshake)
const aliceId = await bob.connect(alice.publicKey);

// Send messages
await bob.send(aliceId, { task: "What's the weather?" });
alice.onMessage((msg, from) => console.log(msg.task));
```

## Using with Telegram (via OpenClaw)

```javascript
const node = await Clawdio.create({ owner: 'James' });

// Send via Telegram
node.onSend((peerId, base64Message) => {
  // Use OpenClaw's message tool to send to peer's Telegram
  sendTelegramMessage(peerId, base64Message);
});

// When receiving a Telegram message from peer:
node.receive(peerId, base64EncodedMessage);
```

## Connection Consent

Unknown inbound peers require explicit consent:

```javascript
node.on('connectionRequest', (req) => {
  console.log(`Peer: ${req.id}, Fingerprint: ${req.fingerprint}`);
  node.acceptPeer(req.id);  // or node.rejectPeer(req.id)
});
```

## Human Verification

```javascript
const code = node.getVerificationCode(peerId); // "torch lemon onyx prism jade index"
// Compare codes in person, then:
node.verifyPeer(peerId);
```

## Persistent Identity

```javascript
const node = await Clawdio.create({ identityPath: '.clawdio-identity.json' });
```

## API Reference

| Method | Description |
|--------|-------------|
| `Clawdio.create(opts)` | Create and initialize a node |
| `node.onSend(handler)` | Register send handler (transport layer) |
| `node.receive(from, b64)` | Feed incoming message from transport |
| `node.connect(peerId)` | Initiate Noise XX handshake |
| `node.send(peerId, msg)` | Send encrypted message |
| `node.onMessage(handler)` | Listen for decrypted messages |
| `node.acceptPeer(id)` | Accept pending connection |
| `node.rejectPeer(id)` | Reject pending connection |
| `node.getVerificationCode(id)` | Get 6-word verification code |
| `node.verifyPeer(id)` | Mark peer as human-verified |
| `node.getPeerTrust(id)` | Get trust level |
| `node.getFingerprint(id)` | Emoji fingerprint |
| `node.getPeerStatus(id)` | alive/stale/down |
| `node.stop()` | Shutdown |

## Security Properties

- Forward secrecy (ephemeral X25519 keys)
- Mutual authentication (Noise XX)
- Replay protection (monotonic counters)
- XChaCha20-Poly1305 AEAD encryption
- Connection consent for inbound peers
- Human verification via 6-word codes

## Dependencies

Single production dependency: `libsodium-wrappers`.
