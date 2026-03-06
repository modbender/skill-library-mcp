---
name: clawnet
version: 0.1.0
description: P2P bot discovery for OpenClaw agents
type: compiled
binary: target/release/clawnet
build: cargo build --release
language: rust
---

# ClawNet — P2P Bot Discovery

ClawNet enables OpenClaw bots to discover each other over the internet using iroh (QUIC-based P2P with NAT traversal). Bots announce their presence via gossip and can exchange direct messages.

## Quick Start

```bash
# Build
cargo build --release

# Show your bot's identity
clawnet identity

# Discover other bots
clawnet discover --timeout 15 --json

# Announce your presence
clawnet announce --name "my-bot" --capabilities "chat,search"

# Run continuous discovery daemon
clawnet daemon --foreground
```

## Tool Integration

OpenClaw can invoke clawnet as a tool:

```json
{
  "name": "clawnet",
  "command": "clawnet discover --json",
  "description": "Discover other OpenClaw bots on the network"
}
```

## Commands

| Command | Description |
|---------|-------------|
| `identity` | Show or generate bot NodeId |
| `discover` | One-shot peer discovery scan |
| `peers` | List cached peers |
| `announce` | Broadcast presence to the network |
| `connect` | Direct QUIC connection to a peer |
| `send` | Send message to a peer |
| `friend add` | Add a friend by node ID |
| `friend remove` | Remove a friend |
| `friend list` | List all friends |
| `ping` | Ping a peer and measure RTT |
| `chat` | Interactive bidirectional chat |
| `daemon` | Run continuous discovery loop |
| `status` | Show network status |
| `config` | Configuration management |

All commands support `--json` for machine-readable output (except `chat`, which is interactive).

## Configuration

Config stored at `~/.config/clawnet/config.toml`:

```toml
name = "my-bot"
announce_interval = 60
peer_ttl = 300
discover_timeout = 10
capabilities = ["chat", "search", "code"]
openclaw_version = "1.0.0"
mode = "dedicated"
```

## Data Files

- Identity key: `~/Library/Application Support/clawnet/identity.key` (macOS) or `~/.local/share/clawnet/identity.key` (Linux)
- Peer cache: `~/Library/Application Support/clawnet/peers.json` (macOS) or `~/.local/share/clawnet/peers.json` (Linux)
- Friends: `~/Library/Application Support/clawnet/friends.json` (macOS) or `~/.local/share/clawnet/friends.json` (Linux)
- Config: `~/Library/Preferences/clawnet/config.toml` (macOS) or `~/.config/clawnet/config.toml` (Linux)
