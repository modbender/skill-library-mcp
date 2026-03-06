---
name: context-pruner
description: Intelligent context window management by summarizing and removing redundant history. Helps agents maintain high performance in long-running threads.
---

# Context Pruner

Save tokens and keep focus sharp. This skill manages the "bloat" of long sessions.

## Pruning Protocol

1. **Noise Detection**: Filter "Acknowledge" messages and filler words.
2. **Fact Distillation**: Extract raw info and discard the conversational fluff.
3. **Chunking**: Break long transcripts into searchable summaries.

## Installation
```bash
clawhub install context-pruner
```
