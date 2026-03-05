---
name: semantic-memory
description: Local semantic memory with vector search and Transformers.js. Store, search, and recall conversation context using embeddings (fully local, no API keys).
version: 1.0.0
author: zuiho-kai
homepage: https://github.com/zuiho-kai/openclaw-semantic-memory
tags: [memory, semantic-search, vector-search, transformers, embeddings, local-ai, context]
metadata:
  openclaw:
    requires:
      bins: [node, npm]
---

# semantic-memory

**Use when** you need your OpenClaw agent to remember and recall information across conversations using semantic search.

⚠️ **Privacy Notice**: The optional `autoCapture` feature (disabled by default) can capture PII like emails and phone numbers if you enable `allowPIICapture`. Only enable if you understand the privacy implications.

Local semantic memory plugin powered by vector search and Transformers.js embeddings. Zero configuration, fully local, no API keys required.

## Features

- Semantic search with local Transformers.js embeddings
- In-memory mode (zero config) or persistent Qdrant storage
- Optional auto-capture of conversation context (opt-in, disabled by default)
- Context-aware memory recall
- Fully local, no API keys or external services required

## Installation

```bash
clawhub install semantic-memory
```

**First-time setup:** This plugin downloads a 25MB embedding model from Hugging Face on first run and may require build tools for native dependencies (sharp, onnxruntime). See [README](https://github.com/zuiho-kai/openclaw-memory-qdrant#readme) for detailed installation requirements.

## Configuration

Enable in your OpenClaw config:

```json
{
  "plugins": {
    "semantic-memory": {
      "enabled": true
    }
  }
}
```

**Options:**
- `persistToDisk` (default: true) - Save memories to disk in memory mode. Data stored in `~/.openclaw-memory/` survives restarts. Set to false for volatile memory.
- `storagePath` (optional) - Custom storage directory. Leave empty for default `~/.openclaw-memory/`.
- `autoCapture` (default: false) - Auto-record conversations. **Privacy protection enabled by default**: text containing PII (emails, phone numbers) is automatically skipped.
- `allowPIICapture` (default: false) - Allow capturing PII when autoCapture is enabled. **Only enable if you understand the privacy implications.**
- `autoRecall` (default: true) - Auto-inject relevant memories
- `qdrantUrl` (optional) - External Qdrant server (leave empty for in-memory)

## Usage

Three tools available:

**memory_store** - Save information
```javascript
memory_store({
  text: "User prefers Opus for complex tasks",
  category: "preference"
})
```

**memory_search** - Find relevant memories
```javascript
memory_search({
  query: "workflow preferences",
  limit: 5
})
```

**memory_forget** - Delete memories
```javascript
memory_forget({ memoryId: "uuid" })
// or
memory_forget({ query: "text to forget" })
```

## Privacy & Security

- **Disk persistence** (default): Memories saved to `~/.openclaw-memory/` and survive restarts. Set `persistToDisk: false` for volatile memory.
- **In-memory mode**: When `persistToDisk: false`, data cleared on restart
- **Qdrant mode**: Data sent to configured server (use trusted servers only)
- **Network**: Downloads ~25MB model from Hugging Face on first run
- **PII Protection**: By default, autoCapture skips text containing emails or phone numbers. Set `allowPIICapture: true` only if you understand the privacy implications.
- **autoCapture**: Disabled by default for privacy. When enabled, only captures text matching semantic triggers (preferences, decisions, facts) and skips PII unless explicitly allowed.

## Technical Details

- Vector DB: Qdrant (in-memory or external)
- Embeddings: Xenova/all-MiniLM-L6-v2 (local)
- Module: ES6 with factory function pattern

## Links

- GitHub: https://github.com/zuiho-kai/openclaw-semantic-memory
- Issues: https://github.com/zuiho-kai/openclaw-semantic-memory/issues
