---
name: lobsterlan
description: Communicate with other OpenClaw agents on your local network. Use when you need to ask another agent a question (sync), delegate a task (async), or check if a peer agent is reachable. Supports both synchronous chat completions and asynchronous webhook-based task delegation. Requires peers.json config with peer addresses and tokens.
---

# LobsterLAN — Agent-to-Agent Communication

Talk to other OpenClaw agents on your LAN.

## Setup

1. Copy `config/peers.example.json` to `config/peers.json`
2. Fill in peer hostnames, ports, and tokens
3. Ensure target agents have the required APIs enabled (see below)
4. **Set up a secure transport** (see Network Transport below)

## Required Config on Target Agent

For **sync ask** (chat completions):
```jsonc
// Target agent's openclaw.json — keep bind as "loopback"!
{
  "gateway": {
    "http": {
      "endpoints": {
        "chatCompletions": { "enabled": true }
      }
    }
  }
}
```

> ⚠️ **Do NOT set `gateway.bind` to `"lan"`** — OpenClaw will refuse to start if the gateway is exposed on a non-loopback address without TLS. Use a secure transport instead (see below).

For **async delegate** (webhooks):
```jsonc
{
  "hooks": {
    "enabled": true,
    "token": "a-secure-shared-secret"
  }
}
```

## Network Transport

OpenClaw gateways default to `bind: loopback` and will not start with plaintext on non-loopback addresses. You need a secure transport layer for cross-host communication:

| Approach | Complexity | Best For |
|----------|-----------|----------|
| **SSH Tunnel** ⭐ | Low | Home LANs, simple setups |
| **Reverse Proxy (TLS)** | Medium | Environments with existing Caddy/nginx |
| **Tailscale Serve** | Medium | Multi-site or remote agents |

**For simple LANs, SSH tunneling is recommended.** Both gateways stay on loopback, the SSH tunnel provides encryption, and no gateway config changes are needed.

### SSH Tunnel Example

Forward a local port to the remote agent's loopback gateway:
```bash
ssh -N -L 18790:127.0.0.1:18790 user@remote-agent-host
```

Then in `peers.json`, point the peer to `127.0.0.1:18790` (the local tunnel endpoint).

For persistence, use a systemd user service with `Restart=always`. See the full setup guide in `docs/setup.md`.

## Commands

### Ask (synchronous — wait for reply)
```bash
scripts/lobsterlan.sh ask scotty "What is the CPU temperature?"
```
Use for quick questions where you need the answer now.

### Delegate (async — fire and forget)
```bash
scripts/lobsterlan.sh delegate scotty "Generate 5 zen wallpapers and push to the file share"
```
Use for long-running tasks. The peer processes independently.

### Status check
```bash
scripts/lobsterlan.sh status scotty
```

### List peers
```bash
scripts/lobsterlan.sh peers
```

## Agent Usage (from within OpenClaw)

Run via exec tool:
```bash
cd ~/.openclaw/workspace/skills/lobsterlan && scripts/lobsterlan.sh ask scotty "status report"
```

## Security

Three layers protect communication:
1. **Network**: LAN-only (firewall blocks external access to gateway port)
2. **Gateway token**: Bearer auth on every request
3. **Agent ID header** (optional): `X-LobsterLAN-Agent` sent with self-ID

The gateway token is the real security boundary. The agent ID header is defense-in-depth for environments where you want explicit identity verification.

## Environment Variables

- `LOBSTERLAN_CONFIG` — path to peers.json (default: `../config/peers.json` relative to script)
