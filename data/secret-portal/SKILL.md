---
name: secret-portal
description: Spin up a one-time web UI for securely entering secret keys and env vars. Supports guided instructions, single-key mode, and cloudflared tunneling.
metadata:
  {
    "openclaw":
      {
        "emoji": "🔐",
        "requires": { "bins": ["uv"] },
        "install":
          [
            {
              "id": "uv-brew",
              "kind": "brew",
              "formula": "uv",
              "bins": ["uv"],
              "label": "Install uv (brew)",
            },
          ],
      },
  }
---

# Secret Portal

Spin up a temporary, one-time-use web UI for securely entering secret keys and environment variables. No secrets ever touch chat history or terminal logs.

## Quick Start

```bash
# Single key with cloudflared tunnel (recommended)
uv run --with secret-portal secret-portal \
  -k API_KEY_NAME \
  -f ~/.secrets/target-env-file \
  --tunnel cloudflared

# With guided instructions and a link to the key's console
uv run --with secret-portal secret-portal \
  -k OPENAI_API_KEY \
  -f ~/.env \
  -i '<strong>Get your key:</strong><ol><li>Go to platform.openai.com</li><li>Click API Keys</li><li>Create new key</li></ol>' \
  -l "https://platform.openai.com/api-keys" \
  --link-text "Open OpenAI dashboard →" \
  --tunnel cloudflared

# Multi-key mode (no -k flag, user enters key names and values)
uv run --with secret-portal secret-portal \
  -f ~/.secrets/keys.env \
  --tunnel cloudflared
```

## Options

| Flag | Description |
|------|-------------|
| `-k, --key` | Pre-populate a single key name (user only enters the value) |
| `-f, --env-file` | Path to save secrets to (default: `~/.env`) |
| `-i, --instructions` | HTML instructions shown above the input field |
| `-l, --link` | URL button for where to get/create the key |
| `--link-text` | Label for the link button (default: "Open console →") |
| `--tunnel` | `cloudflared` (recommended), `ngrok`, or `none` |
| `-p, --port` | Port to bind to (default: random) |
| `--timeout` | Seconds before auto-shutdown (default: 300) |

## Tunneling

**Use `--tunnel cloudflared`** — it's free, requires no account, has no interstitial pages, provides HTTPS, and auto-downloads the binary if missing.

ngrok free tier shows an interstitial warning page that blocks mobile and automated use.

Without a tunnel, the port must be open in your firewall/security group. The CLI will warn you if it detects the port is unreachable.

## Security

- One-time use: portal expires after a single submission
- Token auth: URL contains a random 32-byte token
- Secret values are **never** printed to stdout/stderr (enforced by tests)
- Env file is written with `600` permissions (owner-only)
- Secrets never touch chat history or terminal logs

## Source

https://github.com/Olafs-World/secret-portal
