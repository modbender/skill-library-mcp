---
name: astrai-inference-router
description: Route all LLM calls through Astrai for 40%+ cost savings with intelligent routing and privacy controls
version: 1.0.0
homepage: https://github.com/beee003/astrai-openclaw
metadata:
  clawdbot:
    emoji: "⚡"
    requires:
      env: ["ASTRAI_API_KEY", "ANTHROPIC_API_KEY"]
    primaryEnv: "ASTRAI_API_KEY"
    files: ["plugin.py", "config.example.toml"]
tags: [inference, routing, privacy, cost-optimization, gdpr, eu, savings, llm-gateway]
---

# Astrai Inference Router

Route every LLM call through Astrai's intelligent router.
Save 40%+ on API costs. Privacy controls built in.

## What it does

- **Smart routing**: Classifies each task (code, research, chat, creative) and picks the optimal model
- **Cost savings**: Bayesian learning finds the cheapest provider that meets your quality threshold
- **Auto-failover**: Circuit breaker switches providers when one goes down
- **PII protection**: Personally identifiable information stripped before reaching any provider
- **EU routing**: GDPR-compliant European-only routing with one setting
- **Budget caps**: Set daily spend limits to prevent runaway costs
- **Real-time tracking**: See exactly how much you're saving per request

## Setup

1. Get a free API key at [as-trai.com](https://as-trai.com)
2. Set `ASTRAI_API_KEY` in your environment or skill config
3. Choose your privacy mode (default: `enhanced`)
4. Done — all LLM calls now route through Astrai

## Privacy Modes

- **standard**: Full routing intelligence, normal logging
- **enhanced**: PII stripped, metadata-only logging, region enforced
- **max**: Zero data retention, EU-only, all PII stripped, no prompt logging

## Environment Variables

| Variable | Required | Description | Default |
|---|---|---|---|
| `ASTRAI_API_KEY` | Yes | Your API key from as-trai.com | — |
| `PRIVACY_MODE` | No | standard, enhanced, max | enhanced |
| `REGION` | No | any, eu, us | any |
| `DAILY_BUDGET` | No | Max daily spend in USD (0 = unlimited) | 10 |

## External Endpoints

| Endpoint | Purpose | Data Sent |
|---|---|---|
| `https://as-trai.com/v1/chat/completions` | LLM inference routing | Prompts (with PII stripped if enhanced/max mode) |
| `https://as-trai.com/v1/signup` | Free API key registration | Email address |

## Security & Privacy

- All requests authenticated via API key in Authorization header
- PII stripping runs locally before any data leaves your machine (enhanced/max modes)
- EU routing mode ensures prompts never leave European infrastructure
- Zero data retention available in max privacy mode
- No credentials are stored by the skill — only your API key in environment variables
- Source code is fully open: [github.com/beee003/astrai-openclaw](https://github.com/beee003/astrai-openclaw)

## Model Invocation

This skill intercepts outgoing LLM API calls and reroutes them through the Astrai gateway. The gateway selects the optimal provider and model based on task type, cost, and quality. Your prompts are processed by third-party LLM providers (Anthropic, OpenAI, Google, Mistral, etc.) according to your region and privacy settings.

## Pricing

- **Free**: 1,000 requests/day, smart routing, failover
- **Pro** ($49/mo): Unlimited requests, EU routing, PII stripping, analytics
- **Business** ($199/mo): Multi-agent dashboards, compliance exports, SLA
