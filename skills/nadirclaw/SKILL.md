---
name: nadirclaw
version: 1.0.0
description: Install, configure, and run NadirClaw LLM router to cut AI API costs by 40-70%. Use when the user wants to reduce LLM spending, route prompts to cheaper models, set up cost-saving proxy, or optimize API usage across providers (OpenAI, Anthropic, Google, Ollama). Also use when asked about model routing, LLM cost optimization, or setting up NadirClaw with OpenClaw.
---

# NadirClaw Skill

NadirClaw is an open-source LLM router that classifies prompts in ~10ms and routes simple ones to cheap/local models while keeping complex work on premium models.

## Install

```bash
pip install nadirclaw
```

## Setup

Run the interactive wizard:
```bash
nadirclaw setup
```

Or auto-configure for OpenClaw:
```bash
nadirclaw openclaw onboard
```

This writes NadirClaw as a provider in OpenClaw config with model `nadirclaw/auto`. No restart needed.

## Start

```bash
nadirclaw serve --verbose
```

Runs on `http://localhost:8856`. Any OpenAI-compatible tool can use it by pointing to this URL.

## Point tools at NadirClaw

```bash
# OpenClaw (auto)
nadirclaw openclaw onboard

# Claude Code
ANTHROPIC_BASE_URL=http://localhost:8856/v1 claude

# Any OpenAI-compatible tool
OPENAI_BASE_URL=http://localhost:8856/v1 <tool>
```

## Routing profiles

Pass `x-routing-profile` header or use these models:
- `nadirclaw/auto` - smart routing (default)
- `nadirclaw/eco` - maximize savings
- `nadirclaw/premium` - always use best model
- `nadirclaw/free` - Ollama/local only
- `nadirclaw/reasoning` - chain-of-thought optimized

## Monitor savings

```bash
nadirclaw savings      # cost savings report
nadirclaw report       # detailed routing analytics
nadirclaw dashboard    # live terminal dashboard
```

## Key features

- ~10ms classification overhead
- Session persistence (no model bouncing mid-conversation)
- Rate limit fallback (auto-retry on 429)
- Agentic task detection (forces premium for tool use)
- Context-window filtering (auto-swaps for long conversations)
- Supports: OpenAI, Anthropic, Google Gemini, Ollama, any LiteLLM provider

## Troubleshooting

- If `nadirclaw serve` fails, check API keys: `nadirclaw setup`
- For Ollama: ensure `ollama serve` is running first
- Logs: `nadirclaw report --last 20` to see recent routing decisions
- Raw debug: `nadirclaw serve --verbose --log-raw`
