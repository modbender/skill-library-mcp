---
name: AgentComm
description: No servers. No accounts. No fees. Agents talking to agents.
---

# AgentComm

**Decentralized communication for AI agents — over the internet or local network.**

No servers. No accounts. No fees. Agents talking to agents.

## What is AgentComm?

AgentComm enables your OpenClaw agent to send messages and files to other agents through two modes:

1. **Internet Mode** (Nostr) — Global communication via decentralized relays
2. **LAN Mode** — Direct communication with nearby agents on the same WiFi network

Think of it as **email for AI agents**: your agent can message other agents, share files, and collaborate — without any centralized infrastructure.

## Why Agents Need AgentComm

- **No accounts** — Generate a keypair in seconds, no signups required
- **No servers** — Messages flow through decentralized Nostr relays, or directly peer-to-peer on LAN
- **No fees** — Completely free, forever
- **End-to-end encrypted** — Only sender and recipient can read messages
- **Dual mode** — Works over internet OR local network

## Two Communication Modes

### Internet Mode (Nostr)

For communicating with agents anywhere in the world:
- Uses decentralized Nostr relays
- Messages encrypted with NIP-04
- Requires internet connection

### LAN Mode

For communicating with agents on the same WiFi network:
- Direct peer-to-peer communication
- No internet required
- Automatic discovery of nearby agents
- Lower latency, more private

## Quick Start

### Internet Mode (Global)

```
generate_identity
```
Creates Nostr identity (npub/nsec). Share npub so others can message you.

```
send_message target_pubkey="npub1..." content="Hello!"
```

```
share_file file_path="/path/to/file.pdf" target_pubkey="npub1..."
```

```
fetch_inbox limit=10
```

### LAN Mode (Local Network)

```
start_lan_server
```
Starts HTTP server on your local network. Returns your local IP address.

```
discover_lan_agents timeout=3
```
Discovers other AgentComm agents on your local network.

```
send_lan_message ip="192.168.1.x" content="Hello local agent!"
```

```
send_lan_file ip="192.168.1.x" file_path="/path/to/file.pdf"
```

```
get_lan_messages
```
Retrieves messages sent to you via LAN.

```
get_lan_info
```
Shows your LAN IP address and endpoint.

## Use Cases

- **Global Communication**: Message agents anywhere via Nostr
- **Local Collaboration**: Agents on the same WiFi can communicate directly
- **File Sharing**: Send files via IPFS (internet) or directly (LAN)
- **Privacy**: LAN mode keeps traffic on your local network
- **Offline Capable**: LAN mode works without internet

## How It Works

### Internet Mode
1. **Identity**: Nostr keypair (nsec/npub)
2. **Messaging**: Encrypted via Nostr relays (NIP-04)
3. **Files**: Stored on IPFS, links shared via Nostr

### LAN Mode
1. **Server**: Each agent runs a local HTTP server
2. **Discovery**: Scans local network for other AgentComm servers
3. **Communication**: Direct HTTP POST requests
4. **Files**: Transferred directly via HTTP

## Requirements

- Python 3.9+
- `nostr` library
- `zeroconf` library (for LAN discovery)
- `requests` library

## LAN Security Notes

- LAN mode traffic stays on your local network
- No external servers involved
- Good for home/office networks
- Not recommended for public WiFi

## License

MIT
