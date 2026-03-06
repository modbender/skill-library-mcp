# OpenClaw token optimization reference

## Quick checklist
- Trim injected workspace files (`AGENTS.md`, `SOUL.md`, `MEMORY.md`, `memory/YYYY-MM-DD.md`).
- Remove unused workspace injections from config.
- Enable prompt caching where supported.
- Add heartbeat to keep cache warm; use a cheap model.
- Set context pruning TTL to align with cache.
- Enable compaction with memory flush.
- Use subagents for parallel tasks.
- Enable memory search or qmd for large corpora.
- Audit cron tasks: consolidate, slow down, and downgrade models.

## Example snippets (adjust to your OpenClaw version)

### Prompt caching (model params)
```json
{
  "models": {
    "anthropic/claude-opus-4-6": {
      "params": {
        "cacheRetention": "long",
        "maxTokens": 65536
      }
    }
  }
}
```

### Heartbeat
```json
{
  "heartbeat": {
    "every": "55m",
    "target": "last",
    "model": "minimax/MiniMax-M2.5",
    "quiet": {
      "start": "23:00",
      "end": "08:00"
    }
  }
}
```

### Context pruning
```json
{
  "contextTokens": 200000,
  "contextPruning": {
    "mode": "cache-ttl",
    "ttl": "55m"
  }
}
```

### Compaction with memory flush
```json
{
  "compaction": {
    "mode": "safeguard",
    "reserveTokensFloor": 24000,
    "memoryFlush": {
      "enabled": true,
      "softThresholdTokens": 6000,
      "systemPrompt": "Session nearing compaction. Store durable memories now.",
      "prompt": "Write any lasting notes to memory/YYYY-MM-DD.md; reply with NO_REPLY if nothing to store."
    }
  }
}
```

### Subagents
```json
{
  "subagents": {
    "model": "minimax/MiniMax-M2.5",
    "maxConcurrent": 12,
    "archiveAfterMinutes": 60
  }
}
```

### Memory search (local)
```json
{
  "memorySearch": {
    "provider": "local",
    "cache": {
      "enabled": true,
      "maxEntries": 50000
    }
  }
}
```

### qmd backend
```json
{
  "memory": {
    "backend": "qmd",
    "citations": "auto",
    "qmd": {
      "includeDefaultMemory": true,
      "update": {
        "interval": "5m",
        "debounceMs": 15000
      },
      "limits": {
        "maxResults": 8,
        "timeoutMs": 5000
      },
      "paths": [
        {
          "name": "main-workspace",
          "path": "/home/user/.openclaw/workspace",
          "pattern": "**/*.md"
        }
      ]
    }
  }
}
```

### Model aliasing (manual upgrades)
```json
{
  "agents": {
    "defaults": {
      "models": {
        "anthropic/claude-opus-4-6": {
          "alias": "opus"
        },
        "anthropic/claude-sonnet-4-5": {
          "alias": "sonnet"
        }
      }
    }
  }
}
```

## Workspace file trimming targets
- `AGENTS.md`: keep only core instructions, required policies, and any non-negotiable rules.
- `SOUL.md`: short persona bullets (tone, response style, do/don't).
- `MEMORY.md`: durable facts only. Archive or move transient items.
- `memory/YYYY-MM-DD.md`: keep recent decisions; remove verbose logs.

## Cron optimization heuristics
- Consolidate checks that run within the same 15-30 minute window.
- Downgrade non-creative tasks to lower-cost models.
- Use on-change notifications instead of periodic status spam.

## Notes
- Parameter names and supported features vary by OpenClaw version and provider. Verify keys before applying changes.
- Prompt caching requires stable system prompts and tool schemas to maximize cache hits.
