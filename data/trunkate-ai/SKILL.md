---
name: Trunkate AI
description: Precision token optimization for OpenClaw agents. Built for token-efficient real-world actions.
author: Trunkate AI
metadata:
  clawdbot:
    emoji: "✂️"
    os: ["linux", "darwin"]
    requires:
      bins: ["python3"]
      env: ["TRUNKATE_API_KEY"]
    install:
      - id: pip
        kind: shell
        command: pip install -r requirements.txt
        bins: ["python3"]
        label: Install Python dependencies
---

# Trunkate AI Skill

Precision token optimization for OpenClaw agents. Automatically prune, compress, and optimize text context without losing meaning.

## Installation

Ensure you have the OpenClaw system installed, then add the Trunkate package:

1. Sign up for a free account at [trunkate.ai](https://trunkate.ai) and generate an API key.
2. Install the skill and configure your token:

```bash
# Install the Trunkate AI skill
clawhub install https://github.com/Trunkate-AI/trunkate-ai-skills

# Persistently set the API key for your agent
echo 'TRUNKATE_API_KEY="tk_live_..."' >> ~/.openclaw/.env
```

## Quick Commands

Once installed and authenticated, your agent can natively use Trunkate to optimize its thoughts before executing tasks:

```bash
# Let your agent optimize before executing a task
openclaw "Optimize 'Your very long context...' for the task of 'Summarize this document' with a 500 token budget for model gpt-4o."
```

*Note: The OpenClaw plugin natively hooks into the official Trunkate Python backend and passes the necessary arguments exactly like the standard CLI.*
