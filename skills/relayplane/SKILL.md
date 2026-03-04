---
name: relayplane
description: Save ~$47/mo on a typical $100/mo OpenClaw spend. Local proxy routes simple tasks to cheaper models automatically.
user-invocable: true
model-invocable: false
disableModelInvocation: true
homepage: https://relayplane.com
version: 3.4.0
author: Continuum
license: MIT
metadata:
  openclaw:
    emoji: "🚀"
    category: ai-tools
    instruction-only: true
---

# RelayPlane

**Spend $100/mo on OpenClaw? Keep $47 of it.** 835+ developers already installed. Now with cloud telemetry — every install makes routing smarter for everyone.

## What It Does

RelayPlane is a local proxy that saves you real money by routing simple LLM tasks to cheaper models automatically. Complex reasoning stays on Opus — file reads, status checks, and simple edits go to Haiku. One install, no code changes, automatic fallback if anything fails.

**Pro pays for itself at $60/mo API spend.** If you're spending $100+/mo, expect to save $40-70/mo.

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

## Free Account (Optional)

Create a free account to see your savings dashboard and contribute to smarter network routing:

```bash
# Visit the dashboard to create an account
# Then set your API key for personalized stats:
export RELAYPLANE_API_KEY=rp_...
```

Or just visit https://relayplane.com/dashboard — your proxy works fine without an account.

**Pro ($29/mo)** unlocks network-optimized routing, budget alerts, and provider health monitoring. Worth it at $60+/mo API spend.

## Privacy

- **Your prompts stay local** — never sent to RelayPlane
- **Anonymous telemetry** — only token counts, latency, model used (improves routing for everyone)
- **Opt-out anytime** — `relayplane-proxy telemetry off`
- **Fully offline mode** — `relayplane-proxy --offline`

## Links

- **Docs:** https://relayplane.com/docs
- **GitHub:** https://github.com/RelayPlane/proxy
- **npm:** https://www.npmjs.com/package/@relayplane/proxy
