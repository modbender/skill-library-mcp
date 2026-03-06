---
name: secret-manager
description: Manage API keys securely via GNOME Keyring and inject them into OpenClaw config.
homepage: https://github.com/openclaw/skills
metadata: {"clawdbot":{"emoji":"🔐","requires":{"bins":["secret-tool","systemctl","python3"]},"install":[{"id":"bash","kind":"bash","bin":"secret-manager.sh","label":"Install Secret Manager (bash)"}]}}
---

# Secret Manager

A secure way to manage API keys for OpenClaw using the system keyring (GNOME Keyring / libsecret).

This skill provides a `secret-manager` CLI that:
1.  Stores API keys securely using `secret-tool`.
2.  Injects them into your `auth-profiles.json`.
3.  Propagates them to `systemd` user environment.
4.  Restarts the OpenClaw Gateway service inside your Distrobox container.

## Installation

Ensure you have the dependencies:
- **Debian/Ubuntu:** `sudo apt install libsecret-tools`
- **Fedora:** `sudo dnf install libsecret`
- **Arch:** `sudo pacman -S libsecret`

Copy the script to your path or run it directly.

## Configuration

The script uses default paths that work for most OpenClaw installations, but you can override them with environment variables:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `OPENCLAW_CONTAINER` | Name of the Distrobox container | `clawdbot` |
| `OPENCLAW_HOME` | Path to OpenClaw config directory | `~/.openclaw` |
| `SECRETS_ENV_FILE` | Path to an optional .env file to source | `~/.config/openclaw/secrets.env` |

## Usage

**List all configured keys:**
```bash
secret-manager list
```

**Set a key (interactive prompt):**
```bash
secret-manager OPENAI_API_KEY
# (Paste key when prompted)
```

**Set a key (direct):**
```bash
secret-manager DISCORD_BOT_TOKEN "my-token-value"
```

**Supported Keys:**
- `OPENAI_API_KEY`
- `GEMINI_API_KEY`
- `DISCORD_BOT_TOKEN`
- `GATEWAY_AUTH_TOKEN`
- `OLLAMA_API_KEY`
- `GIPHY_API_KEY`
- `GOOGLE_PLACES_API_KEY`
- `LINKEDIN_LI_AT`
- `LINKEDIN_JSESSIONID`
