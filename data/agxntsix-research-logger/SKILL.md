---
name: Research Logger
version: 1.0.0
description: AI research pipeline with automatic SQLite logging and Langfuse tracing
author: aiwithabidi
---

# Research Logger 📚

AI research pipeline with automatic logging. Search via Perplexity, auto-save results to SQLite with topic/project metadata, full Langfuse tracing. Never lose a research session again.

## Usage

```bash
# Search and auto-save to SQLite
python3 scripts/research_logger.py log quick "what is RAG?"

# Research with topic tagging
python3 scripts/research_logger.py log pro "compare vector databases" --topic "AI infrastructure"

# Search past research entries
python3 scripts/research_logger.py search "AI"

# View recent entries
python3 scripts/research_logger.py recent --limit 5
```

## Requirements

- `PERPLEXITY_API_KEY` environment variable
- `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST` (optional, for tracing)
- Python 3.10+
- `requests`, `langfuse` packages
- SQLite (included with Python)

## Credits

Built by **AgxntSix** — AI ops agent by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi)
🌐 [agxntsix.ai](https://www.agxntsix.ai) | Part of the **AgxntSix Skill Suite** for OpenClaw agents
