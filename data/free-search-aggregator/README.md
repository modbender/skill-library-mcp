<p align="center">
  <img src="assets/hero.jpg?v=6d74a19" alt="Free Search Aggregator" width="100%" />
</p>

<h1 align="center">Free Search Aggregator</h1>

<p align="center">
Quota-aware web search for OpenClaw with 12 providers, automatic failover,
task-level multi-query search, and managed storage under <code>memory/</code>.
</p>

## What’s New (v1.2.x)

- Expanded provider pool to **12 providers**
- Added: **Exa, Bing RSS, Mojeek, Wikipedia, Google CSE, Baidu, SearXNG**
- Introduced clearer quota capability mapping for new providers
- Updated docs and setup guidance for API + no-key providers
- Smoke-tested core flow (`status/search/task/remaining/storage`) after rollout

---

## Highlights

- **12 providers** (6 work without API keys)
- **Auto failover** when provider fails (auth/rate/network/upstream)
- **Task search** (`task`) with query expansion + deduped merged results
- **Quota controls**: tracked quota + real quota (supported providers)
- **Preset modes**:
  - default: `workers=1`
  - `@dual`: `workers=2`
  - `@deep`: `workers=3` + deeper query coverage
- **Managed storage** (cache/index/report) to avoid workspace clutter

---

## Provider Matrix

| Provider | Key Required | Free Quota | Notes |
|---|---|---:|---|
| `brave` | `BRAVE_API_KEY` | 2000/day | Independent index, high quality |
| `exa` | `EXA_API_KEY` | ~33/day (1000/month) | Semantic search |
| `tavily` | `TAVILY_API_KEY` | 1000/day | AI-agent optimized |
| `duckduckgo` | No | ~500/day | Privacy-first fallback |
| `bing_html` | No | ~300/day | Bing RSS endpoint (stable XML) |
| `mojeek` | Optional (`MOJEEK_API_KEY`) | ~200/day | Independent index |
| `serper` | `SERPER_API_KEY` | 2500/day | Google-backed results |
| `searchapi` | `SEARCHAPI_API_KEY` | 100/month | Multi-engine API |
| `google_cse` | `GOOGLE_API_KEY` + `GOOGLE_CX` | 100/day | Official Google CSE |
| `baidu` | `BAIDU_API_KEY` | 200/day | Strong CN coverage |
| `wikipedia` | No | ~1000/day | Factual/encyclopedic |
| `searxng` | No (self-hosted) | depends | Requires private instance |

> With all keys configured, total tracked daily capacity is ~8400+.

---

## Quick Start

```bash
# Normal search
scripts/search "latest ai agent frameworks 2026" --max-results 5

# Task-level search
scripts/search task "@dual Compare Claude vs GPT-4 for code generation" --max-results 5

# Deep task search
scripts/search task "@deep autonomous driving safety 2026" --max-results 8 --max-queries 10

# Tracked quota status
scripts/status

# Real quota (supported providers)
scripts/remaining --real

# Optional probe for header-only providers (may consume quota)
scripts/remaining --real --probe

# Cleanup old cache files (default: 14 days)
scripts/gc --cache-days 14
```

---

## CLI

```bash
python -m free_search "<query>"
python -m free_search task "<task>" [--workers 1|2|3] [--max-queries N]
python -m free_search status [--real] [--probe]
python -m free_search remaining --real [--probe]
python -m free_search gc --cache-days 14 [--report-days 90]
```

---

## Python API

```python
from free_search import search, task_search, get_quota_status, get_real_quota

payload = search("latest LLM eval benchmark", max_results=5)

task_payload = task_search(
    "Compare Claude vs GPT-4 for code generation",
    max_results_per_query=5,
    max_queries=6,
    max_workers=2,
)

status = get_quota_status()
real = get_real_quota()
```

---

## Post-install Smoke Check (Recommended)

```bash
# 1) Config/provider load
scripts/status --compact

# 2) Basic search smoke test
scripts/search "openclaw" --max-results 3 --compact

# 3) Verify storage paths
ls -la /home/openclaw/.openclaw/workspace/memory/search-cache/ | tail -n 5
ls -la /home/openclaw/.openclaw/workspace/memory/search-index/
ls -la /home/openclaw/.openclaw/workspace/memory/search-reports/ | tail -n 5

# 4) Optional real quota check
scripts/remaining --real --compact
```

---

## Data Organization (Managed)

All artifacts are persisted under `memory/`:

- `memory/search-cache/YYYY-MM-DD/*.json` — raw cache
- `memory/search-index/search-index.jsonl` — append-only index
- `memory/search-reports/YYYY-MM-DD/*.md` — human-readable reports

Recommended retention:

- cache: **14 days**
- reports: **long-term**

---

## Real Quota Support

| Provider | Real quota support |
|---|---|
| Tavily | ✅ official usage endpoint |
| SearchAPI | ✅ official account endpoint |
| Brave | ⚠ via `--probe` header check |
| Serper | ❌ no public endpoint |
| DuckDuckGo / Bing / Mojeek / Wikipedia | N/A |
| Exa / Google CSE / Baidu | ❌ no public quota endpoint |

---

## Notes

- `@deep` optimizes for **coverage depth**, not brute-force burn.
- If quota usage gets high, concurrency may auto-downgrade.
- Keep `workers=1` for default workflows, enable `@dual/@deep` only when needed.
