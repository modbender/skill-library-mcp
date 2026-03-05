---
name: insight-engine
version: 1.0.2
metadata:
  {
    "openclaw": {
      "emoji": "🔬",
      "requires": { "bins": ["python3", "ollama"], "env": ["ANTHROPIC_API_KEY", "NOTION_API_KEY"] },
      "primaryEnv": "ANTHROPIC_API_KEY",
      "network": { "outbound": true, "reason": "Calls Anthropic API for statistical interpretation of pre-computed data. Writes reports to Notion API. Raw data analysis is local Python — no raw logs leave the machine." }
    }
  }
description: "Logs/metrics → Python statistics → LLM interpretation → Notion reports. Use when: generating daily/weekly/monthly operational insights from AI system logs, producing data-driven Notion reports from Langfuse traces and gateway logs, setting up a cron-based insight pipeline, building a citation-enforcing analyst that refuses to make claims without specific data. Pattern: collect raw data → compute stats in Python → feed structured packet to LLM → write to Notion."
---

# insight-engine

Data-driven insights from operational logs: collect → stats → LLM interpretation → Notion.

## Architecture

```
collect (Python stats only)
  ├── Langfuse OTEL traces/scores/observations
  ├── OpenClaw/gateway logs
  ├── Git activity
  └── Control plane scores
↓
build_*_data_packet()  ← all stats computed in Python before LLM call
↓
call_claude(system_prompt, structured_json)  ← LLM interprets, doesn't compute
↓
write_*_reflection() → Notion
```

See `references/architecture.md` for full design rationale.

## Quick start

```bash
# Install deps
pip install anthropic requests pyyaml

# Configure
cp scripts/config/analyst.yaml.example config/analyst.yaml
# Edit config/analyst.yaml — set langfuse URL, notion IDs, model choices

# Dry run (local Ollama, no Notion write)
python3 scripts/src/engine.py --mode daily --dry-run

# Print data packet + prompt to stdout (for agent consumption, no API calls)
python3 scripts/src/engine.py --mode daily --data-only

# Live run
python3 scripts/src/engine.py --mode daily
python3 scripts/src/engine.py --mode weekly
python3 scripts/src/engine.py --mode monthly
```

## Required env vars

```bash
ANTHROPIC_API_KEY=sk-ant-...    # Anthropic API key
NOTION_API_KEY=secret_...       # Notion integration token
LANGFUSE_BASE_URL=http://localhost:3100   # Langfuse server URL
LANGFUSE_PUBLIC_KEY=pk-lf-...   # Langfuse public key
LANGFUSE_SECRET_KEY=sk-lf-...   # Langfuse secret key
NOTION_ROOT_PAGE_ID=<uuid>      # Root Notion page for reports
NOTION_DAILY_DB_ID=<uuid>       # Notion database for daily entries
```

Or configure in `config/analyst.yaml`.

## Key design principles

1. **Stats before LLM** — Python computes all numbers. The LLM interprets, doesn't aggregate.
2. **Citation-enforcing prompts** — System prompts require every claim to cite a specific number.
3. **No hallucinated trends** — `< 7 data points` → report "insufficient data (n=X)"
4. **Dry-run mode** — Uses local Ollama (free) to preview output; skip Notion write.
5. **Data-only mode** — Outputs the full data packet + prompts for agent/subagent use.

## Cron setup (LaunchAgent example)

```xml
<!-- ~/Library/LaunchAgents/com.yourname.insight-engine-daily.plist -->
<key>StartCalendarInterval</key>
<dict>
  <key>Hour</key><integer>23</integer>
  <key>Minute</key><integer>0</integer>
</dict>
<key>ProgramArguments</key>
<array>
  <string>/usr/bin/python3</string>
  <string>/path/to/insight-engine/scripts/src/engine.py</string>
  <string>--mode</string><string>daily</string>
</array>
```

## Extending to new data sources

Add a collector in `scripts/src/collectors/`:
1. Create `my_source.py` with a `fetch_*()` function returning a plain dict
2. Import and call it in `build_daily_data_packet()` in `engine.py`
3. Reference the new key in `prompts/daily_analyst.md` under "Data sources"

## See also

- `references/architecture.md` — full design rationale and layer descriptions
- `scripts/prompts/daily_analyst.md` — system prompt with citation rules
- `scripts/config/analyst.yaml.example` — config template
