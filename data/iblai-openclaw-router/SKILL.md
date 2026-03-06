---
name: iblai-router
description: Cost-optimizing model router for OpenClaw. Automatically routes each request to the cheapest capable Claude model (Haiku/Sonnet/Opus) using weighted scoring. Use when setting up smart model routing, reducing API costs, or configuring multi-tier LLM routing. Supports Anthropic models directly and OpenAI/Google models via OpenRouter.
---

# iblai-router

A zero-dependency proxy that sits between OpenClaw and the Anthropic API, routing each request to the cheapest capable model using a 14-dimension weighted scorer (<1ms overhead).

## Install

Run the install script to set up everything automatically:

```bash
bash "$(dirname "$0")/scripts/install.sh"
```

This will:
1. Copy `server.js` and `config.json` to `~/.openclaw/workspace/router/`
2. Create and start a systemd service (`iblai-router`) on port 8402
3. Register `iblai-router/auto` as an OpenClaw model provider

After install, `iblai-router/auto` is available anywhere OpenClaw accepts a model ID.

## Verify

```bash
curl -s http://127.0.0.1:8402/health | jq .
curl -s http://127.0.0.1:8402/stats | jq .
```

## Use

Set `iblai-router/auto` as the model for any scope:

| Scope | How |
|---|---|
| Cron job | Set `model` to `iblai-router/auto` in job config |
| Subagents | `agents.defaults.subagents.model = "iblai-router/auto"` |
| Per-session | `/model iblai-router/auto` |
| All sessions | `agents.defaults.model.primary = "iblai-router/auto"` |

**Tip:** Keep the main interactive session on a fixed model (e.g. Opus). Use the router for cron jobs, subagents, and background tasks where cost savings compound.

## Customize

All config lives in `~/.openclaw/workspace/router/config.json` and hot-reloads on save — no restart needed.

### Models

Change the models per tier:

```json
{
  "models": {
    "LIGHT":  "claude-3-5-haiku-20241022",
    "MEDIUM": "claude-sonnet-4-20250514",
    "HEAVY":  "claude-opus-4-20250514"
  }
}
```

### Non-Anthropic models (OpenAI, Google)

Set `apiBaseUrl` to route through OpenRouter:

```json
{
  "models": {
    "LIGHT":  "openai/gpt-4.1-mini",
    "MEDIUM": "openai/gpt-4.1",
    "HEAVY":  "openai/o3"
  },
  "apiBaseUrl": "https://openrouter.ai/api/v1"
}
```

Update the API key in the systemd service when switching providers, then `systemctl daemon-reload && systemctl restart iblai-router`.

### Scoring

Keyword lists control which tier handles a request:

- `simpleKeywords`, `relayKeywords` → push toward **LIGHT** (cheap)
- `imperativeVerbs`, `codeKeywords`, `agenticKeywords` → push toward **MEDIUM**
- `technicalKeywords`, `reasoningKeywords`, `domainKeywords` → push toward **HEAVY** (capable)

Tune boundaries and weights in `config.json` to match your workload. See the [full README](https://github.com/iblai/iblai-openclaw-router) for details.

## Uninstall

```bash
bash "$(dirname "$0")/scripts/uninstall.sh"
```

Stops the service, removes the systemd unit, and deletes router files. Reminder: switch any workloads using `iblai-router/auto` back to a direct model first.
