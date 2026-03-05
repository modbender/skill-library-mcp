# Token Optimizer Skill for OpenClaw

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://clawhub.com)
[![Version](https://img.shields.io/badge/version-1.1.0-green)](https://github.com)

An optimization suite for OpenClaw agents to prevent token leaks and context bloat.

## Features

- **🔒 Cron Isolation** — Run background tasks without polluting your main context
- **🔍 Local RAG** — Semantic search over memory files instead of loading everything
- **🔄 Reset & Summarize** — Protocol for context consolidation when hitting limits
- **📜 Transcript Indexing** — Search through old session transcripts
- **⚡ Hybrid Search** — Combine vector and keyword search for better recall

## Installation

### Via ClawHub (coming soon)

```bash
openclaw skill install token-optimizer
```

### Manual Installation

1. Clone this repository into your skills folder:

```bash
cd ~/.openclaw/workspace/skills/
git clone https://github.com/D4kooo/Openclaw-Token-memory-optimizer/tree/main
```

2. The skill will be automatically detected by OpenClaw.

## Quick Start

### 1. Isolate Background Tasks

In your `openclaw.json`, set `sessionTarget: "isolated"` for cron jobs:

```json
{
  "cron": {
    "jobs": [
      {
        "name": "My Background Task",
        "schedule": { "kind": "every", "everyMs": 1800000 },
        "sessionTarget": "isolated",
        "payload": {
          "kind": "agentTurn",
          "message": "Do the thing. Use message tool if human needs to know."
        }
      }
    ]
  }
}
```

### 2. Enable Local RAG

Configure semantic search for your memory files:

```json
{
  "memorySearch": {
    "embedding": {
      "provider": "local",
      "model": "hf:second-state/All-MiniLM-L6-v2-Embedding-GGUF"
    },
    "store": "sqlite"
  }
}
```

### 3. Use the Reset Protocol

When context exceeds 100k tokens:

1. Ask your agent to summarize the session
2. Update MEMORY.md with important facts
3. Run `openclaw gateway restart`

## Configuration Reference

| Setting | Description | Default |
|---------|-------------|---------|
| `memorySearch.embedding.provider` | Embedding provider (`local`, `openai`) | — |
| `memorySearch.embedding.model` | Model for embeddings | — |
| `memorySearch.store` | Storage backend (`sqlite`, `memory`) | `memory` |
| `memorySearch.paths` | Paths to index | `["memory/", "MEMORY.md"]` |
| `cron.jobs[].sessionTarget` | Session type (`main`, `isolated`) | `main` |

## Why This Matters

Long-running OpenClaw sessions accumulate tokens from:

- Heartbeat checks
- Background task results
- File reads and tool outputs
- Conversation history

Without optimization, you'll hit context limits and experience:
- Slower responses
- Higher API costs
- Lost context when truncation kicks in

This skill teaches your agent to stay lean.

## Contributing

PRs welcome! Areas we'd love help with:

- [ ] Native hybrid search implementation
- [ ] Automatic context monitoring
- [ ] Smart transcript archiving
- [ ] Cost tracking integration

## Credits

- **shAde**  — Original concept
- **Clément** — Implementation

## License

MIT — Use freely, credit appreciated.

---

*Part of the OpenClaw ecosystem.* 🦦
