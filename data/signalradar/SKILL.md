---
name: signalradar
description: >-
  Monitors Polymarket prediction markets for probability changes and sends
  alerts when thresholds are crossed. Supports AI model releases, crypto,
  and geopolitics categories. Use when user asks to "check prediction markets",
  "monitor Polymarket", "track market probabilities", "set up market alerts",
  or "watch AI/crypto/geopolitics predictions". Do NOT use for stock market
  analysis, sports betting, or real-time trading signals.
  监控 Polymarket 预测市场概率变化，超过阈值时推送通知。支持 AI 模型发布、加密货币、
  地缘政治三大类别。不适用于股市分析、体育博彩或实时交易信号。
allowed-tools: "Bash(python3:*)"
license: MIT
compatibility: Python 3.9+, network access to gamma-api.polymarket.com. No pip dependencies (stdlib only).
metadata:
  openclaw:
    emoji: "📡"
    requires:
      bins: ["python3"]
      env: []
      pip: []
    primaryEnv: ""
    envHelp:
      NOTION_API_KEY:
        required: false
        description: "Notion integration secret. Only needed for watchlist-refresh mode."
        howToGet: "1. Go to https://www.notion.so/my-integrations\n2. Click 'New integration'\n3. IMPORTANT: Select 'Internal' type (NOT OAuth — OAuth requires company info and is for public apps)\n4. Name it anything (e.g. 'signalradar')\n5. Click 'Submit'\n6. Copy the 'Internal Integration Secret' (starts with ntn_)\n7. Go to your target Notion page → click '...' menu → 'Add connections' → select your integration"
        url: "https://www.notion.so/my-integrations"
      NOTION_PARENT_PAGE_ID:
        required: false
        description: "Notion page ID (32-char hex). Only needed for watchlist-refresh mode."
        howToGet: "Open the target Notion page in browser → look at the URL → copy the 32-character hex string after the page title (e.g. https://notion.so/My-Page-abc123def456... → the hex part is the ID)"
  author: Felix Xu
  version: 0.3.0
---

# SignalRadar

## AI Agent Instructions

When presenting SignalRadar results to the user:

- **Always show the market question** (slug), current probability, baseline, and absolute change in percentage points.
- **For HIT results**: highlight the market question, direction of change, and magnitude. Example: "GPT-5 release by June 2026 jumped from 32% to 41% (+9pp), crossing the 5pp threshold."
- **For BASELINE results**: tell the user "First run — baselines recorded for N markets. Run again later to detect changes." Do not present BASELINE as a problem.
- **For NO_REPLY results**: briefly confirm "No markets crossed the threshold" — do not dump raw JSON.
- **Do not manually edit or delete** `cache/`, `config/`, or baseline files unless the user explicitly asks. Note: normal runs automatically write baseline and cache files as part of standard operation — this is expected behavior, not a modification you need to initiate.
- **Never create cron jobs** or scheduled tasks automatically. Always confirm with the user first.
- **Do not re-run** monitoring in a loop. Run once per user request unless told otherwise.
- When the user says "check markets" or "any market signals", run `--mode ai` as the default unless a specific mode is requested.

## Quick Start

### Install

```bash
clawhub install signalradar
```

### Verify installation (two steps)

```bash
# 1. Health check — confirms Python and network connectivity
python3 scripts/signalradar.py doctor --output json

# 2. Dry-run — fetches live data but does not write state
python3 scripts/signalradar.py run --mode ai --dry-run --output json
```

Expected: `doctor` returns `{"status": "HEALTHY", ...}`. Dry-run returns a JSON object with `status` being one of `NO_REPLY`, `HIT`, or `BASELINE`.

**First run note**: The very first run for any mode will return `BASELINE` — this is normal. SignalRadar records the current probability as a baseline on the first run. Run again later (e.g., after 1 hour) to detect changes against that baseline.

## Monitoring Modes

SignalRadar monitors three categories of Polymarket prediction markets. Each mode has its own curated watchlist.

| Mode | Command | What it covers |
|------|---------|----------------|
| **ai** | `python3 scripts/signalradar.py run --mode ai` | AI model releases, AGI timelines, AI regulation |
| **crypto** | `python3 scripts/signalradar.py run --mode crypto` | Bitcoin, Ethereum, DeFi, stablecoin events |
| **geopolitics** | `python3 scripts/signalradar.py run --mode geopolitics` | Elections, conflicts, sanctions, treaties |
| **watchlist-refresh** | `python3 scripts/signalradar.py run --mode watchlist-refresh` | Refreshes watchlist by keyword-matching active Polymarket markets (requires Notion env vars). **Warning**: this auto-discovers markets by category keywords and may add 30-50 entries. Use `--dry-run` first to preview. |

Common flags:

- `--dry-run` — fetch and evaluate but do not write state or deliver alerts
- `--output json` — machine-readable JSON output (recommended for AI agents)
- `--config /path/to/config.json` — use a custom config file

## Understanding Results

Every run returns a JSON object. The `status` field indicates the outcome:

| Status | Meaning | What happens |
|--------|---------|--------------|
| `BASELINE` | First observation for an entry | Baseline recorded; no alert sent |
| `SILENT` | Change is below threshold | No alert sent |
| `HIT` | Change exceeds threshold | Alert emitted via delivery adapter |
| `NO_REPLY` | No entries crossed threshold this run | Nothing to report |

### HIT output example

```json
{
  "status": "HIT",
  "request_id": "9f98e47e-6e0e-4563-b7c8-87a3b19e97af",
  "hits": [
    {
      "entry_id": "polymarket:12345:gpt5-release-june:evt_67890",
      "slug": "gpt5-release-june",
      "current": 0.41,
      "baseline": 0.32,
      "abs_pp": 9.0,
      "confidence": "high",
      "reason": "abs_pp 9.0 >= threshold 5.0"
    }
  ],
  "ts": "2026-03-02T08:00:00Z"
}
```

When presenting a HIT to the user, format it as:
> **[slug]**: [baseline]% -> [current]% (+/-[abs_pp]pp) — [reason]

## Configuration

SignalRadar works out of the box with sensible defaults. All configuration is optional.

### Key settings

| Setting | Default | Description |
|---------|---------|-------------|
| `threshold.abs_pp` | 5.0 | Global threshold in percentage points |
| `threshold.per_category_abs_pp` | varies | Per-category override (e.g., AI: 4.0, Crypto: 8.0) |
| `baseline.cleanup_ttl_days` | 45 | Auto-cleanup stale baselines after N days |
| `delivery.primary.channel` | `openclaw` | Delivery adapter: `openclaw:direct`, `file:/path`, `webhook:https://...` |

### Delivery adapters

- **`openclaw:direct`** (default) — delivers to host messaging layer
- **`file:/path/to/alerts.jsonl`** — appends alerts to a local JSONL file
- **`webhook:https://example.com/hook`** — HTTP POST to external endpoint

For full configuration reference, see `references/config.md`.

## Local State (What This Skill Writes)

During normal operation (without `--dry-run`), SignalRadar writes the following local files:

| Path | Purpose | When written |
|------|---------|--------------|
| `cache/baselines/*.json` | Stores last-seen probability for each market | Every non-dry-run, to enable change detection |
| `cache/events/*.jsonl` | Audit log of all decisions (HIT/SILENT/BASELINE) | Every non-dry-run |
| `memory/polymarket_watchlist_2026.md` | Watchlist table for `ai` mode | Only by `watchlist-refresh` mode |

Use `--dry-run` to fetch and evaluate without writing any state. No files outside the skill directory are modified.

## Scheduling (Optional)

SignalRadar does not create scheduled tasks automatically. If the user wants periodic monitoring, they can set up system cron:

```bash
# Every hour — AI monitoring
0 * * * * cd /path/to/workspace && python3 skills/signalradar/scripts/signalradar.py run --mode ai

# Every 4 hours — Crypto
0 */4 * * * cd /path/to/workspace && python3 skills/signalradar/scripts/signalradar.py run --mode crypto

# Every 6 hours — Geopolitics
0 */6 * * * cd /path/to/workspace && python3 skills/signalradar/scripts/signalradar.py run --mode geopolitics
```

## Optional: Notion Integration

The `watchlist-refresh` mode syncs the monitoring watchlist from a Notion database. This is the **only mode that requires environment variables**.

### Setup

1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations) and click "New integration"
2. **Select "Internal" type** (NOT OAuth — OAuth is for public apps and requires company info)
3. Name it anything (e.g., "signalradar"), click "Submit"
4. Copy the "Internal Integration Secret" (starts with `ntn_`)
5. Open your target Notion page, click "..." menu, select "Add connections", choose your integration
6. Copy the page ID from the URL (the 32-character hex string after the page title)
7. Set environment variables:

```bash
export NOTION_API_KEY="ntn_xxxxxxxxxxxx"
export NOTION_PARENT_PAGE_ID="32-character-hex-from-page-url"
```

8. **Preview first** (recommended): `python3 scripts/signalradar.py run --mode watchlist-refresh --dry-run`
9. Run: `python3 scripts/signalradar.py run --mode watchlist-refresh`

**Important**: `watchlist-refresh` auto-discovers markets by keyword matching across all active Polymarket markets. It will add 30-50 entries based on configured categories (AI, crypto, geopolitics). To customize which markets are discovered, edit `config/watchlist_keywords.json`.

## Troubleshooting

| Error Code | Cause | Fix |
|------------|-------|-----|
| `SR_TIMEOUT` | Polymarket API did not respond within timeout | Check network connectivity; retry after 30s. If persistent, the API may be down. |
| `SR_SOURCE_UNAVAILABLE` | Cannot reach `gamma-api.polymarket.com` | Verify DNS resolution and internet access. Check if a proxy/VPN is blocking the request. |
| `SR_VALIDATION_ERROR` | Malformed entry data or schema mismatch | Run `python3 scripts/validate_schema.py` to identify the invalid field. Check `config/watchlist_keywords.json`. |
| `SR_ROUTE_FAILURE` | Delivery adapter failed to send alert | Check delivery config in `config.json`. For webhook: verify endpoint is reachable. For file: verify write permissions. |
| `SR_CONFIG_CONFLICT` | Contradictory config values | Review `config.json` for duplicate keys or invalid combinations. See `references/config.md`. |
| `SR_PERMISSION_DENIED` | Insufficient permissions for Notion API | Re-check `NOTION_API_KEY` and ensure the integration has access to the target page. |
| `SR_AUTH_MISSING` | Required Notion env vars not set | Set `NOTION_API_KEY` and `NOTION_PARENT_PAGE_ID`. Only needed for `watchlist-refresh` mode. |
| `SR_NOTION_PAGE_NOT_FOUND` | Notion page ID does not exist or is not shared | Verify `NOTION_PARENT_PAGE_ID` is correct (32-char hex). Ensure page is shared with the integration. |
| `SR_NOTION_READ_FAILURE` | Failed to read from Notion API | Check Notion API status. Verify the integration has read access to the page. |
| `SR_NOTION_WRITE_FAILURE` | Failed to write to Notion API | Check Notion API status. Verify the integration has write (insert content) permission. |

## References

- `references/config.md` — Full configuration reference
- `references/protocol.md` — Data contract (EntrySpec, SignalEvent, DeliveryEnvelope)
- `references/operations.md` — SLO targets, retry policy, observability requirements
- `references/notion-sync.md` — Notion integration details
- `references/platform-adapters.md` — Platform adapter specifications
