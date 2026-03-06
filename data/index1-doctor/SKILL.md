---
name: index1-doctor
description: Diagnose index1 environment - check Python, Ollama, models, index health.
version: 2.0.3
license: Apache-2.0
author: gladego
tags: [index1, diagnostics, mcp, troubleshooting]
---

# index1 Doctor

Environment diagnostic skill for index1. Runs health checks and provides fix recommendations.

## Usage

Type `/doctor` or ask the agent to diagnose index1.

## What it checks

The skill runs three commands sequentially and analyzes results:

### 1. Environment Check

```bash
index1 doctor
```

Checks:
- Python version (>= 3.10 required)
- SQLite version (>= 3.43.0 for full features)
- sqlite-vec extension
- ONNX embedding (built-in, bge-small-en-v1.5)
- Ollama connectivity (optional, for multilingual/CJK)
- Embedding model availability
- CJK/Chinese support (jieba)

### 2. Index Status

```bash
index1 status
```

Shows:
- Document count and chunk count
- Collections list
- Last index time
- Database size

### 3. Ollama Models

```bash
ollama list
```

Shows installed models. Recommended embedding models:
- `nomic-embed-text` — Standard, 270MB
- `bge-m3` — Best for CJK content, 1.2GB

## Interpreting Results

| Check | Pass | Fail Fix |
|-------|------|----------|
| Python | >= 3.10 | Install Python 3.11+ |
| SQLite | >= 3.43.0 | Auto-degrades, no action needed |
| sqlite-vec | Loaded | `pip install index1` (bundled) |
| Ollama | Connected | `curl -fsSL https://ollama.com/install.sh \| sh` |
| Model | Available | `ollama pull nomic-embed-text` |
| CJK | jieba loaded | `pip install index1[chinese]` |
| Index | Has documents | `index1 index ./src ./docs` |

## When to use

- First-time setup verification
- After upgrading index1
- When search returns unexpected results
- When vector search stops working
- Before reporting issues
