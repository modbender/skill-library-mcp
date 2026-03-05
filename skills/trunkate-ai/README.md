# Trunkate AI Skill (Optimized) - Token Efficient Engine

**Precision token optimization for OpenClaw agents. Built for token-efficient real-world actions.**

Turn your agent into a token-efficient powerhouse. Automatically prune, compress, and optimize text context without losing meaning.

## Example Prompts

- "Optimize this text for me."
- "Shrink this log output so it fits in the context window."
- "Reduce the token count of this draft."

## What it does

- **Smart Pruning**: Removes redundant phrases, politeness, and filler words.
- **Visual Compression**: Collapses dense structures while preserving data.
- **Budget Compliance**: Ensures text fits within varying token limits (default: 1000).
- **Zero Latency**: Uses the ultra-fast Trunkate AI SaaS API.

## Quick Start

This skill requires a Trunkate API key to communicate with the optimization backend.

1. Sign up for a free account at [trunkate.ai](https://trunkate.ai).
2. Generate a new API key from your dashboard.
3. Configure your agent to use the key permanently (see below).

### 📦 Files

```text
trunkate/
├── SKILL.md              # Agent instructions
├── bin/
│   └── trunkate.py       # Skill logic (CLI script)
└── requirements.txt      # Dependencies
```

## Requirements

- Python 3.9+
- Internet access (to reach `trunkate.ai` API)

## Install as OpenClaw Skill

Ensure you have the OpenClaw system installed, then add the Trunkate package:

```bash
# Install the Trunkate AI skill
clawhub install https://github.com/Trunkate-AI/trunkate-ai-skills

# Persistently set the API key for your agent
echo 'TRUNKATE_API_KEY="tk_live_..."' >> ~/.openclaw/.env
```

Once installed, OpenClaw will autonomously negotiate token budgets with Trunkate before executing prompt-heavy actions!
