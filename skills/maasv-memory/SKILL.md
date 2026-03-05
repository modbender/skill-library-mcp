# maasv Memory

Structured long-term memory for OpenClaw agents, powered by [maasv](https://github.com/ascottbell/maasv).

Replaces the default memory backend with a cognition layer that includes 3-signal retrieval (semantic + keyword + knowledge graph), entity extraction, temporal versioning, and experiential learning.

**maasv is entirely self-hosted.** There is no maasv cloud service. You run the server on your own machine, and all data is stored in a SQLite file on your local disk that you own and control. Nothing is sent to maasv.

## Install

This skill requires the `@maasv/openclaw-memory` plugin and a running maasv server.

### 1. Start the server

```bash
pip install "maasv[server,anthropic,voyage]"
cp server.env.example .env  # fill in API keys (see below)
maasv-server
```

### 2. Install the plugin

```bash
openclaw plugins install @maasv/openclaw-memory
```

### 3. Activate

```json5
// ~/.openclaw/openclaw.json
{
  plugins: {
    slots: { memory: "memory-maasv" },
    entries: {
      "memory-maasv": {
        enabled: true,
        config: {
          serverUrl: "http://127.0.0.1:18790",
          autoRecall: true,
          autoCapture: true,
          enableGraph: true
        }
      }
    }
  }
}
```

## Required Credentials

The maasv server needs an LLM provider (for entity extraction) and an embedding provider (for semantic search). Configure these in your `.env` file:

| Variable | Required | Purpose |
|----------|----------|---------|
| `MAASV_LLM_PROVIDER` | Yes | `anthropic` or `openai` |
| `MAASV_ANTHROPIC_API_KEY` | If using Anthropic | LLM calls for entity extraction |
| `MAASV_OPENAI_API_KEY` | If using OpenAI | LLM calls for entity extraction |
| `MAASV_EMBED_PROVIDER` | Yes | `voyage`, `openai`, or `ollama` |
| `MAASV_VOYAGE_API_KEY` | If using Voyage | Embedding generation |
| `MAASV_API_KEY` | Optional | Protects maasv server endpoints with auth |

**For fully local operation** (no cloud calls), use `ollama` as your embed provider and a local LLM. maasv is optimized for [Qwen3-Embedding-8B](https://ollama.com/library/qwen3-embedding) via Ollama, with built-in Matryoshka dimension truncation. See the [maasv README](https://github.com/ascottbell/maasv) for local setup.

## Data & Network Behavior

- **maasv has no cloud service.** The server runs on your machine, the database is a SQLite file on your disk. You own all of it.
- **The only external calls are to your own LLM/embedding provider** (Anthropic, OpenAI, Voyage) — using your own API keys, from your own machine. If you use `ollama`, zero data leaves your machine.
- **The plugin talks only to localhost** (`127.0.0.1:18790`). It makes no external network calls.
- **autoCapture** sends conversation summaries to your local maasv server for entity extraction. Extracted entities are stored in your local SQLite database.
- **autoRecall** reads from your local SQLite database and injects relevant memories into the agent's context.
- **No telemetry, no analytics, no phone-home.** maasv does not collect or transmit any data.

## What You Get

- **`memory_search`** — 3-signal retrieval across your memory store
- **`memory_store`** — Dedup-aware memory storage
- **`memory_forget`** — Permanent deletion
- **`memory_graph`** — Knowledge graph: entity search, profiles, relationships
- **`memory_wisdom`** — Log reasoning, record outcomes, search past decisions

## Links

- **Plugin (npm):** [@maasv/openclaw-memory](https://www.npmjs.com/package/@maasv/openclaw-memory)
- **Server + core (PyPI):** [maasv](https://pypi.org/project/maasv/)
- **Source:** [github.com/ascottbell/maasv](https://github.com/ascottbell/maasv)
