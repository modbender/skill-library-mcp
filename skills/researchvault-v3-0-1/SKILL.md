---
name: researchvault
description: "Local-first research orchestration engine. Manages state, synthesis, and optional background services (MCP/Watchdog)."
homepage: https://github.com/lraivisto/ResearchVault
disable-model-invocation: true
user-invocable: true
metadata:
  openclaw:
    emoji: "🦞"
    install:
      - id: vault-venv
        kind: exec
        command: python3 -m venv .venv && . .venv/bin/activate && pip install -e .
        label: Initialize ResearchVault (Standard)
    requires:
      python: ">=3.13"
      env:
        RESEARCHVAULT_DB:
          description: "Optional: Custom path to the SQLite database file."
          required: false
        BRAVE_API_KEY:
          description: "Optional: Brave Search API key."
          required: false
        SERPER_API_KEY:
          description: "Optional: Serper API key."
          required: false
        SEARXNG_BASE_URL:
          description: "Optional: SearXNG base URL."
          required: false
        RESEARCHVAULT_PORTAL_TOKEN:
          description: "Optional: static portal token. If unset, start_portal.sh sources/generates .portal_auth and exports this env var."
          required: false
        RESEARCHVAULT_PORTAL_SCAN_OPENCLAW:
          description: "Optional: set to '1' to request OpenClaw workspace DB scan."
          required: false
        RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS:
          description: "Optional: comma-separated absolute DB roots. Default: ~/.researchvault,/tmp."
          required: false
        RESEARCHVAULT_PORTAL_INJECT_SECRETS:
          description: "Optional: set to '1' to inject configured provider env vars into vault subprocesses."
          required: false
        RESEARCHVAULT_PORTAL_STATE_DIR:
          description: "Optional: portal state directory (default ~/.researchvault/portal)."
          required: false
        RESEARCHVAULT_PORTAL_HOST:
          description: "Optional: backend bind host."
          required: false
        RESEARCHVAULT_PORTAL_PORT:
          description: "Optional: backend bind port."
          required: false
        RESEARCHVAULT_PORTAL_FRONTEND_HOST:
          description: "Optional: frontend bind host."
          required: false
        RESEARCHVAULT_PORTAL_FRONTEND_PORT:
          description: "Optional: frontend bind port."
          required: false
        RESEARCHVAULT_PORTAL_CORS_ORIGINS:
          description: "Optional: comma-separated CORS origins for backend."
          required: false
        RESEARCHVAULT_PORTAL_RELOAD:
          description: "Optional: set to 'true' for backend auto-reload."
          required: false
        RESEARCHVAULT_PORTAL_COOKIE_SECURE:
          description: "Optional: set to 'true' to mark auth cookie Secure."
          required: false
        RESEARCHVAULT_PORTAL_PID_DIR:
          description: "Optional: start_portal.sh PID/log directory."
          required: false
        RESEARCHVAULT_PORTAL_SHOW_TOKEN:
          description: "Optional: set to '1' to print tokenized portal URLs."
          required: false
        RESEARCHVAULT_SEARCH_PROVIDERS:
          description: "Optional: search provider order override."
          required: false
        RESEARCHVAULT_WATCHDOG_INGEST_TOP:
          description: "Optional: watchdog ingest top-k override."
          required: false
        RESEARCHVAULT_VERIFY_INGEST_TOP:
          description: "Optional: verify ingest top-k override."
          required: false
        RESEARCHVAULT_MCP_TRANSPORT:
          description: "Optional: MCP server transport override."
          required: false
        REQUESTS_CA_BUNDLE:
          description: "Optional: custom CA bundle for HTTPS verification."
          required: false
        SSL_CERT_FILE:
          description: "Optional: custom CA certificate file."
          required: false
---

# ResearchVault 🦞

**Local-first research orchestration engine.**

ResearchVault manages persistent state, synthesis, and autonomous verification for agents.

## Security & Privacy (Local First)

- **Local Storage**: All data is stored in a local SQLite database (~/.researchvault/research_vault.db). No cloud sync.
- **Network Transparency**: Outbound connections occur ONLY for user-requested research or Brave Search (if configured). 
- **SSRF Hardening**: Strict internal network blocking by default. Local/private IPs (localhost, 10.0.0.0/8, etc.) are blocked. Use `--allow-private-networks` to override.
- **Manual Opt-in Services**: Background watchers and MCP servers are in `scripts/services/` and must be started manually.
- **Strict Control**: `disable-model-invocation: true` prevents the model from autonomously starting background tasks.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Quick Start

1. **Initialize Project**:
   ```bash
   python scripts/vault.py init --objective "Analyze AI trends" --name "Trends-2026"
   ```

2. **Ingest Data**:
   ```bash
   python scripts/vault.py scuttle "https://example.com" --id "trends-2026"
   ```

3. **Autonomous Strategist**:
   ```bash
   python scripts/vault.py strategy --id "trends-2026"
   ```

## Portal (Manual Opt-In)

Start the portal explicitly:

```bash
./start_portal.sh
```

- Backend: `127.0.0.1:8000`
- Frontend: `127.0.0.1:5173`
- Backend auth strictly uses `RESEARCHVAULT_PORTAL_TOKEN`
- `./start_portal.sh` loads/generates `.portal_auth` and exports `RESEARCHVAULT_PORTAL_TOKEN` before backend launch
- Token login: URL hash `#token=<token>` (token from `.portal_auth`)
- Allowed DB roots are controlled by `RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS` (default `~/.researchvault,/tmp`)
- OpenClaw workspace scan is effective only when `RESEARCHVAULT_PORTAL_SCAN_OPENCLAW=1` and `~/.openclaw/workspace` is inside allowed DB roots
- Provider secrets are env-only (`BRAVE_API_KEY`, `SERPER_API_KEY`, `SEARXNG_BASE_URL`) and injected into subprocesses only when `RESEARCHVAULT_PORTAL_INJECT_SECRETS=1`
- Both hosts are supported for browser access:
  - `http://127.0.0.1:5173/#token=<token>`
  - `http://localhost:5173/#token=<token>`

Operational commands:

```bash
./start_portal.sh --status
./start_portal.sh --stop
```

Security parity with CLI:
- SSRF blocking is on by default (private/local/link-local targets denied).
- Portal toggle **Allow private networks** is equivalent to CLI `--allow-private-networks`.

## Optional Services (Manual Start)

- **MCP Server**: `python scripts/services/mcp_server.py`
- **Watchdog**: `python scripts/services/watchdog.py --once`

## Provenance & Maintenance

- **Maintainer**: lraivisto
- **License**: MIT
- **Issues**: [GitHub Issues](https://github.com/lraivisto/ResearchVault/issues)
- **Security**: See [SECURITY.md](SECURITY.md)
