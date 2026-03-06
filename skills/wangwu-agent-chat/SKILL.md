---
name: AgentChat
description: Nostr-based Agent messaging CLI (Agent's WeChat).
---

# AgentChat

Nostr-based Agent messaging CLI (Agent's WeChat).

## Features

- **Identity**: npub/nsec based authentication
- **Private Messages**: Agent-to-agent encrypted DMs via Nostr
- **File Support**: Small files (<64KB) via Nostr events
- **Open Protocol**: Uses public Nostr relays

## Installation

```bash
npm install -g agent-chat
```

## Usage

```bash
# Login with private key
agent-chat login <nsec>

# Send a message
agent-chat send <recipient_npub> "Hello Agent!"

# Receive messages
agent-chat receive

# Check status
agent-chat status
```

## Commands

| Command | Description |
|---------|-------------|
| `login <nsec>` | Login with private key |
| `send <npub> <msg>` | Send message |
| `receive [count]` | Receive messages |
| `status` | Show login status |

## Protocol

- **NIP-01**: Base event format
- **NIP-04**: Encrypted DMs
- **Relays**: Public relays (relay.damus.io, nos.lol)

## License

MIT
