---
name: Bitwarden / Vaultwarden
description: Bitwarden & Vaultwarden password manager integration. Use when storing, retrieving, generating, or managing passwords and credentials. Wraps the Bitwarden CLI (bw) with automatic session management. Works with both official Bitwarden and self-hosted Vaultwarden servers.
homepage: https://github.com/TWhidden/openclaw-skill-bitwarden
metadata:
  clawdbot:
    emoji: "🔐"
    requires:
      env: ["BW_SERVER", "BW_EMAIL", "BW_MASTER_PASSWORD"]
      primaryEnv: "BW_SERVER"
      bins: ["bw", "openssl", "curl"]
      files: ["bw.sh"]
---

# Bitwarden & Vaultwarden

Bitwarden/Vaultwarden CLI (`bw`) wrapper with automatic login, session caching, and convenient commands. Works seamlessly with both official Bitwarden (vault.bitwarden.com) and self-hosted Vaultwarden instances.

## Requirements

- Bitwarden CLI (`bw`) installed: `npm install -g @bitwarden/cli`
- A Bitwarden or Vaultwarden server instance
- Credentials configured (see Configuration below)

## Configuration

Set credentials via environment variables or a credentials file:

```bash
# Environment variables (preferred)
export BW_SERVER="https://vault.bitwarden.com"  # Official Bitwarden
# OR
export BW_SERVER="https://your-vaultwarden-instance.example.com"  # Vaultwarden
export BW_EMAIL="your-email@example.com"
export BW_MASTER_PASSWORD="your-master-password"

# Or use a credentials file (default: secrets/bitwarden.env)
export CREDS_FILE="/path/to/your/bitwarden.env"
```

The credentials file should contain:

```
BW_SERVER=https://vault.bitwarden.com
BW_EMAIL=your-email@example.com
BW_MASTER_PASSWORD=your-master-password
```

## Invocation

```bash
bash skills/bitwarden/bw.sh <command> [args...]
```

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `register [email] [pass] [name]` | Register new account | `bw.sh register user@example.com pass123 "My Name"` |
| `login` | Login & unlock vault | `bw.sh login` |
| `status` | Show vault status | `bw.sh status` |
| `list [search]` | List/search items | `bw.sh list github` |
| `get <name\|id>` | Get full item JSON | `bw.sh get "GitHub"` |
| `get-password <name\|id>` | Get password only | `bw.sh get-password "GitHub"` |
| `get-username <name\|id>` | Get username only | `bw.sh get-username "GitHub"` |
| `create <name> <user> <pass> [uri] [notes]` | Create login | `bw.sh create "GitHub" user pass https://github.com` |
| `generate [length]` | Generate password | `bw.sh generate 32` |
| `delete <id>` | Delete item | `bw.sh delete <uuid>` |
| `lock` | Lock vault | `bw.sh lock` |

## Workflow

1. First call per session: `bw.sh login` (auto-authenticates from configured credentials)
2. Session token cached at `/tmp/.bw_session`
3. All subsequent commands auto-use the cached session
4. After reboot/restart: run `login` again

## Storing New Credentials

```bash
# Generate + store
PASS=$(bash skills/bitwarden/bw.sh generate 32)
bash skills/bitwarden/bw.sh create "New Service" "user@email.com" "$PASS" "https://service.com"
```

## Account Registration

Register a new account on your Bitwarden/Vaultwarden server directly from the CLI:

```bash
# Register using configured credentials (from env/credentials file)
bash skills/bitwarden/bw.sh register

# Register with explicit credentials
bash skills/bitwarden/bw.sh register "user@example.com" "SecurePass123!" "Display Name"
```

**How it works:**
- Derives a master key using PBKDF2-SHA256 (600,000 iterations) with the email as salt
- Creates a master password hash for server authentication
- Generates a 64-byte symmetric key, encrypted with AES-256-CBC + HMAC-SHA256
- Submits registration to the server's `/api/accounts/register` endpoint

**Requirements:** OpenSSL 3.x+ (for PBKDF2 and HKDF support), curl, xxd.

**Note:** The master password must be at least 12 characters. Works with both official Bitwarden and Vaultwarden servers.

## Guardrails

- Never paste secrets into logs, chat, or code.
- Keep `bitwarden.env` out of version control.
- Use `chmod 600` on credential files.
- Session tokens are stored in `/tmp` and cleared on lock/logout.

## External Endpoints

| Endpoint | Purpose | Data Sent |
|----------|---------|-----------|
| User-configured BW_SERVER | Bitwarden/Vaultwarden API | Encrypted vault data, authentication credentials |

**Note:** The skill communicates with the Bitwarden server you configure via `BW_SERVER`. For official Bitwarden, this is `https://vault.bitwarden.com`. For Vaultwarden, this is your self-hosted instance URL.

## Security & Privacy

**What leaves your machine:**
- Authentication requests (email, master password) to your configured Bitwarden server
- Encrypted vault data (create/read/update/delete operations)
- All communication uses HTTPS/TLS

**What stays local:**
- Session tokens (cached in `/tmp/.bw_session`)
- Credential files (if using `bitwarden.env`)
- Decrypted passwords (only in memory, never written to disk)

**Trust statement:**
By using this skill, you are sending authentication credentials and vault data to the Bitwarden server you configure. Only install this skill if you trust your Bitwarden/Vaultwarden instance.

## Model Invocation

This skill can be invoked autonomously by your OpenClaw agent when it needs to:
- Store credentials securely
- Retrieve passwords for automation tasks
- Generate secure passwords

If you prefer manual approval before password operations, configure your OpenClaw agent's tool policy accordingly.

## Security Best Practices

1. **Credentials file:** Use `chmod 600` on `secrets/bitwarden.env`
2. **Environment isolation:** Don't share credential files across systems
3. **Session tokens:** Automatically expire; run `bw.sh lock` when done
4. **Git:** The `.gitignore` excludes all secrets (`secrets/`, `*.env`, `.bw_session`)
5. **Master password:** Never hardcode or log your master password
