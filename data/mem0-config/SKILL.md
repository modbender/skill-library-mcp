---
name: openclaw-mem0
description: Install, configure, diagnose, and operate the openclaw-mem0 long-term memory plugin for OpenClaw agents. Use when the user wants to set up mem0 memory (platform or open-source/self-hosted mode), configure OSS components (embedder, vector store, LLM, historyDbPath), debug memory issues (SQLITE_CANTOPEN crash loops, memories not being stored or recalled, Qdrant/Ollama connectivity), use the `openclaw mem0` CLI (search, stats), or understand how auto-recall and auto-capture work in agent sessions.
---

# openclaw-mem0

Long-term memory plugin for OpenClaw agents, powered by [Mem0](https://mem0.ai). Extracts and injects memories automatically around each agent turn.

## Installation

### 1. Install the plugin

```bash
openclaw plugins install @mem0/openclaw-mem0
```

This installs the plugin into `~/.openclaw/extensions/openclaw-mem0/` and adds it to `openclaw.json`.

### 2. Choose a mode and install dependencies

**Platform mode** — no local dependencies. Get an API key from [app.mem0.ai](https://app.mem0.ai) and skip to [Configuration](#configuration).

**Open-source mode** — requires two local services:

```bash
# Ollama (embedder + LLM)
brew install ollama
ollama serve                        # or: brew services start ollama
ollama pull bge-m3:latest           # embedder (1024-dim)
ollama pull llama3.2                # LLM for memory extraction

# Qdrant (vector store)
docker run -d -p 6333:6333 qdrant/qdrant
# or: brew install qdrant && qdrant
```

Verify both are running:
```bash
curl -s http://localhost:11434/          # → "Ollama is running"
curl -s http://localhost:6333/health     # → {"status":"ok"}
```

### 3. Add to openclaw.json

Add under `plugins.entries` (see [Configuration](#configuration) below).

### 4. Restart the gateway

```bash
openclaw gateway stop && openclaw gateway
```

Confirm the plugin loaded:
```bash
grep "openclaw-mem0: initialized" ~/.openclaw/logs/gateway.log | tail -1
```

Expected output: `openclaw-mem0: initialized (mode: open-source, user: ..., autoRecall: true, autoCapture: true)`

---

## Modes

| Mode | Config | Requires |
|---|---|---|
| `platform` | `apiKey` from app.mem0.ai | Internet, Mem0 API key |
| `open-source` | `oss` block (self-hosted) | Ollama + Qdrant (or other providers) |

## Configuration

### Minimal Config

**Platform:**
```json5
"openclaw-mem0": {
  "enabled": true,
  "config": { "mode": "platform", "apiKey": "${MEM0_API_KEY}", "userId": "your-id" }
}
```

**Open-source:**
```json5
"openclaw-mem0": {
  "enabled": true,
  "config": {
    "mode": "open-source",
    "userId": "your-id",
    "oss": {
      "embedder":    { "provider": "ollama", "config": { "model": "bge-m3:latest", "baseURL": "http://localhost:11434" } },
      "vectorStore": { "provider": "qdrant", "config": { "host": "localhost", "port": 6333, "collection": "memories", "dimension": 1024 } },
      "llm":         { "provider": "ollama", "config": { "model": "llama3.2", "baseURL": "http://localhost:11434" } },
      "historyDbPath": "/absolute/path/to/.openclaw/memory/history.db"
    }
  }
}
```

> **Always set `historyDbPath` to an absolute path.** When openclaw runs as a LaunchAgent, `process.cwd()` is `/`, so the default relative `"memory.db"` resolves to `/memory.db` (unwritable on macOS), causing a SQLITE_CANTOPEN crash loop. See [troubleshooting.md](references/troubleshooting.md).

## Key Config Options

| Key | Default | Notes |
|---|---|---|
| `autoRecall` | `true` | Inject memories before each agent turn |
| `autoCapture` | `true` | Store memories after each agent turn |
| `topK` | `5` | Max memories injected per turn |
| `searchThreshold` | `0.5` | Min similarity score (0–1) |
| `userId` | `"default"` | Scope memories per user |

## CLI

```bash
openclaw mem0 stats                          # Total memories, mode, user
openclaw mem0 search "user's name"           # Semantic search
openclaw mem0 search "topic" --scope long-term   # long-term | session | all
```

## Agent Tools

The plugin registers 5 tools for agents to call:

| Tool | Description |
|---|---|
| `memory_search` | Semantic search (scope: session/long-term/all) |
| `memory_list` | List all memories for a user |
| `memory_store` | Explicitly save a fact (`longTerm: true` by default) |
| `memory_get` | Fetch memory by ID |
| `memory_forget` | Delete by ID or query |

## Verifying It Works

```bash
# Check gateway log for injection events
grep "openclaw-mem0: inject" ~/.openclaw/logs/gateway.log | tail -5

# Confirm history DB created at configured path
ls -la /path/to/history.db

# No SQLITE errors since last gateway start
grep "SQLITE_CANTOPEN" ~/.openclaw/logs/gateway.err.log | tail -3
```

## Troubleshooting

See [references/troubleshooting.md](references/troubleshooting.md) for:
- SQLITE_CANTOPEN crash loop (most common issue)
- Qdrant / Ollama not reachable
- Memories not being stored or recalled
- Telegram `allowFrom` config warning
