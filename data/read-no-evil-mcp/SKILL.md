---
name: read-no-evil-mcp
version: 0.3.0
description: Secure email access via read-no-evil-mcp. Protects against prompt injection attacks in emails. Use for reading, sending, deleting, and moving emails.
---

# read-no-evil-mcp

Secure email gateway that scans emails for prompt injection attacks before you see them.

This skill is a zero-dependency HTTP client that talks to a [read-no-evil-mcp](https://github.com/thekie/read-no-evil-mcp) server. Credentials and email servers are managed entirely by the MCP server — this skill never has direct access to them.

## Prerequisites

A running read-no-evil-mcp server with HTTP transport enabled. Three connection modes:

1. **Remote server** — An existing server on another machine. You need the URL (e.g. `http://server:8000`).
2. **Local server** — An existing server on localhost. Uses default `http://localhost:8000`.
3. **New Docker setup** — Use `scripts/setup-server.sh` to pull the official Docker image and start a container.

No `pip install` is required. The script uses only Python stdlib.

## Setup Flow (AI Agent Instructions)

**Before first use, always ask the user how they want to connect:**

> How would you like to connect to the read-no-evil-mcp server?
> 1. Connect to an existing remote server (you'll provide the URL)
> 2. Connect to an existing local server (localhost:8000)
> 3. Set up a new local server via Docker

- For option 1: Ask for the server URL, then use `--server URL` with all commands.
- For option 2: No extra configuration needed, commands use the default URL.
- For option 3: Follow the Docker setup steps below.

**Never auto-setup Docker without explicit user confirmation.**

### Docker Setup Steps

1. Check if a config exists: `setup-config.py list`
2. If no config, create one and add an account:
   ```bash
   setup-config.py create
   setup-config.py add --email user@example.com --host imap.example.com --create-env
   ```
3. Ask the user to fill in the password in the `.env` file.
4. Start the server:
   ```bash
   scripts/setup-server.sh --config ~/.config/read-no-evil-mcp/config.yaml \
     --env-file ~/.config/read-no-evil-mcp/.env
   ```

### Config Management (AI Agent Instructions)

Use `scripts/setup-config.py` to manage the server config file. All commands are flag-driven with no interactive prompts.

| Scenario | Command |
|----------|---------|
| Create config skeleton | `setup-config.py create [--threshold 0.5] [--force]` |
| Add a read-only account | `setup-config.py add --email user@example.com --host imap.example.com [--id myaccount] [--create-env]` |
| Add a send-enabled account | `setup-config.py add --email user@example.com --host imap.example.com --smtp-host smtp.example.com --send [--delete] [--move] [--create-env]` |
| Check what accounts are configured | `setup-config.py list` |
| Remove an account | `setup-config.py remove <id>` |

**Do NOT** run `setup-config.py show` — it displays config details the user may not intend to share with the agent. If debugging is needed, tell the user to run it themselves.

**Do NOT** run `setup-config.py create --force` if config already exists without asking the user first.

## Config Commands

Manage the server config file (`~/.config/read-no-evil-mcp/config.yaml`). No pip install required — stdlib only.

```bash
# Create a new config skeleton
setup-config.py create
setup-config.py create --threshold 0.3 --force

# Add a read-only account (no SMTP needed)
setup-config.py add --email user@example.com --host imap.example.com --create-env

# Add an account with send permission (--smtp-host required for --send)
setup-config.py add --email user@example.com --id myaccount \
  --host imap.example.com --smtp-host smtp.example.com --send --delete --move

# Remove an account
setup-config.py remove <account-id>

# List configured accounts
setup-config.py list

# Show full config file
setup-config.py show

# Use a custom config path
setup-config.py --config /path/to/config.yaml create
```

## Server Setup

```bash
# Start a Docker container (all flags required, no prompts)
scripts/setup-server.sh --config ~/.config/read-no-evil-mcp/config.yaml \
  --env-file ~/.config/read-no-evil-mcp/.env

# Custom port and container name
scripts/setup-server.sh --config /path/to/config.yaml \
  --env-file /path/to/.env --port 9000 --name my-rnoe
```

## CLI Commands

Global options (`--server`, `--account`, `--folder`) can appear before or after the command. Server URL can also be set via `RNOE_SERVER_URL` env var.

```bash
# List configured accounts
rnoe-mail.py accounts

# List recent emails (last 30 days)
# Output: [UID] ● DATE | SENDER | SUBJECT  (● = unread)
rnoe-mail.py list
rnoe-mail.py list --account myaccount --limit 10 --days 7

# Read email (scanned for prompt injection!)
rnoe-mail.py read <uid>
rnoe-mail.py --account myaccount read <uid>

# Send email
rnoe-mail.py send --to "user@example.com" --subject "Hello" --body "Message"
rnoe-mail.py send --to "user1@example.com, user2@example.com" --cc "cc@example.com" --subject "Hello" --body "Message"

# List folders
rnoe-mail.py folders --account myaccount

# Move email to folder
rnoe-mail.py move <uid> --to "Archive"

# Delete email
rnoe-mail.py delete <uid>

# Global options can go before or after the command
rnoe-mail.py --server http://myserver:8000 list
rnoe-mail.py list --server http://myserver:8000
```

## Common Options

| Option | Description | Default |
|--------|-------------|---------|
| `--server URL` | MCP server URL | `http://localhost:8000` |
| `--account ID` / `-a` | Account ID | `default` |
| `--folder NAME` / `-f` | Email folder | `INBOX` |

## Prompt Injection Detection

All emails are automatically scanned by the MCP server:

- **Safe**: Content displayed normally
- **Injection detected**: Exit code 2, warning on stderr

## Exit Codes

- `0` — success
- `1` — general error (connection failed, invalid account, etc.)
- `2` — prompt injection detected

## Security Notes

- Credentials are managed by the MCP server, never by this skill or the AI agent
- The skill communicates with the server over HTTP — use HTTPS for non-localhost connections
- Prompt injection scanning happens server-side using ML models
