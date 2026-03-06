---
name: metaskill
description: "Teaches AI agents how to learn better by enforcing deep correction, transfer learning, and proactive pattern recognition. Use when an error occurs and needs deep analysis (not surface patch), before starting a complex task to check past analogies, or after success to capture winning patterns. NOT for routine file reads or simple one-off commands."
---
# Metaskill

## 3 Core Components

1. **Deep Self-Correction (`deep-correct.sh`)** — 3-level breakdown on errors:
   - **Surface**: What specifically failed
   - **Principle**: The underlying rule/constraint violated
   - **Habit**: Concrete behavioral change to prevent recurrence

2. **Transfer Learning (`transfer-check.sh`)** — Before a task, search past learnings for analogous patterns. Maps domains (e.g., "auth" → "security") to prevent siloed learning.

3. **Proactive Pattern Recognition (`success-capture.sh`)** — Log what worked and why, building a repository of successful patterns.

## Usage

```bash
# When an error occurs
bash skills/metaskill/scripts/deep-correct.sh "description of the error"

# Before starting a complex task
bash skills/metaskill/scripts/transfer-check.sh "description of the new task"

# After successful execution
bash skills/metaskill/scripts/success-capture.sh "what worked" "why it worked"

# Monthly health eval
bash skills/metaskill/scripts/eval.sh --save
```

## Configuration (LLM Provider)

Metaskill uses two provider tiers — **fast** (extraction) and **deep** (transfer/eval). Edit `config.yaml` to match your setup:

```yaml
# config.yaml
providers:
  fast: anthropic   # change to: openai | ollama | gemini
  deep: anthropic
```

| Provider | Env Var | Notes |
|---|---|---|
| `anthropic` | `ANTHROPIC_API_KEY` | Default |
| `openai` | `OPENAI_API_KEY` | |
| `ollama` | *(none needed)* | Local, free |
| `gemini` | `GOOGLE_API_KEY` | |

**Ollama example** (fully local, no API key):
```yaml
providers:
  fast: ollama
  deep: ollama
models:
  ollama:
    fast: llama3.2
    deep: llama3.1:70b
```

If no provider is available, metaskill falls back to manual/heuristic mode (still works, but less precise extraction).

## Integration with Self-Improving-Agent

Writes to `skills/self-improving-agent/.learnings/` if present, otherwise falls back to its own `.learnings/` directory. No extra setup needed.

## AGENTS.md Wiring (Mandatory)

Add to pre-task checklist:
1. Run `transfer-check.sh` before any major task
2. Run `deep-correct.sh` immediately after any error (not just LEARNINGS.md append)
3. Run `success-capture.sh` after complex task completes successfully
