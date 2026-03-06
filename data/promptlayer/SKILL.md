---
name: promptlayer
description: Manage prompts, log LLM requests, run evaluations, and track scores via the PromptLayer API. Use when working with prompt versioning, A/B testing prompts, LLM observability/logging, prompt evaluation pipelines, datasets, or PromptLayer agents/workflows.
---

# PromptLayer

Interact with PromptLayer's REST API for prompt management, logging, evals, and observability.

## Setup

Set `PROMPTLAYER_API_KEY` env var. Run `scripts/setup.sh` to configure, or add to `~/.openclaw/.env`.

## CLI — `scripts/pl.sh`

```bash
# Prompt Templates
pl.sh templates list [--name <filter>] [--label <label>]
pl.sh templates get <name|id> [--label prod] [--version 3]
pl.sh templates publish              # JSON on stdin
pl.sh templates labels               # List release labels

# Log an LLM request (JSON on stdin)
echo '{"provider":"openai","model":"gpt-4o",...}' | pl.sh log

# Tracking
pl.sh track-prompt <req_id> <prompt_name> [--version 1] [--vars '{}']
pl.sh track-score <req_id> <score_0_100> [--name accuracy]
pl.sh track-metadata <req_id> --json '{"user_id":"abc"}'
pl.sh track-group <req_id> <group_id>

# Datasets & Evaluations
pl.sh datasets list [--name <filter>]
pl.sh evals list [--name <filter>]
pl.sh evals run <eval_id>
pl.sh evals get <eval_id>

# Agents
pl.sh agents list
pl.sh agents run <agent_id> --input '{"key":"val"}'
```

## API Path Groups

- `/prompt-templates` — registry (list, get)
- `/rest/` — tracking, logging, publishing
- `/api/public/v2/` — datasets, evaluations

Full reference: `references/api.md`
