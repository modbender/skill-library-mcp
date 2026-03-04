# Insight Engine — Architecture Reference

## Core principle

> "Tell me something I didn't know. Show me the data. Show your working."

Every insight must cite its source data. Every claim must be falsifiable. Uncertainty is
expressed explicitly. Patterns are separated from noise using statistical thresholds.

## Four-layer pipeline

### Layer 1 — Collection (raw data)
`src/collectors/` — fetch and normalise data from all sources. No interpretation here.

- `langfuse_data.py` — Langfuse REST API: traces, observations/generations, scores
- `openclaw_logs.py` — gateway logs + daily memory .md files
- `git_collector.py` — commit history across tracked repos
- `cp_trends.py` — Control Plane promotion tracks and history (optional)

### Layer 2 — Statistics (what the numbers say)
`build_*_data_packet()` in `engine.py` — pure Python aggregation:
- Token usage totals, distributions, per-model breakdown
- Cost: actual spend, model mix ratios
- Latency: p50/p95/p99 per model, outlier detection (>2σ from mean)
- Experiment results: confidence intervals on eval scores, not just means
- Anomalies: any metric outside expected range flagged with supporting data

### Layer 3 — Patterns (what the numbers mean)
LLM prompt (`prompts/daily_analyst.md`) receives the structured data packet and identifies:
- Which task types cost the most per unit of value?
- Is complexity increasing (more expensive model calls)?
- Are shadow tests converging toward promotion thresholds?
- Time-of-day / day-of-week usage patterns

### Layer 4 — Insights (so what?)
Actionable conclusions from Layer 2+3 evidence. Each insight:
- States what it found
- Cites the specific data point(s)
- States confidence level (High/Medium/Low) with reason
- States what action, if any, it implies

## Prompts and citation enforcement

The system prompts (`prompts/`) enforce citation discipline:

```
Every factual claim must reference a specific number from the data packet.
"Usage was high" → unacceptable.
"Input tokens were 14,320 — 2.3× the 7-day mean of 6,218" → acceptable.
```

If fewer than N data points exist for a trend, the prompt instructs the model to report
"insufficient data (n=X)" rather than extrapolating.

## Key design decisions

1. **Stats before LLM**: Compute all numbers in Python first. Feed LLM a structured JSON
   packet, not raw logs. The LLM's job is interpretation, not aggregation.

2. **Dry-run = free**: `--dry-run` uses local Ollama (zero API cost) to preview output
   before committing to Anthropic API + Notion write.

3. **Data-only mode**: `--data-only` outputs the full data packet + system prompt to stdout.
   Useful for agent/subagent consumption without any API calls.

4. **Graceful degradation**: All collectors (Langfuse, CP, Git) catch exceptions and return
   empty/error dicts. The engine continues with what's available.

5. **Separation of concerns**: Collectors are pure data extraction. Writers are pure Notion I/O.
   Engine orchestrates. Each layer is independently testable.

## Reflection cadence

| Mode    | When                   | Data window | LLM model    |
|---------|------------------------|-------------|--------------|
| daily   | 11pm nightly (cron)    | 1 day       | claude-sonnet |
| weekly  | Sunday 11pm (cron)     | 7 days      | claude-sonnet |
| monthly | Last day of month 11pm | 30 days     | claude-opus  |

## Adding a new data source

1. Create `src/collectors/my_source.py` with a `fetch_*()` function returning a plain dict
2. Call it inside `build_daily_data_packet()` in `engine.py`
3. Add the new key's description to `prompts/daily_analyst.md` under "Data sources"
4. The LLM will automatically incorporate it in its analysis

## Environment variables reference

| Var                    | Required | Default                     | Description                      |
|------------------------|----------|-----------------------------|----------------------------------|
| `ANTHROPIC_API_KEY`    | Yes (live run) | —               | Anthropic API key                |
| `NOTION_API_KEY`       | Yes (live run) | —               | Notion integration token         |
| `LANGFUSE_BASE_URL`    | No       | `http://localhost:3100`     | Langfuse server URL              |
| `LANGFUSE_PUBLIC_KEY`  | No       | from config                 | Langfuse public key              |
| `LANGFUSE_SECRET_KEY`  | No       | from config                 | Langfuse secret key              |
| `NOTION_ROOT_PAGE_ID`  | Yes (live run) | from config      | Notion root page                 |
| `NOTION_DAILY_DB_ID`   | Yes (daily)    | from config      | Notion daily DB                  |
| `OPENCLAW_LOG_DIR`     | No       | `/tmp/openclaw`             | Daily log files directory        |
| `OPENCLAW_MEMORY_DIR`  | No       | `~/.openclaw/memory`        | Daily memory .md files directory |
| `CP_API_URL`           | No       | `http://localhost:8765`     | Control plane API URL            |
| `GIT_REPOS`            | No       | current dir                 | Comma-separated repo paths       |
| `OLLAMA_MODEL`         | No       | `mistral`                   | Model for --dry-run              |
| `OLLAMA_BASE_URL`      | No       | `http://localhost:11434`    | Ollama server URL                |
