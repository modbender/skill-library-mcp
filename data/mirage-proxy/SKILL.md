---
name: mirage-proxy
description: Install and configure mirage-proxy as a transparent PII/secrets filter for OpenClaw LLM API calls. Handles binary installation, provider config, auto-restart, and multi-model routing through the proxy.
---

# mirage-proxy for OpenClaw

Transparent secrets/PII filter between OpenClaw and LLM providers. Replaces sensitive data with plausible fakes — the LLM never knows.

GitHub: https://github.com/chandika/mirage-proxy

## Quick Setup

Run the bundled setup script:

```bash
bash ~/.openclaw/workspace/skills/mirage-proxy/setup.sh
```

This downloads the binary, creates an auto-restart wrapper, starts the proxy, and verifies it's running.

To uninstall: `bash ~/.openclaw/workspace/skills/mirage-proxy/setup.sh --uninstall`

## Configure OpenClaw Providers

After setup.sh succeeds, patch the OpenClaw config. Keep original providers AND add mirage versions for instant fallback:

```json5
{
  "models": {
    "mode": "merge",
    "providers": {
      "mirage-anthropic": {
        "baseUrl": "http://127.0.0.1:8686/anthropic",
        "api": "anthropic-messages",
        "apiKey": "${ANTHROPIC_API_KEY}",
        "models": [
          { "id": "claude-opus-4-6", "name": "Claude Opus 4.6 (mirage)", "api": "anthropic-messages", "reasoning": true, "input": ["text", "image"], "cost": {"input":0,"output":0,"cacheRead":0,"cacheWrite":0}, "contextWindow": 200000, "maxTokens": 32000 },
          { "id": "claude-sonnet-4-6", "name": "Claude Sonnet 4.6 (mirage)", "api": "anthropic-messages", "reasoning": true, "input": ["text", "image"], "cost": {"input":0,"output":0,"cacheRead":0,"cacheWrite":0}, "contextWindow": 200000, "maxTokens": 16000 },
          { "id": "claude-haiku-3-6", "name": "Claude Haiku 3.6 (mirage)", "api": "anthropic-messages", "reasoning": false, "input": ["text", "image"], "cost": {"input":0,"output":0,"cacheRead":0,"cacheWrite":0}, "contextWindow": 200000, "maxTokens": 8192 }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "models": {
        "anthropic/claude-opus-4-6": { "alias": "anthropic-opus" },
        "anthropic/claude-sonnet-4-6": { "alias": "anthropic-sonnet" },
        "anthropic/claude-haiku-3-6": { "alias": "anthropic-haiku" },
        "mirage-anthropic/claude-opus-4-6": { "alias": "mirage-opus" },
        "mirage-anthropic/claude-sonnet-4-6": { "alias": "mirage-sonnet" },
        "mirage-anthropic/claude-haiku-3-6": { "alias": "mirage-haiku" }
      }
    }
  }
}
```

### OpenAI / Codex (OAuth)

For OAuth-based providers (no API key env var), override the built-in provider baseUrl instead of creating a custom provider:

```json5
{
  "models": {
    "mode": "merge",
    "providers": {
      "openai-codex": {
        "baseUrl": "http://127.0.0.1:8686"
      }
    }
  }
}
```

⚠️ Do NOT add `"apiKey": "${OPENAI_API_KEY}"` to custom providers unless the env var exists in your container — it will crash OpenClaw on startup.

## Model Aliases

After config, switch with `/model`:

| Alias | Route |
|---|---|
| `anthropic-opus` | Direct to Anthropic |
| `mirage-opus` | Via mirage-proxy → Anthropic |
| `anthropic-sonnet` | Direct |
| `mirage-sonnet` | Via mirage |
| `codex` | Direct to OpenAI (or miraged if baseUrl overridden) |

## Persistence

mirage-proxy dies on OpenClaw restarts. Two solutions:

**Docker entrypoint (recommended):**
```yaml
# docker-compose.yml
command: sh -c "nohup /home/node/.openclaw/workspace/start-mirage.sh > /dev/null 2>&1 & exec openclaw start"
```

**Heartbeat check (fallback):**
Add to HEARTBEAT.md:
```
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8686/
```
If 000 or connection refused → restart via `start-mirage.sh`.

## Verify

```bash
# Proxy running?
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8686/
# Expect 502 (up, no path matched)

# Check redaction stats
tail -20 ~/.openclaw/workspace/mirage-proxy.log
# Look for: 🛡️ SECRET (AWS Access Key) [40 chars] → AKIA••••
```
