# ResearchVault 🦞

**The local-first orchestration engine for high-velocity AI research.**

ResearchVault is a local-first state manager and orchestration framework for long-running investigations. It lets you persist projects, findings, evidence, instrumentation, and automation state into a local SQLite "Vault" so research can survive across sessions.

Vault is built CLI-first to close the loop between planning, ingestion, verification, and synthesis.

## ✨ Core Features

*   **The Vault (SQLite)**: A persistent local ledger stored at `~/.researchvault/research_vault.db` (override via `RESEARCHVAULT_DB`).
*   **Normalized Evidence Core**: Scalable storage for `artifacts`, `findings`, and `links` (graph-ready).
*   **Divergent Reasoning**: First-class `branches` + `hypotheses` so agents can explore competing explanations without contaminating the main line.
*   **Cross-Artifact Synthesis**: Deterministic local embeddings (feature hashing; no model downloads) + similarity links (`links`) across findings and artifacts.
*   **Active Verification Protocol**: Auto-generated `verification_missions` for low-confidence or `unverified` findings (can run via Brave Search if configured).
*   **MCP Server**: Expose the Vault over MCP (`python -m scripts.vault mcp` / `python -m scripts.mcp_server`).
*   **Watchdog Mode**: Periodic ingestion for watched URL targets and query targets.
*   **Unified Ingestion Engine**: Modular connectors for automated research capture.
*   **Instrumentation 2.0**: Every research event tracks **Confidence** (0.0-1.0), **Source**, and **Tags**.
*   **Multi-Source Support**: 
    *   **Web**: Basic HTML paragraph extraction (SSRF-protected).
    *   **Reddit**: Post + top comment via the public `.json` endpoint.
    *   **YouTube**: Metadata-only extraction (title/description) without API keys.
    *   **Moltbook**: Demo connector to exercise the suspicion protocol (always low-confidence + `unverified` tag).
    *   **Grokipedia**: Example API connector (requires a reachable API endpoint).
*   **Suspicion Protocol 2.0**: Hardened logic for low-trust sources. Moltbook scans are forced to low-confidence (`0.55`) and tagged `unverified`.
*   **Search Cache + Dedup**: Search results cached by query hash; watch targets and verification missions are deduplicated.
*   **SSRF Safety**: Robust URL validation blocks internal network probes and private IP ranges.
*   **Hardened Logic**: Versioned database migrations and a comprehensive `pytest` suite.

## ⚙️ Configuration

*   `RESEARCHVAULT_DB`: Override the SQLite path (default: `~/.researchvault/research_vault.db`).
*   `BRAVE_API_KEY`: Enables live Brave search, verification mission execution, and query watch targets (otherwise these paths must use cached or manually-injected search results).

## 🚀 Workflows

### 1. Project Management
Initialize a project, set objectives, and assign priority levels.
```bash
uv run python -m scripts.vault init --id "metal-v1" --name "Suomi Metal" --objective "Rising underground bands" --priority 5
```

### 2. Multi-Source Ingestion
Use the unified `scuttle` command to ingest data from any supported source (Reddit, YouTube, Grokipedia, Web).
```bash
uv run python -m scripts.vault scuttle "https://www.youtube.com/watch?v=..." --id "metal-v1"
```

### 3. Divergent Reasoning (Branches + Hypotheses)
```bash
uv run python -m scripts.vault branch create --id "metal-v1" --name "alt-hypothesis" --hypothesis "The trend is label-driven, not organic."
uv run python -m scripts.vault hypothesis add --id "metal-v1" --branch "alt-hypothesis" --statement "Streaming growth is driven by playlist placement." --conf 0.55
uv run python -m scripts.vault insight --id "metal-v1" --add --branch "alt-hypothesis" --title "Counter-signal" --content "..." --tags "unverified"
```

### 4. Cross-Artifact Synthesis
```bash
uv run python -m scripts.vault synthesize --id "metal-v1" --threshold 0.78 --top-k 5
```

### 5. Verification Missions
```bash
uv run python -m scripts.vault verify plan --id "metal-v1" --threshold 0.7 --max 20
uv run python -m scripts.vault verify list --id "metal-v1" --status open
uv run python -m scripts.vault verify run --id "metal-v1" --limit 5
```

### 6. Watchdog Mode
```bash
uv run python -m scripts.vault watch add --id "metal-v1" --type url --target "https://example.com" --interval 3600 --tags "seed"
uv run python -m scripts.vault watch add --id "metal-v1" --type query --target "rising underground metal bands finland" --interval 21600
uv run python -m scripts.vault watchdog --once --limit 10
```

### 7. MCP Server
```bash
uv run python -m scripts.vault mcp --transport stdio
# or:
uv run python -m scripts.mcp_server
```

### 8. Export & Reporting
Ship research summaries to Markdown or JSON for external use or agent review.
```bash
uv run python -m scripts.vault export --id "metal-v1" --format markdown --output summary.md
```

### 9. Verification & Testing
Run the integrated test suite to verify system integrity.
```bash
uv run pytest
```

### 10. Monitoring
View sorted project lists, high-level summaries, and detailed event logs.
```bash
uv run python -m scripts.vault list
uv run python -m scripts.vault summary --id "metal-v1"
uv run python -m scripts.vault status --id "metal-v1"
```

## 🛠️ Development & Environment

ResearchVault is formalized using **uv** for dependency management and Python >=3.13.

*   **Core Architecture**: Modular design separating Interface (`vault.py`), Logic (`core.py`), and Storage (`db.py`).
*   **Oracle Loops**: Complex refactors use high-reasoning sub-agents.
*   **Main-Line Evolution**: Atomic improvements are committed directly to `main`.

---
*This project is 100% developed by AI agents (OpenClaw / Google Antigravity / OpenAI Codex), carefully orchestrated and reviewed by **Luka Raivisto**.*
