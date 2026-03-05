# Memory Configuration

## Built-in Memory Search

```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "enabled": true,
        "provider": "openai",
        "sources": ["memory", "sessions"],
        "model": "text-embedding-3-small"
      }
    }
  }
}
```

**providers:** `openai`, `gemini`, `voyage`, `local`
**sources:**
- `memory` — MEMORY.md + memory/*.md
- `sessions` — Past session transcripts

---

## Memory Files

Place in workspace:

| File | Purpose |
|------|---------|
| `MEMORY.md` | Long-term curated knowledge |
| `memory/*.md` | Topic-specific memory files |
| `memory/YYYY-MM-DD.md` | Daily logs |
| `memory/INDEX.md` | Memory index/TOC |

---

## Embedding Configuration

### OpenAI (Recommended)

```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "provider": "openai",
        "model": "text-embedding-3-small"
      }
    }
  }
}
```

### Local (No API)

```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "provider": "local",
        "local": {
          "modelPath": "hf:BAAI/bge-small-en-v1.5"
        }
      }
    }
  }
}
```

---

## Hybrid Search

Combine vector + text search:

```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "query": {
          "hybrid": {
            "enabled": true,
            "vectorWeight": 0.7,
            "textWeight": 0.3
          },
          "maxResults": 6,
          "minScore": 0.5
        }
      }
    }
  }
}
```

---

## Memory Sync

Control when index updates:

```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "sync": {
          "onSessionStart": true,
          "onSearch": true,
          "watch": true,
          "watchDebounceMs": 2000
        }
      }
    }
  }
}
```

---

## QMD Backend (Alternative)

For larger memory stores:

```json
{
  "memory": {
    "backend": "qmd",
    "qmd": {
      "includeDefaultMemory": true,
      "paths": [
        { "path": "~/notes", "pattern": "**/*.md" }
      ],
      "update": {
        "interval": "5m",
        "onBoot": true
      },
      "limits": {
        "maxResults": 6,
        "maxSnippetChars": 700
      }
    }
  }
}
```

---

## Session Indexing

Include past conversations in search:

```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "sources": ["memory", "sessions"],
        "sync": {
          "sessions": {
            "deltaBytes": 100000,
            "deltaMessages": 50
          }
        }
      }
    }
  }
}
```

---

## LanceDB Plugin (Advanced)

Full-featured memory with auto-capture:

```json
{
  "plugins": {
    "entries": {
      "memory-lancedb": {
        "enabled": true,
        "config": {
          "embedding": {
            "apiKey": "${OPENAI_API_KEY}",
            "model": "text-embedding-3-small"
          },
          "autoCapture": true,
          "autoRecall": true
        }
      }
    }
  }
}
```

---

## Batch Embeddings

Speed up indexing with batch API:

```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "remote": {
          "batch": {
            "enabled": true,
            "concurrency": 2,
            "timeoutMinutes": 60
          }
        }
      }
    }
  }
}
```
