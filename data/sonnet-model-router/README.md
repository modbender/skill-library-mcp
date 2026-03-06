# 🧭 Model Router for OpenClaw

Self-learning multi-provider model routing. Auto-detects your available models, discovers new ones when you add them, fetches their benchmarks, and updates routing automatically.

Benchmarks are routing tables, not leaderboards.

## Install

```bash
clawhub install chandika/model-router
```

Or manually copy `SKILL.md` to your OpenClaw skills directory.

## How It Works

1. **Detects** which providers and models you have configured
2. **Maintains a registry** — `model-registry.json` with benchmark scores, pricing, and routing rules
3. **Discovers new models** — when you add a model to OpenClaw, the router detects it, fetches its model card and benchmarks via web search, and tells you where it fits
4. **Recommends** the best routing mode based on what's available
5. **Adapts** — "work harder" escalates to Opus, "save money" drops to Gemini/DeepSeek
6. **Hard routes by task** — computer use always goes to Claude (72.5% vs GPT's 38.2%), deep reasoning always goes to Opus

### New Model Detection

```
🧭 New model detected: Gemini 3 Pro

Pricing: $2.50 / $12.00 per 1M tokens
Context: 1M tokens

Key benchmarks:
- SWE-bench: 78.2% (current best: 80.8% from Opus)
- GPQA: 76.1% (beats Sonnet's 74.1%)

Recommendation: Use as subagent model in Balanced mode —
stronger reasoning than Gemini 2.5 Pro at similar cost.

Apply? [yes/no]
```

## Three Modes

### 🏆 Performance — "Work hard"

Opus 4.6 main, Sonnet 4.6 subagents. Best quality. Claude-only.

```json
{
  "agents": {
    "defaults": {
      "model": { "primary": "anthropic/claude-opus-4-6" },
      "subagents": { "model": "anthropic/claude-sonnet-4-6" }
    }
  }
}
```

### ⚖️ Balanced — "Normal" (recommended)

Sonnet 4.6 main, Gemini 2.5 Pro subagents. Good quality, rate limits survive.

```json
{
  "agents": {
    "defaults": {
      "model": { "primary": "anthropic/claude-sonnet-4-6" },
      "subagents": { "model": "google/gemini-2.5-pro" }
    }
  }
}
```

### 💰 Economy — "Save money"

Gemini 2.5 Pro main, Flash/DeepSeek subagents. Max efficiency.

```json
{
  "agents": {
    "defaults": {
      "model": { "primary": "google/gemini-2.5-pro" },
      "subagents": { "model": "google/gemini-2.5-flash" }
    }
  }
}
```

## Task Overrides (always apply)

| Task | Model | Why |
|------|-------|-----|
| Computer use / browser | Claude | 72.5% vs 38.2% — hard rule |
| Deep reasoning / novel problems | Opus 4.6 | 75.2% ARC-AGI-2 — uniquely capable |
| Office / finance | Sonnet 4.6 | 1633 Elo — beats everything incl. Opus |
| Drafts / summaries | Cheapest | Don't overthink it |

## Adaptive Triggers

| You say | It does |
|---------|---------|
| "work harder" | Suggests Performance mode |
| "save money" | Suggests Economy mode |
| "normal" / "reset" | Reverts to Balanced |
| "use opus for this" | Session-only override |

## Why

v1 solved Claude-only routing. v2 expanded to multi-provider. v2.1 makes it self-learning.

Add a new model to OpenClaw → the router detects it, researches its benchmarks, figures out where it beats your current setup, and asks if you want to use it. Remove a model → it reroutes affected tasks to the next best option.

One provider or five — the router adapts to what you have and keeps adapting as your setup changes.

See [SKILL.md](./SKILL.md) for full benchmark tables, all configs, and routing logic.

## License

MIT
