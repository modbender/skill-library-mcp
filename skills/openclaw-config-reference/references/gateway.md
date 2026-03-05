# Gateway Configuration Reference

Full schema for the `gateway` block in `openclaw.json`.

---

## Table of Contents
1. [Gateway Block Schema](#gateway-block-schema)
2. [Mode](#mode)
3. [Port & Bind](#port--bind)
4. [Authentication](#authentication)
5. [Hot Reload](#hot-reload)
6. [HTTP Endpoints](#http-endpoints)
7. [Control UI](#control-ui)
8. [Trusted Proxies](#trusted-proxies)
9. [Tailscale Integration](#tailscale-integration)
10. [Gateway CLI Reference](#gateway-cli-reference)

---

## Gateway Block Schema

```json5
gateway: {
  mode: "local",
  port: 18789,
  bind: "loopback",
  reload: "hybrid",
  auth: {
    mode: "token",
    token: "your-token",
    password: "your-password"
  },
  http: {
    endpoints: {
      chatCompletions: { enabled: false }
    }
  },
  controlUi: {
    allowInsecureAuth: true
  },
  trustedProxies: ["172.16.0.0/12", "10.0.0.0/8", "127.0.0.1"]
}
```

---

## Mode

```json5
gateway: {
  mode: "local"     // Standard local mode
}
```

---

## Port & Bind

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `port` | number | `18789` | TCP port. Multiplexes WebSocket + HTTP on single port. |
| `bind` | string | `"loopback"` | Network interface to listen on. |

### Bind Modes

| Mode | Listens On | Use Case |
|------|-----------|----------|
| `loopback` | `127.0.0.1` only | Default. Safest - local machine only. |
| `lan` | `0.0.0.0` (all interfaces) | Required for Docker, ClawHosters, remote access. **Must set auth.** |
| `tailnet` | Direct Tailnet bind | For Tailscale network access. |
| `auto` | Prefers loopback | Falls back to available interface. |
| `custom` | Explicit network spec | Must provide additional network configuration. |

**CRITICAL:** `bind: "lan"` without authentication causes Gateway to refuse to start. Always set `auth` when using lan binding.

---

## Authentication

```json5
gateway: {
  auth: {
    mode: "token",           // token | password | trusted-proxy
    token: "your-token",     // Used when mode is "token"
    password: "your-password" // Used when mode is "password"
  }
}
```

### Auth Modes

| Mode | Description | Config / Env |
|------|-------------|-------------|
| `token` | Bearer token (recommended) | `gateway.auth.token` or `OPENCLAW_GATEWAY_TOKEN` env var |
| `password` | Password auth | `gateway.auth.password` or `OPENCLAW_GATEWAY_PASSWORD` env var |
| `trusted-proxy` | Identity-aware reverse proxy | Proxy handles auth, sets `X-Authenticated-User` header |

**Token auth usage:**
```
Authorization: Bearer <token>
```

**Rate limiting:** Auth endpoints have built-in rate limiting to prevent brute-force attacks.

**Prefer env vars over config:** Store tokens in `~/.openclaw/.env` rather than in `openclaw.json`:
```bash
# ~/.openclaw/.env
OPENCLAW_GATEWAY_TOKEN=your-secret-token
```

---

## Hot Reload

```json5
gateway: {
  reload: "hybrid"    // hybrid | hot | restart | off
}
```

| Mode | Behavior |
|------|----------|
| `hybrid` | Smart reload: hot-apply where possible, restart where needed (default) |
| `hot` | Non-destructive in-place reload. Keeps all connections alive. |
| `restart` | Full process restart on any config change. |
| `off` | Disable automatic reload entirely. |

**Manual hot reload:**
```bash
pkill -SIGUSR1 -f gateway
```

SIGUSR1 reloads config from disk without dropping connections or sessions.

---

## HTTP Endpoints

```json5
gateway: {
  http: {
    endpoints: {
      chatCompletions: {
        enabled: false     // Enable OpenAI-compatible /v1/chat/completions
      }
    }
  }
}
```

When enabled, the Gateway serves an OpenAI-compatible API at:
```
POST http://127.0.0.1:18789/v1/chat/completions
```

This allows using OpenClaw as a drop-in replacement for OpenAI API in other tools.

---

## Control UI

```json5
gateway: {
  controlUi: {
    allowInsecureAuth: true   // Allow auth over HTTP (not just HTTPS)
  }
}
```

Access the web-based Control UI at: `http://127.0.0.1:18789`

Features:
- Configuration editor
- Agent status monitoring
- Channel health
- Session management
- Built-in WebChat

---

## Trusted Proxies

For reverse proxy setups where the proxy handles authentication:

```json5
gateway: {
  auth: { mode: "trusted-proxy" },
  trustedProxies: [
    "127.0.0.1",
    "172.16.0.0/12",
    "10.0.0.0/8"
  ]
}
```

The proxy must set the `X-Authenticated-User` header with the authenticated user's identity. Only requests from listed CIDR ranges are trusted.

---

## Tailscale Integration

```bash
openclaw gateway --tailscale serve    # Expose via Tailscale Serve
openclaw gateway --tailscale funnel   # Expose via Tailscale Funnel (public internet)
openclaw gateway --tailscale off      # No Tailscale (default)
```

---

## Gateway CLI Reference

### Main Commands

```bash
openclaw gateway                    # Start gateway (foreground)
openclaw gateway run                # Alias for start
openclaw gateway health             # Health check (returns JSON)
openclaw gateway status             # Show running/stopped status
openclaw gateway probe              # Comprehensive debug diagnostic
openclaw gateway discover           # Scan mDNS beacons on local network
openclaw gateway call <method>      # Low-level RPC call
```

### Service Management

```bash
openclaw gateway install            # Register as system service
openclaw gateway start              # Start system service
openclaw gateway stop               # Stop system service
openclaw gateway restart            # Restart system service
openclaw gateway uninstall          # Remove system service
```

### Run Flags

| Flag | Description |
|------|-------------|
| `--port <port>` | Override port (default: 18789) |
| `--bind <mode>` | Bind mode |
| `--auth <mode>` | Auth mode |
| `--token <token>` | Bearer token (implies `--auth token`) |
| `--password <pw>` | Password (implies `--auth password`) |
| `--tailscale <mode>` | off, serve, funnel |
| `--allow-unconfigured` | Start without complete config |
| `--dev` | Development mode with verbose logging |
| `--reset` | Reset gateway state on startup |
| `--force` | Force start if another instance running |

### Health Check Response

```json
{
  "status": "ok",
  "version": "x.y.z",
  "uptime": 3600,
  "agents": [{"agentId": "main", "status": "idle"}],
  "channels": [{"channel": "telegram", "status": "connected"}],
  "cron": {"enabled": true, "jobs": 3}
}
```
