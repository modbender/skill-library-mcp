# Recommended OpenClaw Configuration for Big Memory

Add these settings to your project's `openclaw.json` to optimize memory and compaction
for use with the big-memory skill. These are optional but strongly recommended.

## Compaction Settings

The most impactful change: replace the default generic flush prompt with one that
triggers structured snapshot capture.

```json
{
  "agents": {
    "defaults": {
      "compaction": {
        "memoryFlush": {
          "enabled": true,
          "softThresholdTokens": 40000,
          "systemPrompt": "You are capturing structured task state for post-compaction recovery. Follow the BIG-MEMORY-SNAPSHOT schema exactly. Be precise with file paths, variable names, and code snippets. Do not summarize -- capture specifics.",
          "prompt": "Context compaction is imminent. Create a structured task snapshot following the BIG-MEMORY-SNAPSHOT schema and APPEND it to memory/YYYY-MM-DD.md. Include all sections: active goal, current state, files in play, decisions made, code context (key snippets only), key names/values, blockers, and next steps. Read the existing daily log first and append -- never overwrite existing content. If there is genuinely nothing worth storing, reply NO_FLUSH."
        }
      }
    }
  }
}
```

### What These Settings Do

- **`softThresholdTokens: 40000`** -- Triggers the snapshot capture early, while there is
  still enough context to capture accurately. Lower this to 30000 for smaller models (8k-32k
  context) or raise to 60000 for 200k+ context windows.
- **`systemPrompt`** -- Tells the agent to use the BIG-MEMORY-SNAPSHOT schema instead of
  writing unstructured prose.
- **`prompt`** -- Explicit instructions for structured capture with the append-only rule.

## Memory Search Settings (Optional)

If you want to use a specific embedding provider for memory search:

```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "enabled": true,
        "provider": "local",
        "query": {
          "hybrid": {
            "enabled": true,
            "vectorWeight": 0.7,
            "textWeight": 0.3
          }
        }
      }
    }
  }
}
```

The `local` provider uses a GGUF embedding model (~0.6 GB) with zero cloud costs.
Hybrid search combines vector similarity with BM25 keyword matching, which helps
the `BIG-MEMORY-SNAPSHOT` markers score highly on exact-term match.

If you prefer cloud embeddings, use `"provider": "openai"` with `text-embedding-3-small`
(~$0.10 per thousands of searches).

## Session Memory (Experimental, Optional)

To also index conversation transcripts (not just memory files):

```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "experimental": {
          "sessionMemory": true
        },
        "sources": ["memory", "sessions"]
      }
    }
  }
}
```

This makes `memory_search` also find relevant context from past conversation turns,
not just from what was explicitly written to memory files.

## Notes

- The skill works without any configuration changes. The `/big-memory save` and
  `/big-memory recall` commands use OpenClaw's default memory tools.
- Configuration only enhances the AUTOMATIC pre-compaction capture. Without it,
  the default flush prompt fires instead of the structured one.
- All settings go in your project's `openclaw.json` or `~/.openclaw/openclaw.json`.
