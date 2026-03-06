# Autotask MCP

A Docker Compose skill for running the [Autotask MCP server](https://github.com/asachs01/autotask-mcp) locally. Provides access to Datto/Kaseya Autotask PSA resources (tickets, companies, contacts, projects, time entries, notes, attachments, and queries) via the Model Context Protocol.

**Version:** 1.0.4

## Prerequisites

- Docker and Docker Compose
- Autotask API credentials (Integration Code, Username, Secret)

## Setup

1. **Create your environment file:**

   ```bash
   cp .env.example.txt .env
   chmod 600 .env
   ```

   Then **manually** open `.env` in your preferred text editor and fill in your credentials.
   The `chmod 600` restricts the file so only the owner can read or write it.

   > **Security note:** Never run `$EDITOR` from an automated agent. Always edit credential files manually.

2. **Pull the image and start the service:**

   ```bash
   ./scripts/mcp_pull.sh
   ./scripts/mcp_up.sh
   ```

3. **Verify the service is healthy:**

   ```bash
   curl -sS http://localhost:8080/health
   ```

   MCP endpoint: `http://localhost:8080/mcp`

## Scripts

| Script | Description |
|---|---|
| `scripts/mcp_pull.sh` | Pull the latest Docker image |
| `scripts/mcp_up.sh` | Start the service in detached mode |
| `scripts/mcp_down.sh` | Stop and remove the container |
| `scripts/mcp_logs.sh` | Tail container logs (last 200 lines) |
| `scripts/mcp_update.sh` | Check for image updates and restart if a new version is found |
| `scripts/mcp_pin_digest.sh` | Pin the current image digest for supply chain verification |
| `scripts/cron_install.sh` | Install a weekly scheduled task (Sunday 3 AM) to auto-update |
| `scripts/cron_uninstall.sh` | Remove the auto-update scheduled task |

## Automatic Updates

The update script compares image digests before and after pulling, and only restarts the container when a new image is detected. Logs are written to `logs/update.log`.

### Digest Pinning (Supply Chain Protection)

You can pin the current image digest so that the update script refuses to restart if a pulled image doesn't match:

```bash
./scripts/mcp_pin_digest.sh
```

When pinned, `mcp_update.sh` will pull the latest image but **abort** if the digest differs from the pin. This prevents silent supply chain compromises. Re-run `mcp_pin_digest.sh` after manually verifying a new version.

**Manual update:**

```bash
./scripts/mcp_update.sh
```

**Enable weekly auto-updates:**

Uses macOS LaunchAgent or Linux systemd user timer — no direct crontab modification.

```bash
./scripts/cron_install.sh
```

**Disable auto-updates:**

```bash
./scripts/cron_uninstall.sh
```

## Environment Variables

### Required

| Variable | Description |
|---|---|
| `AUTOTASK_INTEGRATION_CODE` | Your Autotask API integration code |
| `AUTOTASK_USERNAME` | Your Autotask API username |
| `AUTOTASK_SECRET` | Your Autotask API secret |

### Optional

| Variable | Description |
|---|---|
| `AUTOTASK_API_URL` | Override the default Autotask API endpoint |
| `LOG_LEVEL` | Logging level (default: `info`) |
| `LOG_FORMAT` | Log format (default: `simple`) |
| `NODE_ENV` | Node environment (default: `production`) |

See `.env.example.txt` for the full template.

### Registry Metadata (Secret Handling)

Both `_meta.json` and the SKILL.md frontmatter now declare required env vars with `secret: true` flags. This allows the skill registry/platform to:

- **Validate** that required credentials are configured before launching
- **Enforce masking** of secret values in logs, UI, and agent output
- **Distinguish** secrets from plain configuration (e.g. `LOG_LEVEL` is not secret, `AUTOTASK_SECRET` is)
- **Audit** which skills require credential access

Skill authors publishing to the registry should include an `env` block in `_meta.json` (and optionally in the SKILL.md frontmatter) to opt into platform-level secret enforcement.

## Security

### Agent Guardrails

SKILL.md includes mandatory security rules that agents must follow when executing this skill:

- **No credential access** — Agents must never read, display, log, or output the `.env` file
- **No variable expansion** — Agents must never run `$EDITOR` or any shell-variable-expanded command
- **No external transmission** — Credentials must never be sent to any destination other than `127.0.0.1:8080`
- **Command allowlist** — Agents may only execute the specific scripts and commands listed in SKILL.md
- **Refusal policy** — If asked to show or share credentials, agents must refuse and instruct the user to inspect `.env` manually

### Credential Protection

- **File permissions** — `.env` is created with `chmod 600` (owner-only read/write)
- **Git exclusion** — `.env` is gitignored to prevent accidental commits
- **No duplication** — Agents are prohibited from copying or moving the `.env` file

### Container Hardening

- **Localhost-only binding** — Port 8080 is bound to `127.0.0.1`, not exposed externally
- **Read-only filesystem** — Container filesystem is mounted read-only (`read_only: true`)
- **Dropped capabilities** — All Linux capabilities are dropped (`cap_drop: ALL`)
- **No privilege escalation** — `no-new-privileges` security option enabled
- **Tmpfs for temp files** — `/tmp` is mounted as tmpfs with 64 MB limit, noexec, nosuid
- **Resource limits** — Memory capped at 512 MB, CPU capped at 1 core, max 64 PIDs
- **Log rotation** — Container logs limited to 3 files of 10 MB each

### Supply Chain Verification

- **Digest pinning** — Pin a known-good image digest with `scripts/mcp_pin_digest.sh`
- **Update verification** — `mcp_update.sh` refuses to restart if pulled digest doesn't match pin
- **No crontab modification** — Scheduled updates use macOS LaunchAgent or Linux systemd user timers

## Project Structure

```
autotask-mcp/
├── SKILL.md              # Skill definition for MCP clients
├── README.md             # This file
├── docker-compose.yml    # Service configuration
├── .env.example.txt      # Environment variable template
├── .gitignore            # Excludes .env, .pinned-digest, and logs/
├── .pinned-digest        # Pinned image digest (created by mcp_pin_digest.sh)
├── _meta.json            # Skill metadata
├── logs/                 # Update and cron logs (gitignored)
└── scripts/
    ├── mcp_pull.sh       # Pull Docker image
    ├── mcp_up.sh         # Start service
    ├── mcp_down.sh       # Stop service
    ├── mcp_logs.sh       # Tail logs
    ├── mcp_update.sh     # Check for updates (with digest verification)
    ├── mcp_pin_digest.sh # Pin current image digest
    ├── cron_install.sh   # Install weekly update (LaunchAgent/systemd)
    └── cron_uninstall.sh # Remove weekly update schedule
```

## Upstream

- Repository: https://github.com/asachs01/autotask-mcp
- Docker Image: `ghcr.io/asachs01/autotask-mcp:latest`
