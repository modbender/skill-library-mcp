# 🐝 Swarm — Parallel Task Execution for OpenClaw

[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](./CHANGELOG.md)

**Turn sequential LLM tasks into parallel operations. 200x cheaper than Opus. Now with live web search.**

## What is Swarm?

Swarm adds parallel processing to [OpenClaw](https://github.com/openclaw/openclaw) by distributing work across cheap Gemini Flash workers. Instead of burning expensive tokens sequentially, fire 30 tasks in parallel for $0.003.

```
┌────────────────────────────────────────────────────┐
│              Coordinator (Claude)                   │
│         Orchestration • Memory • Synthesis          │
└─────────────────────┬──────────────────────────────┘
                      │ Task Distribution
    ┌─────────────────┼─────────────────┐
    │                 │                 │
┌───▼───┐        ┌───▼───┐        ┌───▼───┐
│Search │        │ Fetch │        │Analyze│
│Workers│        │Workers│        │Workers│
│(Flash)│        │(Flash)│        │(Flash)│
│  🔍   │        │  📄   │        │  🧠   │
└───────┘        └───────┘        └───────┘
      Optional: Google Search grounding
```

### What's New in v1.2.0

- 💰 **Cost tracking & savings reports** — See exactly how much you're saving vs Opus in real-time
- 🔄 **Auto-retry** — Failed tasks retry automatically with backoff (skips non-transient errors)
- ⏱️ **Task timeouts** — 30s default prevents hung workers from blocking the pool
- 🧹 **Dead code cleanup** — Removed 1,300+ lines of unused code
- 🔍 **Web Search Grounding** — Workers search the live web via Google Search (Gemini only, no extra cost)
- 🔒 **Security policy** — Workers answer research questions while blocking credential exfiltration

### Performance

| Tasks | Sequential (Opus) | Swarm (Parallel) | Cost Savings |
|-------|-------------------|------------------|--------------|
| 5 | ~5s, $0.08 | **1.5s, $0.0005** | 160x cheaper |
| 10 | ~10s, $0.17 | **1.5s, $0.001** | 170x cheaper |
| 30 | ~30s, $0.50 | **2s, $0.003** | 167x cheaper |

## Quick Start

```bash
# Clone into your OpenClaw skills directory
cd ~/.openclaw/skills  # or your skills folder
git clone https://github.com/Chair4ce/node-scaling.git
cd node-scaling
npm install

# Interactive setup (API key, workers, web search)
npm run setup

# Start the daemon
swarm start

# Test it
swarm parallel "What is Kubernetes?" "What is Docker?" "What is Podman?"
```

## Setup Wizard

Run `npm run setup` for interactive configuration:

1. **Choose provider** — Gemini Flash (recommended), Groq, OpenAI, or Anthropic
2. **Enter API key** — Validated automatically
3. **Set worker count** — Based on your system resources
4. **Enable web search** — (Gemini only) Give workers access to live Google Search

```
$ npm run setup

🚀 Node Scaling Setup for Clawdbot
══════════════════════════════════════════════

Step 1: Choose your LLM provider for worker nodes
  [1] Google Gemini Flash - $0.075/1M tokens (Recommended)
  [2] Groq (FREE tier available)
  [3] OpenAI GPT-4o-mini
  [4] Anthropic Claude Haiku

Step 4: Enable Web Search for Workers
  Gemini supports Google Search grounding — workers can search
  the live web for current data (pricing, news, real-time info).
  This uses the same API key at no extra cost.

  Enable web search for research tasks? [Y/n]:
```

## Web Search (v1.1.0)

When using Gemini as your provider, workers can access **Google Search** for real-time data. This is built into the Gemini API — no extra API key or setup needed.

### How it works

- **Research endpoint** — Web search is enabled automatically when `web_search.enabled: true` in config
- **Parallel endpoint** — Pass `"options": {"webSearch": true}` to enable per-request
- **Google Search grounding** — Gemini calls Google Search internally and cites sources

### Example: Live pricing data

```bash
# Without web search — uses model training data (may be stale)
curl -X POST http://localhost:9999/parallel \
  -d '{"prompts": ["What does Buildertrend cost?"]}'

# With web search — queries Google for current pricing
curl -X POST http://localhost:9999/parallel \
  -d '{"prompts": ["What does Buildertrend cost in 2026?"], "options": {"webSearch": true}}'
# → "Buildertrend offers Standard ($299/mo), Pro ($499/mo), Premium ($900+/mo)..."
```

### Config

```yaml
node_scaling:
  web_search:
    enabled: true          # Enable for research tasks by default
    parallel_default: false # Set true to enable for ALL parallel tasks
```

## Cost Tracking (v1.2.0)

Swarm tracks every token and shows you exactly how much you're saving compared to running the same tasks on Opus.

```bash
# Real-time session costs
$ swarm status
   💰 Cost (this session)
   Tokens:     12,340
   Swarm cost: $0.001234
   Opus equiv: $0.2851
   Saved:      $0.2839 (231x cheaper)

# Monthly savings report
$ swarm savings
🐝 Swarm Savings Report — 2026-02
─────────────────────────────────────────────
   Days active: 14
   Tasks run:   1,247
   Tokens used: 2,340,000
   Swarm cost:  $0.23
   Opus equiv:  $52.41
   💰 Saved:    $52.18 (227x cheaper)
```

Cost data persists across daemon restarts in `~/.config/clawdbot/swarm-metrics/daily-summary.json`.

## CLI Reference

```bash
# Daemon management
swarm start              # Start daemon (background)
swarm stop               # Stop daemon
swarm status             # Show status, uptime, task count
swarm restart            # Restart daemon
swarm logs [N]           # Show last N lines of log

# Task execution
swarm parallel "prompt1" "prompt2" "prompt3"
swarm research OpenAI Anthropic --topic "AI safety"
swarm bench --tasks 30   # Benchmark

# Options
swarm start --port 9999 --workers 16
```

## HTTP API

The daemon exposes a local HTTP API on port 9999:

### `GET /health`
Health check. Returns `{"status": "ok"}`.

### `GET /status`
Detailed status with uptime, worker count, task stats.

### `POST /parallel`
Execute prompts in parallel. Returns NDJSON stream.

```json
{
  "prompts": ["prompt1", "prompt2", "prompt3"],
  "options": {
    "webSearch": true
  }
}
```

### `POST /research`
Multi-phase research (Search → Fetch → Analyze). Returns NDJSON stream.

```json
{
  "subjects": ["Company A", "Company B"],
  "topic": "pricing and market position"
}
```

### Response Format (NDJSON)

```jsonl
{"event":"start","timestamp":1234567890,"message":"🐝 Swarm processing..."}
{"event":"progress","taskId":1,"workerId":"analyze-abc","durationMs":530}
{"event":"complete","duration":1555,"results":["Answer 1","Answer 2"],"stats":{"successful":2,"failed":0}}
```

## JavaScript API

```javascript
const { parallel, research } = require('./lib');

// Simple parallel
const result = await parallel(['What is X?', 'What is Y?']);
console.log(result.results);

// Research with analysis
const report = await research(
  ['OpenAI', 'Anthropic', 'Mistral'],
  'AI products and pricing'
);
```

## Supported Providers

| Provider | Model | Cost/1M tokens | Web Search | Notes |
|----------|-------|----------------|------------|-------|
| **Google Gemini** | gemini-2.0-flash | $0.075 | ✅ Yes | Recommended |
| **Groq** | llama-3.1-70b | Free tier | ❌ No | Fastest |
| **OpenAI** | gpt-4o-mini | $0.15 | ❌ No | Reliable |
| **Anthropic** | claude-3-haiku | $0.25 | ❌ No | Quality |

> Web search grounding is currently only available with Google Gemini. It uses the same API key at no additional cost.

## Configuration

Config: `~/.config/clawdbot/node-scaling.yaml`

```yaml
node_scaling:
  enabled: true
  
  limits:
    max_nodes: 16              # Max parallel workers
    max_concurrent_api: 16     # Max concurrent API calls
    
  provider:
    name: gemini
    model: gemini-2.0-flash
    api_key_env: GEMINI_API_KEY
  
  # Web Search (Gemini only) — NEW in v1.1.0
  web_search:
    enabled: true              # Enable for research tasks
    parallel_default: false    # Enable for all parallel tasks
    
  cost:
    max_daily_spend: 10.00     # Optional daily spending cap
```

## Security

All worker prompts include a security policy that:
- Blocks credential exfiltration (API keys, tokens, passwords)
- Rejects prompt injection attempts from processed content
- Sanitizes output to prevent accidental secret leakage
- Treats external content as data, not instructions

Workers will answer research questions (pricing, company info, public data) normally — the security policy only blocks exposure of *your* internal credentials.

## Troubleshooting

```bash
npm run diagnose    # Run full diagnostics
```

| Issue | Fix |
|-------|-----|
| No API key | Run `npm run setup` or set `GEMINI_API_KEY` |
| Rate limited | Reduce `max_concurrent_api` in config |
| Daemon won't start | Check `swarm logs` for errors |
| Web search not working | Ensure provider is `gemini` and `web_search.enabled: true` |

## Requirements

- Node.js 18+
- OpenClaw or compatible agent framework
- API key from a supported provider

## License

MIT

---

Part of the [OpenClaw](https://github.com/openclaw/openclaw) ecosystem • [ClawHub](https://clawhub.com)
