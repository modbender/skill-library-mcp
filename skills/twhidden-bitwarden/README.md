# Bitwarden / Vaultwarden — Password Manager Skill

[![ClawHub](https://img.shields.io/badge/ClawHub-twhidden--bitwarden-blue)](https://clawhub.ai/skills/twhidden-bitwarden)

An [OpenClaw](https://openclaw.dev) skill for [Bitwarden](https://bitwarden.com/) password management. Wraps the [Bitwarden CLI](https://bitwarden.com/help/cli/) with automatic session management.

**Works with both official Bitwarden and [Vaultwarden](https://github.com/dani-garcia/vaultwarden) (self-hosted).**

**📦 Install from ClawHub:** [`clawhub install twhidden-bitwarden`](https://clawhub.ai/skills/twhidden-bitwarden)

## Features

- 🔐 Automatic login & session caching
- 🔑 Store, retrieve, and manage credentials
- 🎲 Secure password generation
- 🔍 Search across your vault
- ⚡ Simple single-command interface
- 🏠 Compatible with official Bitwarden AND self-hosted Vaultwarden

## Prerequisites

- [OpenClaw](https://openclaw.dev) installed and configured
- [Bitwarden CLI](https://bitwarden.com/help/cli/) (`bw`): `npm install -g @bitwarden/cli`
- A Bitwarden or Vaultwarden server instance

## Installation

Copy the skill into your OpenClaw workspace:

```bash
cp -r bitwarden-skill-opensource/ ~/.openclaw/workspace/skills/bitwarden/
```

Or clone directly:

```bash
cd ~/.openclaw/workspace/skills/
git clone https://github.com/YOUR_USERNAME/openclaw-skill-bitwarden.git bitwarden
```

## Configuration

Create a credentials file at `secrets/bitwarden.env` in your OpenClaw workspace:

```bash
BW_SERVER=https://vault.bitwarden.com
BW_EMAIL=your-email@example.com
BW_MASTER_PASSWORD=your-master-password
```

Secure the file:

```bash
chmod 600 ~/.openclaw/workspace/secrets/bitwarden.env
```

Alternatively, set these as environment variables directly.

You can also override the credentials file path:

```bash
export CREDS_FILE=/path/to/your/credentials.env
```

### Server Configuration Examples

**Official Bitwarden:**
```bash
BW_SERVER=https://vault.bitwarden.com
```

**Vaultwarden (self-hosted):**
```bash
BW_SERVER=https://your-vaultwarden-instance.com
```

Both use the same Bitwarden CLI — just point `BW_SERVER` at your instance.

## Vaultwarden Compatibility

This skill is fully compatible with [Vaultwarden](https://github.com/dani-garcia/vaultwarden), the popular self-hosted Bitwarden-compatible server. Since Vaultwarden implements the Bitwarden API, the Bitwarden CLI works identically with both services. Simply set `BW_SERVER` to your Vaultwarden instance URL and everything works out of the box.

## Usage

```bash
# Login (required once per session)
bash skills/bitwarden/bw.sh login

# Retrieve a password
bash skills/bitwarden/bw.sh get-password "GitHub"

# Search vault
bash skills/bitwarden/bw.sh list "email"

# Generate a secure password
bash skills/bitwarden/bw.sh generate 32

# Store a new credential
bash skills/bitwarden/bw.sh create "Service" "user@example.com" "password123" "https://service.com"

# Lock vault
bash skills/bitwarden/bw.sh lock
```

### All Commands

| Command | Description |
|---------|-------------|
| `register [email] [pass] [name]` | Register new account on server |
| `login` | Login & unlock vault |
| `status` | Show vault status |
| `sync` | Sync vault with server |
| `list [search]` | List/search items |
| `get <name\|id>` | Get full item JSON |
| `get-password <name\|id>` | Get password only |
| `get-username <name\|id>` | Get username only |
| `get-notes <name\|id>` | Get notes only |
| `create <name> <user> <pass> [uri] [notes]` | Create login item |
| `create-json <json>` | Create item from raw JSON |
| `edit <id> <json>` | Edit item |
| `delete <id>` | Delete item |
| `generate [length]` | Generate secure password (default: 24 chars) |
| `lock` | Lock vault |
| `logout` | Logout completely |

## Security Best Practices

- **Never commit credentials** — `secrets/` and `.env` files are in `.gitignore`
- **File permissions** — Use `chmod 600` on credential files
- **Session tokens** — Stored in `/tmp/.bw_session`, cleared on lock/logout
- **Master password** — Consider using a dedicated account for OpenClaw with limited vault access
- **Network** — Use HTTPS for your server instance; consider VPN/firewall restrictions
- **Audit** — Regularly review the credentials stored and accessed by OpenClaw

## How It Works

1. On `login`, the script authenticates with the Bitwarden CLI using configured credentials
2. The session token is cached at `/tmp/.bw_session` with `600` permissions
3. Subsequent commands automatically use the cached session
4. On `lock`/`logout`, the session file is removed

## Contributing

Contributions welcome! Please ensure no credentials or instance-specific information is included in PRs.

## License

MIT License — see [LICENSE](LICENSE).

## Security Improvements in v1.0.3

### Account Registration Support
- **Added:** `register` command for creating new accounts via API
- **Crypto:** Uses proper Bitwarden key derivation (PBKDF2 + HKDF-Expand + AES-256-CBC + HMAC-SHA256)
- **Security:** 12-character minimum password, error messages don't leak server response details
- **Compatibility:** Works with both official Bitwarden and Vaultwarden servers
- **Dependencies:** Requires Python `cryptography` and `requests` packages

## Security Improvements in v1.0.1

### Safe Credential Loading
- **Fixed:** Replaced dangerous `source` command with safe KEY=VALUE parsing
- **Impact:** Credential files can no longer execute arbitrary shell code
- **Details:** The script now safely parses only `BW_SERVER`, `BW_EMAIL`, and `BW_MASTER_PASSWORD` variables from the credentials file, ignoring any other content or shell commands

### Declared Dependencies
- **Added:** Explicit declaration of required binaries (`bw`, `python3`) in SKILL.md metadata
- **Impact:** ClawHub and OpenClaw can now properly validate dependencies before installation
- **Details:** Updated `metadata.clawdbot.requires.bins` to include all required system binaries

### Security Scan
- **Status:** Addresses all concerns raised in ClawHub security scan
- **Report:** https://clawhub.ai/skills/twhidden-bitwarden (scan results available)
