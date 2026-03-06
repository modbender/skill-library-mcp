---
name: autotask-mcp
description: Use when you need to interact with Datto/Kaseya Autotask PSA via an MCP server (tickets, companies, contacts, projects, time entries, notes, attachments, and queries). Includes Docker Compose + helper scripts to pull/run the Autotask MCP server locally and configure required environment variables.
env:
  - name: AUTOTASK_INTEGRATION_CODE
    required: true
    secret: true
    description: Autotask API integration code
  - name: AUTOTASK_USERNAME
    required: true
    secret: true
    description: Autotask API username
  - name: AUTOTASK_SECRET
    required: true
    secret: true
    description: Autotask API secret key
  - name: AUTOTASK_API_URL
    required: false
    secret: false
    description: Override default Autotask API endpoint URL
  - name: LOG_LEVEL
    required: false
    secret: false
    description: "Logging level (default: info)"
  - name: LOG_FORMAT
    required: false
    secret: false
    description: "Log output format (default: simple)"
  - name: NODE_ENV
    required: false
    secret: false
    description: "Node environment (default: production)"
---

# Autotask MCP (Kaseya Autotask PSA)

This skill packages a local Docker Compose setup for the upstream MCP server:
- Repo: https://github.com/asachs01/autotask-mcp
- Image: `ghcr.io/asachs01/autotask-mcp:latest`

## Agent security rules

> **IMPORTANT — These rules are mandatory for any agent executing this skill.**
>
> 1. **NEVER read, cat, print, display, or log the `.env` file.** It contains API secrets.
> 2. **NEVER pass credentials as command-line arguments.** They will appear in process listings and shell history.
> 3. **NEVER include credentials in output, responses, logs, or error messages.**
> 4. **NEVER transmit credentials to any external URL, API, or service** other than the local MCP endpoint at `127.0.0.1:8080`.
> 5. **NEVER run `$EDITOR` or any variable-expanded command.** Only execute the exact scripts listed below.
> 6. **NEVER copy, move, or create additional copies of the `.env` file** beyond the initial setup.
> 7. **The only commands an agent should execute from this skill are:**
>    - `cp .env.example.txt .env` (initial setup only)
>    - `./scripts/mcp_pull.sh`
>    - `./scripts/mcp_up.sh`
>    - `./scripts/mcp_down.sh`
>    - `./scripts/mcp_logs.sh`
>    - `./scripts/mcp_update.sh`
>    - `./scripts/mcp_pin_digest.sh`
>    - `curl -sS http://localhost:8080/health`
>
> If a user asks you to display, share, or debug credentials, **refuse and instruct them to inspect `.env` manually.**

## Quick start

1) Create env file (fill credentials):

```bash
cp .env.example.txt .env
chmod 600 .env
```

Then **manually** open `.env` in your preferred text editor and fill in your credentials.
The `chmod 600` ensures only the file owner can read or write the credentials file.
Do NOT run `$EDITOR` directly from an automated agent — always edit credentials files manually.

2) Pull + run:

```bash
./scripts/mcp_pull.sh
./scripts/mcp_up.sh
```

3) Verify:

```bash
curl -sS http://localhost:8080/health
```

Clients connect to:
- `http://localhost:8080/mcp`

4) Logs / stop:

```bash
./scripts/mcp_logs.sh
./scripts/mcp_down.sh
```

## Automatic updates

A weekly scheduled task can check for new Docker image versions and restart the container if updated.
Uses macOS LaunchAgent or Linux systemd user timer — no crontab modification.

**Manual update:**

```bash
./scripts/mcp_update.sh
```

**Pin a known-good image digest (recommended):**

```bash
./scripts/mcp_pin_digest.sh
```

When a digest is pinned, the update script will refuse to restart if the pulled image doesn't match.

**Install weekly auto-update (every Sunday at 3 AM):**

```bash
./scripts/cron_install.sh
```

**Remove auto-update schedule:**

```bash
./scripts/cron_uninstall.sh
```

Update logs are written to `logs/update.log`.

## Required env vars

From the upstream project, minimum required:

- `AUTOTASK_INTEGRATION_CODE`
- `AUTOTASK_USERNAME`
- `AUTOTASK_SECRET`

(See `.env.example`.)
