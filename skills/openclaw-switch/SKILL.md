---
name: openclaw-switch
description: Manage multi-provider model switching and fallback chains in OpenClaw. "OpenClaw Switch" helps users set up automatic model failover (e.g. 429 rate-limit → fallback), switch primary models, view current fallback chains, and configure heartbeat/subagent routing. Works with any provider (Gemini, OpenAI, Anthropic, NVIDIA, Ollama, etc.).
metadata:
  openclaw:
    bin:
      openclaw-switch: scripts/openclaw-switch.sh
---

# OpenClaw Switch

The missing model manager for OpenClaw. Switch models, visualize fallback chains, and manage multi-provider setups.

## Quick start

```bash
# Show current model, fallback chain, heartbeat & subagent config
bash {baseDir}/scripts/openclaw-switch.sh status

# List all available models across all providers
bash {baseDir}/scripts/openclaw-switch.sh list

# Switch primary model (by number from list)
bash {baseDir}/scripts/openclaw-switch.sh switch 2

# Show fallback chain only
bash {baseDir}/scripts/openclaw-switch.sh fallback
```

## How it works

OpenClaw natively supports `model.fallbacks` — when the primary model returns an error (429, 500, etc.), the next model in the chain is tried automatically. OpenClaw Switch helps users **configure, visualize, and toggle** this chain.

### Typical setup

Register multiple providers in `openclaw.json`, each with its own API key:

```json
{
  "models": {
    "providers": {
      "provider-a": { "apiKey": "...", "models": [{ "id": "model-1" }] },
      "provider-b": { "apiKey": "...", "models": [{ "id": "model-2" }] }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "provider-a/model-1",
        "fallbacks": ["provider-b/model-2"]
      }
    }
  }
}
```

### Use cases

- **Same provider, two API keys** (e.g. paid + free Gemini) — register as separate providers
- **Cross-provider failover** (e.g. Gemini → OpenAI → local Ollama)
- **Cost optimization** — route heartbeat/subagents to cheaper or free models

## Security

The bundled script:

- **Never transmits** API keys or config data over the network
- **Never logs** full API keys (masks all but first 8 chars)
- Uses only `bash` + `python3` stdlib — **zero external dependencies**
- Source is < 150 lines — **fully auditable in 2 minutes**
