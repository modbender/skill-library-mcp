# ResearchVault 🦞

**The local-first orchestration engine for high-velocity AI research.**

ResearchVault is a local-first state manager and orchestration framework for long-running investigations. It lets you persist projects, findings, evidence, and automation state into a local SQLite "Vault".

Vault is built CLI-first to close the loop between planning, ingestion, verification, and synthesis.

## 🛡️ Security & Privacy

ResearchVault is designed with a **Local-First, Privacy-First** posture:

*   **Local Persistence**: All research data stays on your machine in a local SQLite database (~/.researchvault/research_vault.db). No telemetry or auto-sync.
*   **SSRF Protection**: Strict internal network blocking by default. The tool resolves DNS and blocks private/local/link-local IPs (RFC1918, 127.0.0.1, 169.254.169.254, etc.).
*   **Network Transparency**: Outbound connections are limited to user-requested scuttling or Brave Search API (if configured).
*   **Zero Auto-Start**: No background processes or servers start during installation. Services must be explicitly invoked from `scripts/services/`.
*   **Restricted Model Invocation**: The `disable-model-invocation: true` flag prevents the AI from autonomously triggering side-effects without a direct user prompt.

## 🚀 Installation

### Standard (Recommended)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 🌐 Portal (v3)

Run the portal manually (nothing auto-starts in the background):

```bash
./start_portal.sh
```

- Backend binds to `127.0.0.1:8000`
- Frontend binds to `127.0.0.1:5173`
- Backend auth strictly uses `RESEARCHVAULT_PORTAL_TOKEN`.
- `./start_portal.sh` loads token from `.portal_auth` (or generates it) and exports `RESEARCHVAULT_PORTAL_TOKEN` before launching the backend.
- Use either host for login:
  - `http://127.0.0.1:5173/#token=<token>`
  - `http://localhost:5173/#token=<token>`
- Tokenized URLs are hidden in terminal output by default; read `.portal_auth` (chmod 600) to paste the token manually, or set `RESEARCHVAULT_PORTAL_SHOW_TOKEN=1` to print tokenized URLs.
- Allowed DB roots are constrained by `RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS` (default `~/.researchvault,/tmp`).
- OpenClaw workspace DB discovery is disabled by default; it only becomes effective when `RESEARCHVAULT_PORTAL_SCAN_OPENCLAW=1` and `~/.openclaw/workspace` is inside allowed DB roots.
- Search provider secrets are env-only (read-only in Portal): configure `BRAVE_API_KEY`, `SERPER_API_KEY`, and/or `SEARXNG_BASE_URL` in the backend process environment.
- Provider secrets are injected into vault subprocesses only when `RESEARCHVAULT_PORTAL_INJECT_SECRETS=1`.

Process controls:

```bash
./start_portal.sh --status
./start_portal.sh --stop
```

Ingest SSRF behavior matches CLI defaults:
- Private/local/link-local targets are blocked by default.
- Portal checkbox **Allow private networks** maps to CLI `--allow-private-networks`.

## 🛠️ Key Workflows

### 1. Project Management
```bash
python scripts/vault.py init --id "ai-research" --name "AI Research" --objective "Monitor 2026 trends"
```

### 2. Multi-Source Ingestion
```bash
python scripts/vault.py scuttle "https://example.com" --id "ai-research"
```

### 3. Synthesis & Verification
```bash
python scripts/vault.py synthesize --id "ai-research"
python scripts/vault.py verify run --id "ai-research"
```

### 4. Optional Services (Manual Opt-in)
*   **MCP Server**: `python scripts/services/mcp_server.py`
*   **Watchdog**: `python scripts/services/watchdog.py`

## 📦 Dependencies

*   `requests` & `beautifulsoup4`: Targeted web ingestion.
*   `rich`: CLI output formatting.
*   `mcp`: Standard protocol for agent-tool communication.
*   `pytest`: Local integrity verification.

## ⚖️ License & Provenance

- **Maintainer**: lraivisto
- **License**: MIT
- **Issues**: [GitHub Issues](https://github.com/lraivisto/ResearchVault/issues)
- **Releases**: [Changelog](CHANGELOG.md)

---
*This project is 100% developed by AI agents (OpenClaw / Google Antigravity / OpenAI Codex), carefully orchestrated and reviewed by **Luka Raivisto**.*
