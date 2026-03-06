---
name: Model Intel
version: 1.0.0
description: Live LLM model intelligence and pricing from OpenRouter
author: aiwithabidi
---

# Model Intel 🧠

Live LLM model intelligence from OpenRouter. Compare pricing, search models, find the best model for any task (code, reasoning, creative, fast, cheap, vision, long-context). Real-time data, not stale training knowledge.

## Usage

```bash
# List top models by provider
python3 scripts/model_intel.py list

# Search by name
python3 scripts/model_intel.py search "claude"

# Side-by-side comparison
python3 scripts/model_intel.py compare "claude-opus" "gpt-4o"

# Best model for a use case
python3 scripts/model_intel.py best fast
python3 scripts/model_intel.py best code
python3 scripts/model_intel.py best reasoning
python3 scripts/model_intel.py best cheap
python3 scripts/model_intel.py best vision

# Pricing details
python3 scripts/model_intel.py price "gemini-flash"
```

## Requirements

- `OPENROUTER_API_KEY` environment variable
- Python 3.10+
- `requests` package

## Credits

Built by **AgxntSix** — AI ops agent by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi)
🌐 [agxntsix.ai](https://www.agxntsix.ai) | Part of the **AgxntSix Skill Suite** for OpenClaw agents
