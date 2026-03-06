---
name: swarm
description: Cut your LLM costs by 200x. Offload parallel, batch, and research work to Gemini Flash workers instead of burning your expensive primary model.
homepage: https://github.com/Chair4ce/node-scaling
metadata: {"clawdbot":{"emoji":"🐝","requires":{"bins":["node"]}}}
---

# Swarm — Cut Your LLM Costs by 200x

**Turn your expensive model into an affordable daily driver. Offload the boring stuff to Gemini Flash workers — parallel, batch, research — at a fraction of the cost.**

## At a Glance

| 30 tasks via | Time | Cost |
|--------------|------|------|
| Opus (sequential) | ~30s | ~$0.50 |
| Swarm (parallel) | ~1s | ~$0.003 |

## When to Use

Swarm is ideal for:
- **3+ independent tasks** (research, summaries, comparisons)
- **Comparing or researching multiple subjects**
- **Multiple URLs** to fetch/analyze
- **Batch processing** (documents, entities, facts)
- **Complex analysis** needing multiple perspectives → use chain

## Quick Reference

```bash
# Check daemon (do this every session)
swarm status

# Start if not running
swarm start

# Parallel prompts
swarm parallel "What is X?" "What is Y?" "What is Z?"

# Research multiple subjects
swarm research "OpenAI" "Anthropic" "Mistral" --topic "AI safety"

# Discover capabilities
swarm capabilities
```

## Execution Modes

### Parallel (v1.0)
N prompts → N workers simultaneously. Best for independent tasks.

```bash
swarm parallel "prompt1" "prompt2" "prompt3"
```

### Research (v1.1)
Multi-phase: search → fetch → analyze. Uses Google Search grounding.

```bash
swarm research "Buildertrend" "Jobber" --topic "pricing 2026"
```

### Chain (v1.3) — Refinement Pipelines
Data flows through multiple stages, each with a different perspective/filter. Stages run in sequence; tasks within a stage run in parallel.

**Stage modes:**
- `parallel` — N inputs → N workers (same perspective)
- `single` — merged input → 1 worker
- `fan-out` — 1 input → N workers with DIFFERENT perspectives
- `reduce` — N inputs → 1 synthesized output

**Auto-chain** — describe what you want, get an optimal pipeline:
```bash
curl -X POST http://localhost:9999/chain/auto \
  -d '{"task":"Find business opportunities","data":"...market data...","depth":"standard"}'
```

**Manual chain:**
```bash
swarm chain pipeline.json
# or
echo '{"stages":[...]}' | swarm chain --stdin
```

**Depth presets:** `quick` (2 stages), `standard` (4), `deep` (6), `exhaustive` (8)

**Built-in perspectives:** extractor, filter, enricher, analyst, synthesizer, challenger, optimizer, strategist, researcher, critic

**Preview without executing:**
```bash
curl -X POST http://localhost:9999/chain/preview \
  -d '{"task":"...","depth":"standard"}'
```

### Benchmark (v1.3)
Compare single vs parallel vs chain on the same task with LLM-as-judge scoring.

```bash
curl -X POST http://localhost:9999/benchmark \
  -d '{"task":"Analyze X","data":"...","depth":"standard"}'
```

Scores on 6 FLASK dimensions: accuracy (2x weight), depth (1.5x), completeness, coherence, actionability (1.5x), nuance.

### Capabilities Discovery (v1.3)
Lets the orchestrator discover what execution modes are available:
```bash
swarm capabilities
# or
curl http://localhost:9999/capabilities
```

## Prompt Cache (v1.3.2)

LRU cache for LLM responses. **212x speedup on cache hits** (parallel), **514x on chains**.

- Keyed by hash of instruction + input + perspective
- 500 entries max, 1 hour TTL
- Skips web search tasks (need fresh data)
- Persists to disk across daemon restarts
- Per-task bypass: set `task.cache = false`

```bash
# View cache stats
curl http://localhost:9999/cache

# Clear cache
curl -X DELETE http://localhost:9999/cache
```

Cache stats show in `swarm status`.

## Stage Retry (v1.3.2)

If tasks fail within a chain stage, only the failed tasks get retried (not the whole stage). Default: 1 retry. Configurable per-phase via `phase.retries` or globally via `options.stageRetries`.

## Cost Tracking (v1.3.1)

All endpoints return cost data in their `complete` event:
- `session` — current daemon session totals
- `daily` — persisted across restarts, accumulates all day

```bash
swarm status        # Shows session + daily cost
swarm savings       # Monthly savings report
```

## Web Search (v1.1)

Workers search the live web via Google Search grounding (Gemini only, no extra cost).

```bash
# Research uses web search by default
swarm research "Subject" --topic "angle"

# Parallel with web search
curl -X POST http://localhost:9999/parallel \
  -d '{"prompts":["Current price of X?"],"options":{"webSearch":true}}'
```

## JavaScript API

```javascript
const { parallel, research } = require('~/clawd/skills/node-scaling/lib');
const { SwarmClient } = require('~/clawd/skills/node-scaling/lib/client');

// Simple parallel
const result = await parallel(['prompt1', 'prompt2', 'prompt3']);

// Client with streaming
const client = new SwarmClient();
for await (const event of client.parallel(prompts)) { ... }
for await (const event of client.research(subjects, topic)) { ... }

// Chain
const result = await client.chainSync({ task, data, depth });
```

## Daemon Management

```bash
swarm start              # Start daemon (background)
swarm stop               # Stop daemon
swarm status             # Status, cost, cache stats
swarm restart            # Restart daemon
swarm savings            # Monthly savings report
swarm logs [N]           # Last N lines of daemon log
```

## Performance (v1.3.2)

| Mode | Tasks | Time | Notes |
|------|-------|------|-------|
| Parallel (simple) | 5 | ~700ms | 142ms/task effective |
| Parallel (stress) | 10 | ~1.2s | 123ms/task effective |
| Chain (standard) | 5 | ~14s | 3-stage multi-perspective |
| Chain (quick) | 2 | ~3s | 2-stage extract+synthesize |
| Cache hit | any | ~3-5ms | 200-500x speedup |
| Research (web) | 2 | ~15s | Google grounding latency |

## Config

Location: `~/.config/clawdbot/node-scaling.yaml`

```yaml
node_scaling:
  enabled: true
  limits:
    max_nodes: 16
    max_concurrent_api: 16
  provider:
    name: gemini
    model: gemini-2.0-flash
  web_search:
    enabled: true
    parallel_default: false
  cost:
    max_daily_spend: 10.00
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Daemon not running | `swarm start` |
| No API key | Set `GEMINI_API_KEY` or run `npm run setup` |
| Rate limited | Lower `max_concurrent_api` in config |
| Web search not working | Ensure provider is gemini + web_search.enabled |
| Cache stale results | `curl -X DELETE http://localhost:9999/cache` |
| Chain too slow | Use `depth: "quick"` or check context size |

## Structured Output (v1.3.7)

Force JSON output with schema validation — zero parse failures on structured tasks.

```bash
# With built-in schema
curl -X POST http://localhost:9999/structured \
  -d '{"prompt":"Extract entities from: Tim Cook announced iPhone 17","schema":"entities"}'

# With custom schema
curl -X POST http://localhost:9999/structured \
  -d '{"prompt":"Classify this text","data":"...","schema":{"type":"object","properties":{"category":{"type":"string"}}}}'

# JSON mode (no schema, just force JSON)
curl -X POST http://localhost:9999/structured \
  -d '{"prompt":"Return a JSON object with name, age, city for a fictional person"}'

# List available schemas
curl http://localhost:9999/structured/schemas
```

**Built-in schemas:** `entities`, `summary`, `comparison`, `actions`, `classification`, `qa`

Uses Gemini's native `response_mime_type: application/json` + `responseSchema` for guaranteed JSON output. Includes schema validation on the response.

## Majority Voting (v1.3.7)

Same prompt → N parallel executions → pick the best answer. Higher accuracy on factual/analytical tasks.

```bash
# Judge strategy (LLM picks best — most reliable)
curl -X POST http://localhost:9999/vote \
  -d '{"prompt":"What are the key factors in SaaS pricing?","n":3,"strategy":"judge"}'

# Similarity strategy (consensus — zero extra cost)
curl -X POST http://localhost:9999/vote \
  -d '{"prompt":"What year was Python released?","n":3,"strategy":"similarity"}'

# Longest strategy (heuristic — zero extra cost)
curl -X POST http://localhost:9999/vote \
  -d '{"prompt":"Explain recursion","n":3,"strategy":"longest"}'
```

**Strategies:**
- `judge` — LLM scores all candidates on accuracy/completeness/clarity/actionability, picks winner (N+1 calls)
- `similarity` — Jaccard word-set similarity, picks consensus answer (N calls, zero extra cost)
- `longest` — Picks longest response as heuristic for thoroughness (N calls, zero extra cost)

**When to use:** Factual questions, critical decisions, or any task where accuracy > speed.

| Strategy | Calls | Extra Cost | Quality |
|----------|-------|-----------|---------|
| similarity | N | $0 | Good (consensus) |
| longest | N | $0 | Decent (heuristic) |
| judge | N+1 | ~$0.0001 | Best (LLM-scored) |

## Self-Reflection (v1.3.5)

Optional critic pass after chain/skeleton output. Scores 5 dimensions, auto-refines if below threshold.

```bash
# Add reflect:true to any chain or skeleton request
curl -X POST http://localhost:9999/chain/auto \
  -d '{"task":"Analyze the AI chip market","data":"...","reflect":true}'

curl -X POST http://localhost:9999/skeleton \
  -d '{"task":"Write a market analysis","reflect":true}'
```

Proven: improved weak output from 5.0 → 7.6 avg score. Skeleton + reflect scored 9.4/10.

## Skeleton-of-Thought (v1.3.6)

Generate outline → expand each section in parallel → merge into coherent document. Best for long-form content.

```bash
curl -X POST http://localhost:9999/skeleton \
  -d '{"task":"Write a comprehensive guide to SaaS pricing","maxSections":6,"reflect":true}'
```

**Performance:** 14,478 chars in 21s (675 chars/sec) — 5.1x more content than chain at 2.9x higher throughput.

| Metric | Chain | Skeleton-of-Thought | Winner |
|--------|-------|---------------------|--------|
| Output size | 2,856 chars | 14,478 chars | SoT (5.1x) |
| Throughput | 234 chars/sec | 675 chars/sec | SoT (2.9x) |
| Duration | 12s | 21s | Chain (faster) |
| Quality (w/ reflect) | ~7-8/10 | 9.4/10 | SoT |

**When to use what:**
- **SoT** → long-form content, reports, guides, docs (anything with natural sections)
- **Chain** → analysis, research, adversarial review (anything needing multiple perspectives)
- **Parallel** → independent tasks, batch processing
- **Structured** → entity extraction, classification, any task needing reliable JSON
- **Voting** → factual accuracy, critical decisions, consensus-building

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |
| GET | /status | Detailed status + cost + cache |
| GET | /capabilities | Discover execution modes |
| POST | /parallel | Execute N prompts in parallel |
| POST | /research | Multi-phase web research |
| POST | /skeleton | Skeleton-of-Thought (outline → expand → merge) |
| POST | /chain | Manual chain pipeline |
| POST | /chain/auto | Auto-build + execute chain |
| POST | /chain/preview | Preview chain without executing |
| POST | /chain/template | Execute pre-built template |
| POST | /structured | Forced JSON with schema validation |
| GET | /structured/schemas | List built-in schemas |
| POST | /vote | Majority voting (best-of-N) |
| POST | /benchmark | Quality comparison test |
| GET | /templates | List chain templates |
| GET | /cache | Cache statistics |
| DELETE | /cache | Clear cache |

## Cost Comparison

| Model | Cost per 1M tokens | Relative |
|-------|-------------------|----------|
| Claude Opus 4 | ~$15 input / $75 output | 1x |
| GPT-4o | ~$2.50 input / $10 output | ~7x cheaper |
| Gemini Flash | ~$0.075 input / $0.30 output | **200x cheaper** |

Cache hits are essentially free (~3-5ms, no API call).
