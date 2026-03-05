---
name: memento
description: Local persistent memory for OpenClaw agents. Captures conversations, extracts structured facts via LLM, and auto-recalls relevant knowledge before each turn. Privacy-first, all stored data stays local in SQLite.
metadata:
  version: "0.6.0"
  author: braibaud
  license: MIT
  repository: https://github.com/braibaud/Memento
  openclaw:
    emoji: "🧠"
    kind: plugin
    requires:
      node: ">=18.0.0"
      optionalEnv:
        - name: ANTHROPIC_API_KEY
          when: "Using anthropic/* models for extraction"
        - name: OPENAI_API_KEY
          when: "Using openai/* models for extraction"
        - name: MISTRAL_API_KEY
          when: "Using mistral/* models for extraction"
        - name: MEMENTO_API_KEY
          when: "Generic fallback for any provider"
        - name: CLAUDE_CODE_OAUTH_TOKEN
          when: "OpenClaw OAuth token for model routing (auto-used when running inside OpenClaw)"
        - name: MEMENTO_WORKSPACE_MAIN
          when: "Migration only: path to agent workspace for bootstrapping"
        - name: MEMENTO_AGENT_PATHS
          when: "Deep consolidation CLI: explicit agent:path mappings"
      dataFiles:
        - path: "~/.engram/conversations.sqlite"
          purpose: "Main database — conversations, facts, embeddings (local only, never uploaded)"
        - path: "~/.engram/segments/*.jsonl"
          purpose: "Human-readable conversation backups (local only)"
        - path: "~/.engram/migration-config.json"
          purpose: "Optional: agent workspace paths for one-time migration bootstrap"
    install:
      - id: npm
        kind: node
        package: "@openclaw/memento"
        label: "Install Memento plugin (npm)"
    extensions:
      - "./src/index.ts"
  keywords:
    - memory
    - knowledge-base
    - recall
    - conversation
    - extraction
    - embeddings
    - sqlite
    - privacy
    - local
    - cross-agent
---

# Memento — Local Persistent Memory for OpenClaw Agents

Memento gives your agents long-term memory. It captures conversations, extracts structured facts using an LLM, and auto-injects relevant knowledge before each AI turn.

**All stored data stays on your machine — no cloud sync, no subscriptions.** Extraction uses your configured LLM provider; use a local model (Ollama) for fully air-gapped operation.

> ⚠️ **Privacy note:** When `autoExtract` is enabled, conversation segments are sent to your configured LLM provider for fact extraction. If you use a cloud provider (Anthropic, OpenAI, Mistral), that text leaves your machine. For fully local operation, set `extractionModel` to `ollama/<model>` and keep Ollama running locally.

## What It Does

1. **Captures** every conversation turn, buffered per session
2. **Extracts** structured facts (preferences, decisions, people, action items) via configurable LLM (opt-in — see Privacy section)
3. **Recalls** relevant facts before each AI turn using FTS5 keyword search + optional semantic embeddings (BGE-M3)
4. **Respects privacy** — facts are classified as `shared`, `private`, or `secret` based on content, with hard overrides for sensitive categories (medical, financial, credentials)
5. **Cross-agent knowledge** — shared facts flow between agents with provenance tags; private/secret facts never cross boundaries

## Quick Start

Install the plugin, restart your gateway, and Memento starts capturing automatically. Extraction is **off by default** — enable it explicitly when ready.

### Optional: Semantic Search

Download a local embedding model for richer recall:

```bash
mkdir -p ~/.node-llama-cpp/models
curl -L -o ~/.node-llama-cpp/models/bge-m3-Q8_0.gguf \
  "https://huggingface.co/gpustack/bge-m3-GGUF/resolve/main/bge-m3-Q8_0.gguf"
```

## Environment Variables

All environment variables are **optional** — you only need the one matching your chosen LLM provider:

| Variable | When Needed |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Using `anthropic/*` models for extraction |
| `OPENAI_API_KEY` | Using `openai/*` models for extraction |
| `MISTRAL_API_KEY` | Using `mistral/*` models for extraction |
| `MEMENTO_API_KEY` | Generic fallback for any provider |
| `MEMENTO_WORKSPACE_MAIN` | Migration only: path to agent workspace for bootstrapping |

No API key needed for `ollama/*` models (local inference).

## Configuration

Add to your `openclaw.json` under `plugins.entries.memento.config`:

```json
{
  "memento": {
    "autoCapture": true,
    "extractionModel": "anthropic/claude-sonnet-4-6",
    "extraction": {
      "autoExtract": true,
      "minTurnsForExtraction": 3
    },
    "recall": {
      "autoRecall": true,
      "maxFacts": 20,
      "crossAgentRecall": true,
      "autoQueryPlanning": false
    }
  }
}
```

> **`autoExtract: true`** is an explicit opt-in (default: `false`). When enabled, conversation segments are sent to the configured `extractionModel` for LLM-based fact extraction. Omit or set to `false` to keep everything local.

> **`autoQueryPlanning: true`** is an explicit opt-in (default: `false`). When enabled, a fast LLM call runs before each recall search to expand the query with synonyms and identify relevant categories — improving precision at the cost of one extra LLM call per turn.

## Data Storage

Memento stores all data locally:

| Path | Contents |
|------|----------|
| `~/.engram/conversations.sqlite` | Main database: conversations, facts, embeddings |
| `~/.engram/segments/*.jsonl` | Human-readable conversation backups |
| `~/.engram/migration-config.json` | Optional: migration workspace paths (only for bootstrapping) |

## Privacy & Data Flow

| Feature | Data leaves machine? | Details |
|---------|---------------------|---------|
| `autoCapture` (default: `true`) | ❌ No | Writes to local SQLite + JSONL only |
| `autoExtract` (default: `false`) | ⚠️ Yes, if cloud LLM | Sends conversation text to configured provider. Use `ollama/*` for local. |
| `autoRecall` (default: `true`) | ❌ No | Reads from local SQLite only |
| Secret facts | ❌ Never | Filtered from extraction context — never sent to any LLM |
| Migration | ❌ No | Reads local workspace files, writes to local SQLite |

## Migration (Bootstrap from Existing Memory Files)

Migration is an **optional, one-time** process to seed Memento from existing agent memory/markdown files. It is user-initiated only — never runs automatically.

### What it reads

Migration reads **only** the files you explicitly list in the config. It does **not** scan your filesystem, read arbitrary files, or access anything outside the configured paths.

### Setup

1. Create `~/.engram/migration-config.json` or set `MEMENTO_WORKSPACE_MAIN`:

```json
{
  "agents": [
    {
      "agentId": "main",
      "workspace": "/path/to/your-workspace",
      "paths": ["MEMORY.md", "memory/*.md"]
    }
  ]
}
```

2. **Always dry-run first** to verify exactly which files will be read:

```bash
npx tsx src/extraction/migrate.ts --all --dry-run
```

The dry-run prints every file path it would read — review this before proceeding.

3. Run the actual migration:

```bash
npx tsx src/extraction/migrate.ts --all
```

### Security notes

- Migration only reads files matching the glob patterns you configure
- Extracted facts inherit visibility classification (shared/private/secret)
- Secret-classified facts are **never** sent to cloud LLM providers
- Migration config file is optional — if absent, migration is completely inert
- The migration script has no network access beyond the configured extraction LLM

## Architecture

- **Capture layer** — hooks `message:received` + `message:sent`, buffers multi-turn segments
- **Extraction layer** — async LLM extraction with deduplication, occurrence tracking, temporal state transitions (`previous_value`), and knowledge graph relations (including causal edges with `causal_weight`)
- **Storage layer** — SQLite schema v7 (better-sqlite3) with FTS5 full-text search + optional vector embeddings; knowledge graph (`fact_relations` with `causal_weight`), multi-layer clusters, and temporal transition tracking (`previous_value`)
- **Recall layer** — optional LLM query planning pre-pass (`autoQueryPlanning`), multi-factor scoring (recency × frequency × category weight), 1-hop graph traversal with causal edge 1.5× boost, injected via `before_prompt_build` hook

## Requirements

- OpenClaw 2026.2.20+
- Node.js 18+
- An API key for your preferred LLM provider (for extraction — not needed if extraction is disabled or using Ollama)
- Optional: GPU for accelerated embedding search (falls back to CPU gracefully)

## Install

```bash
# From ClawHub
clawhub install memento

# Or for local development
git clone https://github.com/braibaud/Memento
cd Memento
npm install
```

Note: `better-sqlite3` includes native bindings that compile during `npm install`. This is expected behavior for SQLite access.
