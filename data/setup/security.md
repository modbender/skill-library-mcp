# Security Configuration

## DM Policies

Every channel needs a DM policy:

| Policy | Behavior | Use Case |
|--------|----------|----------|
| `pairing` | Unknown users get code, CLI approval | ⭐ Recommended |
| `allowlist` | Only allowFrom users | Strict access |
| `open` | Anyone can message | Public bots only |
| `disabled` | No DMs | Channel-only bot |

```json
{
  "channels": {
    "telegram": {
      "dmPolicy": "pairing",
      "allowFrom": ["YOUR_USER_ID"]
    }
  }
}
```

**Approve pending users:**
```bash
openclaw pairing list
openclaw pairing approve telegram ABC123
```

---

## Gateway Authentication

For remote access, ALWAYS set auth:

```json
{
  "gateway": {
    "auth": {
      "mode": "token",
      "token": "your-secure-token-here"
    }
  }
}
```

**mode options:**
- `token` — API token (recommended)
- `password` — Password auth (for Tailscale Funnel)

---

## Tailscale Integration

Expose gateway securely via Tailscale:

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

**mode:** `off`, `serve` (tailnet only), `funnel` (public, requires password)

---

## Tool Access Control

### Exec Tool

```json
{
  "tools": {
    "exec": {
      "host": "gateway",
      "security": "allowlist",
      "safeBins": ["cat", "ls", "grep", "head", "tail"]
    }
  }
}
```

**security levels:**
- `deny` — No exec allowed
- `allowlist` — Only safeBins ⭐
- `full` — Any command (dangerous)

### Elevated Permissions

```json
{
  "tools": {
    "elevated": {
      "enabled": true,
      "allowFrom": {
        "telegram": ["YOUR_USER_ID"]
      }
    }
  }
}
```

---

## Owner Access

Define who has owner-level access:

```json
{
  "commands": {
    "ownerAllowFrom": [
      "telegram:123456",
      "whatsapp:+15551234567"
    ]
  }
}
```

---

## Per-Group Security

Different tools for different groups:

```json
{
  "channels": {
    "telegram": {
      "groups": {
        "-100GROUPID": {
          "tools": {
            "deny": ["exec", "gateway"]
          },
          "toolsBySender": {
            "123456": {
              "alsoAllow": ["exec"]
            }
          }
        }
      }
    }
  }
}
```

---

## Cross-Context Messaging

Control whether agent can send to other channels:

```json
{
  "tools": {
    "message": {
      "crossContext": {
        "allowWithinProvider": true,
        "allowAcrossProviders": false,
        "marker": {
          "enabled": true
        }
      }
    }
  }
}
```

---

## Sensitive Data

Never put secrets directly in config. Use env vars:

```json
{
  "channels": {
    "telegram": {
      "botToken": "${TELEGRAM_BOT_TOKEN}"
    }
  }
}
```

Store in `~/.openclaw/.env`:
```bash
TELEGRAM_BOT_TOKEN=1234567890:ABC...
```

---

## Security Checklist

- [ ] DM policy set to `pairing` or `allowlist`
- [ ] Gateway auth configured for remote access
- [ ] Exec security set to `allowlist` (not `full`)
- [ ] Elevated permissions restricted to known users
- [ ] Secrets in env vars, not config
- [ ] Group tools restricted appropriately
- [ ] Cross-context messaging controlled

---

## Run Security Check

```bash
openclaw doctor
```

This flags:
- Open DM policies
- Missing auth tokens
- Dangerous exec settings
- Exposed gateway bindings
