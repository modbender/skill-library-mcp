---
name: relayplane
description: Cut API costs 40-60% with intelligent model routing. Auto-routes simple tasks to cheaper models.
user-invocable: true
model-invocable: false
disableModelInvocation: true
homepage: https://relayplane.com
version: 3.0.0
author: Continuum
license: MIT
metadata:
  openclaw:
    emoji: "🚀"
    category: ai-tools
    instruction-only: true
---

# RelayPlane

**Cut your AI API costs by 40-60%** with intelligent model routing.

## What It Does

RelayPlane is a local proxy that routes your LLM requests to the optimal model based on task complexity. Simple tasks go to cheaper models (Haiku), complex reasoning stays on premium models (Opus).

## Installation

Install the proxy globally:

```bash
npm install -g @relayplane/proxy
```

## Quick Start

```bash
# 1. Start the proxy
relayplane-proxy

# 2. Point OpenClaw at it (add to your shell config)
export ANTHROPIC_BASE_URL=http://localhost:3001
export OPENAI_BASE_URL=http://localhost:3001

# 3. Run OpenClaw normally - requests now route through RelayPlane
```

## Commands

Once installed, use the CLI directly:

| Command | Description |
|---------|-------------|
| `relayplane-proxy` | Start the proxy server |
| `relayplane-proxy stats` | View usage and cost breakdown |
| `relayplane-proxy telemetry off` | Disable telemetry |
| `relayplane-proxy telemetry status` | Check telemetry setting |
| `relayplane-proxy --help` | Show all options |

## Configuration

The proxy runs on `localhost:3001` by default. Configure via CLI flags:

```bash
relayplane-proxy --port 8080        # Custom port
relayplane-proxy --host 0.0.0.0     # Bind to all interfaces
relayplane-proxy --offline          # No telemetry, no network except LLM APIs
relayplane-proxy --audit            # Show telemetry payloads before sending
```

## Environment Variables

Set your API keys before starting:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export OPENAI_API_KEY=sk-...
# Optional: Google, xAI
export GEMINI_API_KEY=...
export XAI_API_KEY=...
```

## Privacy

- **Your prompts stay local** — never sent to RelayPlane
- **Anonymous telemetry** — only token counts, latency, model used
- **Opt-out anytime** — `relayplane-proxy telemetry off`
- **Fully offline mode** — `relayplane-proxy --offline`

## Links

- **Docs:** https://relayplane.com/docs
- **GitHub:** https://github.com/RelayPlane/proxy
- **npm:** https://www.npmjs.com/package/@relayplane/proxy
