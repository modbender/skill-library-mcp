# Memento — Local Persistent Memory for OpenClaw Agents

**Memento** gives OpenClaw agents a long-term memory — structured, private, and stored entirely on your machine. All stored data stays local — no cloud sync, no subscriptions. Extraction uses your configured LLM provider; use a local model (Ollama) for fully air-gapped operation.

> ⚠️ **Privacy note:** When `autoExtract` is enabled, conversation segments are sent to your configured LLM provider for fact extraction. Memento uses OpenClaw's built-in model routing — it inherits whichever model you have configured for your agent (including fallbacks). If you use a cloud provider (Anthropic, OpenAI, Mistral), that text leaves your machine. For fully local operation, configure your OpenClaw agent to use Ollama.

---

## Features

- **📥 Capture** — buffers every conversation turn per session, auto-flushes on pause or session end
- **🧠 Extraction** — asynchronously extracts structured facts (preferences, decisions, people, etc.) using the configured LLM; **history-agnostic** — existing facts are NOT passed to the LLM (Phase 1)
- **🔍 Recall** — injects relevant facts before each AI turn via FTS5 keyword search + optional semantic embedding search
- **🔒 Privacy-first** — facts are classified by visibility (`shared` / `private` / `secret`); secret facts never leave your machine or cross agent boundaries
- **🌐 Cross-agent KB** — shared facts from multiple agents are surfaced with provenance tags in recall
- **📊 Temporal intelligence** — recency, frequency, and category weights govern recall ranking; `previous_value` shown when a fact has changed
- **🔗 Knowledge graph** — typed weighted relations between facts (`related_to`, `elaborates`, `contradicts`, `supports`, `caused_by`, `part_of`, `precondition_of`) with 1-hop graph traversal during recall; causal edges get a **1.5× score boost**; Phase 3 background sweep auto-builds relations from embedding similarity
- **🔮 Query planning** — optional LLM pre-pass before retrieval expands queries with synonyms and identifies relevant categories/entities for higher precision recall
- **📦 Multi-layer memory** — facts cluster into higher-level summaries; incremental consolidation after each extraction + periodic deep "sleep" passes with confidence decay

---

## Architecture

```
                ┌──────────────────────────────────────────────────────────────┐
                │                       OpenClaw Agent                         │
                │                                                              │
  Conversation  │   message_received ──► ConversationBuffer ──► SegmentWriter  │
  Flow          │                                                     │        │
                │                                           ExtractionTrigger  │
                │                                                     │        │
                │                                           extractFacts (LLM) │
                │                                                     │        │
                │                                     processExtractedFacts    │
                │                                          │          │        │
                │                              fact_relations    SQLite DB      │
                │                              (graph edges,    (facts, FTS5,  │
                │                              causal_weight)    previous_val) │
                │                                          │          │        │
                │                              incrementalConsolidate          │
                │                              (cluster assignment)            │
                │                                                              │
  Deep Sleep    │   cron (3 AM) ──► deepConsolidate ──► decay + merge + refresh│
  Phase 3       │   cron (3 AM) ──► relationSweep ──► embedding sim → typed edges   │
                │                                                              │
  Recall        │   before_prompt_build ──► [planQuery?] ──► searchRelevantFacts│
                │                           + 1-hop graph traversal ──► inject │
                └──────────────────────────────────────────────────────────────┘
```

### Key Modules

| Module | Description |
|--------|-------------|
| `src/index.ts` | Plugin entry point — registers hooks and services |
| `src/capture/buffer.ts` | In-memory session buffer with auto-flush |
| `src/capture/writer.ts` | Persists segments to SQLite + JSONL |
| `src/extraction/extractor.ts` | **Phase 1**: LLM-based fact extraction — history-agnostic (no existing facts passed); prompt loaded from `prompts/extraction.md` at runtime |
| `src/extraction/embedded-runner.ts` | OpenClaw model routing — delegates LLM calls to `runEmbeddedPiAgent` |
| `src/extraction/deduplicator.ts` | **Phase 2**: embedding-based dedup — cosine similarity classifies each extracted fact as duplicate (≥0.97), update (≥0.82), or new (<0.82); embeds new facts immediately |
| `src/extraction/trigger.ts` | Async extraction scheduling with rate limiting |
| `src/extraction/classifier.ts` | Visibility classification with hard overrides |
| `src/recall/search.ts` | FTS5 + semantic search with multi-factor scoring; optional `planQuery` pre-pass; causal edge 1.5× boost |
| `src/recall/context-builder.ts` | Formats recalled facts for injection; shows `previous_value` for changed facts |
| `src/storage/db.ts` | SQLite database layer (better-sqlite3) |
| `src/storage/embeddings.ts` | Local embedding engine via node-llama-cpp |
| `src/storage/schema.ts` | SQLite schema v7, migrations, row types |
| `src/consolidation/consolidator.ts` | Incremental consolidation — assigns facts to clusters after extraction |
| `src/consolidation/deep-consolidator.ts` | Deep "sleep" consolidation — decay, cluster merging, summary refresh |
| `src/consolidation/relation-sweep.ts` | **Phase 3**: background relation linking — pairwise embedding similarity → typed graph edges; same-category ≥0.85 auto-linked; cross-category 0.72–0.88 → Haiku batch classification |
| `src/cli/deep-consolidate.ts` | CLI entry point for deep consolidation (cron-compatible) |
| `prompts/extraction.md` | LLM prompt for fact extraction — edit to tune quality without recompiling |
| `prompts/relation-classify.md` | Haiku prompt for relation type classification (Phase 3) |
| `src/config.ts` | Plugin configuration with defaults |
| `src/types.ts` | Shared TypeScript types |

### Schema (v7)

The SQLite database at `~/.engram/conversations.sqlite` uses schema version 7:

| Table | Purpose |
|-------|---------|
| `conversations` | Raw conversation segments (one row per flushed buffer) |
| `messages` | Individual messages within a segment |
| `facts` | Extracted knowledge base — includes `previous_value` (v7) for temporal transitions |
| `fact_occurrences` | Temporal tracking of each fact mention |
| `extraction_log` | Which conversations have been processed |
| `fact_relations` | Knowledge graph edges — includes `causal_weight` (v7) for causal edge boosting |
| `fact_clusters` | Higher-level memory clusters (Layer 2+) |
| `cluster_members` | Membership edges linking facts → clusters |
| `ingest_tokens` | Auth tokens for remote JSONL ingest |
| `ingest_file_log` | Dedup log for ingested files |

---

## Installation

Memento is a plugin for OpenClaw. Install it from the plugin directory:

```bash
openclaw plugin install @openclaw/memento
```

Or for local development, clone and link:

```bash
git clone https://github.com/openclaw/memento
cd memento
npm install
npm link
openclaw plugin link /path/to/memento
```

---

## Configuration

Add to your `openclaw.json` under `plugins.entries.memento.config`:

> **`extractionModel`** accepts any of these provider prefixes:
> `anthropic/` · `openai/` · `mistral/` · `ollama/` (or any OpenAI-compatible string as fallback).
> Set the matching API key env var: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `MISTRAL_API_KEY`.
> Ollama runs locally — no key needed.

```json
{
  "memento": {
    "autoCapture": true,
    "dataDir": ".engram",
    "extractionModel": "anthropic/claude-sonnet-4-6",
    "embeddingModel": "hf:BAAI/bge-m3-gguf",
    "agentDisplay": {
      "main": "Main Assistant",
      "medbot": "Medical Bot"
    },
    "extraction": {
      "autoExtract": true,
      "minTurnsForExtraction": 3,
      "maxExtractionsPerMinute": 10,
      "includeExistingFactsCount": 50
    },
    "recall": {
      "autoRecall": true,
      "maxFacts": 20,
      "maxContextChars": 4000,
      "minQueryLength": 5,
      "crossAgentRecall": true,
      "autoQueryPlanning": false
    }
  }
}
```

> **`autoExtract: true`** is an explicit opt-in (default: `false`). When enabled, conversation segments are sent to the configured `extractionModel` for LLM-based fact extraction. Omit or set to `false` to keep everything local (capture + recall still work via SQLite without any LLM calls).

### Configuration Reference

| Key | Default | Description |
|-----|---------|-------------|
| `autoCapture` | `true` | Buffer and persist all conversation messages |
| `dataDir` | `.engram` | Data directory (relative to workspace) |
| `extractionModel` | `anthropic/claude-sonnet-4-6` | LLM for fact extraction — supports `anthropic/`, `openai/`, `mistral/`, `ollama/` prefixes |
| `embeddingModel` | `hf:BAAI/bge-m3-gguf` | Local embedding model (HuggingFace URI or path) |
| `agentDisplay` | `{}` | Human-readable names for agents in cross-agent recall tags |
| `extraction.autoExtract` | `false` | **Opt-in**: automatically extract facts after each segment — sends conversation text to the configured LLM provider |
| `extraction.minTurnsForExtraction` | `3` | Skip very short segments |
| `extraction.maxExtractionsPerMinute` | `10` | Rate limit for LLM calls |
| `extraction.includeExistingFactsCount` | `50` | _(Deprecated — no longer used)_ Dedup is now handled by Phase 2 embedding similarity, not by the extraction LLM |
| `recall.autoRecall` | `true` | Inject relevant facts before each AI turn |
| `recall.maxFacts` | `20` | Maximum facts to inject per turn |
| `recall.maxContextChars` | `4000` | Maximum characters for the injected context block |
| `recall.crossAgentRecall` | `true` | Include shared facts from other agents |
| `recall.autoQueryPlanning` | `false` | **Opt-in**: run a fast LLM pre-pass to expand the query with synonyms/entities before FTS search — improves recall precision at the cost of an extra LLM call per turn |

---

## Local Development Setup

### Prerequisites

- Node.js 18+
- TypeScript 5.7+
- OpenClaw installed globally

### TypeScript path resolution

The `openclaw/plugin-sdk` module type declarations are resolved from the OpenClaw installation. After cloning:

```bash
# Option 1: npm link (recommended for local dev)
npm link openclaw

# Option 2: adjust tsconfig.json paths to point to your global install
# $(npm root -g)/openclaw/dist/plugin-sdk/index.d.ts
```

### Type-check

```bash
npx tsc --noEmit
```

---

## Fact Migration (Bootstrap from Existing Memory Files)

Migration is an **optional, one-time** process to seed Memento from existing agent memory/markdown files. It is user-initiated only — never runs automatically.

> **Tip:** Always run with `--dry-run` first to preview what will be imported without making any writes. Migration reads **only** the files you explicitly list in the config — it does not scan your filesystem or access anything outside the configured paths.

1. Create `~/.engram/migration-config.json`:

```json
{
  "agents": [
    {
      "agentId": "main",
      "workspace": "/home/yourname/your-workspace",
      "paths": ["MEMORY.md", "memory/*.md"]
    }
  ]
}
```

Or set `MEMENTO_WORKSPACE_MAIN` environment variable.

2. Run the migration:

```bash
# Dry run (no writes)
npx tsx src/extraction/migrate.ts --all --dry-run

# Process all agents
npx tsx src/extraction/migrate.ts --all

# Single agent
npx tsx src/extraction/migrate.ts --agent main
```

---

## Privacy & Security

| Feature | Data location | Leaves your machine? |
|---------|--------------|----------------------|
| `autoCapture: true` | SQLite + JSONL on disk | ❌ Never |
| Relation sweep (Phase 3) | Sends fact _summaries_ to Haiku for relation classification; **secret facts are never included** | ✅ Yes (unless using Ollama) |
| `autoExtract: true` | Sends conversation segments to `extractionModel` | ✅ Yes (unless using Ollama) |
| `autoRecall: true` | Reads from local SQLite | ❌ Never |
| `autoQueryPlanning: true` | Sends the user's message to `extractionModel` for query expansion | ✅ Yes (unless using Ollama) |
| Secret facts (`credentials`, `medical`, `financial`) | Filtered **before** extraction context | ❌ Never sent to LLM |

- **Secret facts** (`credentials`, `medical`, `financial`) are never sent to external APIs — they are filtered from the extraction dedup context before LLM calls
- **Private facts** stay within the agent that created them — they are never shared across agents
- **Shared facts** can appear in cross-agent recall (with provenance tags)
- All stored data lives locally in `~/.engram/conversations.sqlite` (or your configured `dataDir`)
- No cloud sync, telemetry, or external storage

**For fully local / air-gapped operation:** set `extractionModel` to `ollama/<model>` (e.g. `ollama/llama3`) and keep Ollama running on localhost. No API keys needed.

---

## Semantic Search (Embeddings)

Memento supports optional local semantic search via BGE-M3 (or any compatible GGUF embedding model):

```bash
# Download the BGE-M3 model (~1.3GB, Q8 quantization)
mkdir -p ~/.node-llama-cpp/models
curl -L -o ~/.node-llama-cpp/models/bge-m3-Q8_0.gguf \
  "https://huggingface.co/gpustack/bge-m3-GGUF/resolve/main/bge-m3-Q8_0.gguf"
```

The embedding engine uses GPU (CUDA) when available, falling back to CPU automatically. If no model is found, keyword (FTS5) search still works.

---

## License

MIT
