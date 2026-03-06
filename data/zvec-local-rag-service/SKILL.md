---
name: zvec-local-rag-service
description: Operate an always-on local semantic-search service using zvec + Ollama embeddings. Use when you need to ingest .txt/.md files, run meaning-based search via HTTP endpoints (/health, /ingest, /search), and keep the service running on macOS (launchd) or manually. Includes service code, launchd template, and management scripts.
metadata:
  openclaw:
    requires:
      bins: ["node", "npm", "ollama", "curl"]
    install:
      - id: zvec-deps
        kind: npm
        package: "@zvec/zvec"
        label: "Install zvec Node binding"
---

# zvec-local-rag-service

Run local RAG search with Ollama embeddings and zvec.

## Included files

- `scripts/rag-service.mjs` → HTTP service implementation
- `scripts/manage.sh` → bootstrap/start/stop/restart/health/ingest/search
- `references/launchd.plist.template` → macOS LaunchAgent template

## Prerequisites

- Node.js 18+
- Ollama daemon running
- Embedding model (default): `mxbai-embed-large`

Prepare model once:

```bash
ollama pull mxbai-embed-large
```

## Quick start

From the skill directory:

```bash
scripts/manage.sh bootstrap
scripts/manage.sh install-launchd   # writes plist, inspect once
scripts/manage.sh start
scripts/manage.sh health
```

Ingest and search:

```bash
scripts/manage.sh ingest ./docs
scripts/manage.sh search "your query"
```

## Install + smoke test (copy/paste)

```bash
# 1) prerequisites
ollama pull mxbai-embed-large

# 2) bootstrap and start service
scripts/manage.sh bootstrap
scripts/manage.sh install-launchd
scripts/manage.sh start

# 3) verify health
scripts/manage.sh health

# 4) create tiny test corpus
mkdir -p ./docs
cat > ./docs/sample.md <<'EOF'
Zvec + Ollama enables local semantic search.
EOF

# 5) ingest + query
scripts/manage.sh ingest ./docs
scripts/manage.sh search "local semantic search with ollama"
```

## Endpoints

- `GET /health`
- `POST /ingest` with `{ "dir": "./docs", "reset": true }`
- `POST /search` with `{ "query": "...", "topk": 5 }`

## Persistence (macOS launchd)

Install and enable LaunchAgent:

```bash
scripts/manage.sh install-launchd
scripts/manage.sh start
scripts/manage.sh status
```

Remove LaunchAgent:

```bash
scripts/manage.sh uninstall-launchd
```

Always inspect generated plist before enabling persistence:
- `~/Library/LaunchAgents/com.openclaw.zvec-rag-service.plist`

## Config via env vars

- `RAG_HOST` (default `127.0.0.1`)
- `RAG_PORT` (default `8787`)
- `OLLAMA_URL` (default `http://127.0.0.1:11434`)
- `OLLAMA_EMBED_MODEL` (default `mxbai-embed-large`)
- `RAG_BASE_DIR` (default `~/.openclaw/data/zvec-rag-service`)
- `ALLOW_REMOTE_OLLAMA` (default `false`, blocks non-local OLLAMA_URL)
- `ALLOW_NON_LOOPBACK_HOST` (default `false`, blocks externally reachable bind host)

## Notes

- Secure defaults: loopback-only service + loopback-only Ollama.
- Remote embedding/host binding require explicit opt-in env flags.
- `launchd` operations are macOS-specific. On non-macOS, run with `scripts/manage.sh start` (manual mode).
