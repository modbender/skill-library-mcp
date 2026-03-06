# Gateway Configuration

## Basic Settings

```json
{
  "gateway": {
    "port": 18789,
    "bind": "loopback",
    "mode": "local"
  }
}
```

**bind options:**
- `loopback` — localhost only (default) ⭐
- `lan` — accessible on local network
- `auto` — auto-detect
- `tailnet` — Tailscale only

---

## Remote Access

### Via Tailscale (Recommended)

```json
{
  "gateway": {
    "bind": "tailnet",
    "tailscale": {
      "mode": "serve"
    },
    "auth": {
      "allowTailscale": true
    }
  }
}
```

**modes:**
- `serve` — Tailnet only (private)
- `funnel` — Public internet (requires password auth)

### Via SSH Tunnel

From remote machine:
```bash
ssh -L 18789:localhost:18789 user@gateway-host
```

Then connect to `ws://localhost:18789`

### Direct Remote

```json
{
  "gateway": {
    "bind": "lan",
    "auth": {
      "mode": "token",
      "token": "${GATEWAY_TOKEN}"
    }
  }
}
```

---

## TLS (HTTPS)

```json
{
  "gateway": {
    "tls": {
      "enabled": true,
      "autoGenerate": true
    }
  }
}
```

Or with custom certs:

```json
{
  "gateway": {
    "tls": {
      "enabled": true,
      "certPath": "/path/to/cert.pem",
      "keyPath": "/path/to/key.pem"
    }
  }
}
```

---

## Control UI

```json
{
  "gateway": {
    "controlUi": {
      "enabled": true,
      "basePath": "/",
      "allowedOrigins": ["https://control.example.com"]
    }
  }
}
```

Access at `http://127.0.0.1:18789`

---

## Hot Reload

```json
{
  "gateway": {
    "reload": {
      "mode": "hybrid",
      "debounceMs": 300
    }
  }
}
```

**modes:**
- `hybrid` — Hot-reload safe changes, restart for critical ⭐
- `hot` — Hot-reload only, warn on restart-needed
- `restart` — Always restart on change
- `off` — Manual restart required

---

## Config Reload Behavior

| Setting Category | Hot Reload? |
|------------------|-------------|
| Channels | ✅ Yes |
| Agents, Models | ✅ Yes |
| Automation (cron, hooks) | ✅ Yes |
| Tools, Browser, Skills | ✅ Yes |
| Gateway (port, TLS, auth) | ❌ Restart |
| Plugins | ❌ Restart |

---

## Remote Client Mode

Connect to a remote gateway:

```json
{
  "gateway": {
    "mode": "remote",
    "remote": {
      "url": "wss://gateway.example.com:18789",
      "token": "${REMOTE_TOKEN}"
    }
  }
}
```

---

## Node Browser Routing

Route browser commands to a node:

```json
{
  "gateway": {
    "nodes": {
      "browser": {
        "mode": "auto",
        "node": "my-mac"
      }
    }
  }
}
```

**modes:**
- `auto` — Pick connected browser node
- `manual` — Require explicit node param
- `off` — Disable node browser

---

## HTTP Endpoints

OpenAI-compatible API:

```json
{
  "gateway": {
    "http": {
      "endpoints": {
        "chatCompletions": { "enabled": true },
        "responses": { "enabled": true }
      }
    }
  }
}
```

Access at `POST /v1/chat/completions`

---

## Logging

```json
{
  "logging": {
    "level": "info",
    "consoleLevel": "info",
    "consoleStyle": "pretty",
    "file": "~/.openclaw/logs/gateway.log"
  }
}
```

**levels:** `silent`, `fatal`, `error`, `warn`, `info`, `debug`, `trace`
