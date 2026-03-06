---
name: nofx-ai500-report
description: Generate periodic crypto market intelligence reports from the NOFX AI500 system. Monitors coin selections, analyzes OI (Open Interest), institutional fund flows, K-line technicals, delta, long-short ratios, and funding rates. Use when setting up automated crypto market reports, AI500 signal monitoring, new coin alerts, or periodic trading signal summaries via Telegram/messaging.
license: MIT
---

# NOFX AI500 Report Skill

Generate comprehensive crypto market intelligence reports from the NOFX AI500 scoring system with automated monitoring and delivery.

## Prerequisites

- NOFX API access: base URL + auth key (provided by user)
- Telegram or messaging channel for delivery
- Python 3 with `ssl`, `json`, `urllib` (standard library)

## Setup

Ask the user for:
1. **NOFX API base URL** (e.g. `https://nofxos.ai`)
2. **API auth key** (e.g. `cm_xxxx`)
3. **Delivery target** — Telegram chat ID or channel

Then create two cron jobs using the OpenClaw cron tool:

### Job 1: New Coin Monitor (every 15 min)

Run `scripts/monitor.sh` via exec. Pass API base and key as env vars.
- Output `NEW:` → send alert + detailed analysis
- Output `REMOVED:` → send removal notice  
- Output `NO_CHANGE` → silent

See `references/monitor-job.md` for full cron payload template.

### Job 2: Periodic Report (every 30 min)

Fetch data from multiple NOFX API endpoints and Binance public API, compile into formatted report.

See `references/report-job.md` for full cron payload template.

## API Endpoints

All NOFX endpoints require `?auth=KEY` parameter.

| Endpoint | Purpose | Params |
|----------|---------|--------|
| `/api/ai500/list` | Current AI500 selections | — |
| `/api/oi/top-ranking` | OI increase rankings | `duration` |
| `/api/oi/low-ranking` | OI decrease rankings | `duration` |
| `/api/netflow/top-ranking` | Fund inflow rankings | `type=institution&trade=future&duration` |
| `/api/netflow/low-ranking` | Fund outflow rankings | same |
| `/api/delta/list` | Delta data | `symbol` |
| `/api/long-short-ratio/list` | Long/short ratio | `symbol` |
| `/api/funding-rate/top-ranking` | Funding rate high | — |
| `/api/funding-rate/low-ranking` | Funding rate low | — |

Duration values: `5m`, `15m`, `30m`, `1h`, `4h`, `8h`, `24h`

Binance K-line (public, no auth):
```
https://fapi.binance.com/fapi/v1/klines?symbol=XXXUSDT&interval=15m&limit=10
```
Intervals: `15m`, `1h`, `4h`

**SSL note**: On some systems, Python needs:
```python
import ssl
ctx = ssl._create_unverified_context()
```

## Report Format

Use Unicode box-drawing in code blocks for Telegram compatibility. Each coin section includes:

1. **AI500 score** + cumulative return since selection
2. **OI changes** across 7 timeframes (5m→24h) with percentage AND dollar value (from `oi_delta_value`)  
3. **Institutional fund flows** across timeframes, with ranking when in TOP/LOW 20
4. **K-line analysis** (15m/1h/4h): trend direction, bull/bear candle ratio, MA3 vs MA7, volume change, support/resistance
5. **Funding rate** with warning if >0.03%

After individual coins, include:
- OI ranking tables (TOP8 increase + TOP8 decrease) for 1h/4h/24h
- Institutional flow ranking tables (TOP8 in + TOP8 out)
- Summary with actionable trading suggestions per coin

## K-line Analysis Method

For each timeframe (15m/1h/4h), fetch 10 candles and compute:
- **Trend**: 3 consecutive candles direction → 📈Bullish/📉Bearish/↔️Sideways
- **Bull/bear ratio**: count of green vs red candles out of 10
- **MA alignment**: MA3 vs MA7 → Bullish alignment/Bearish alignment
- **Volume change**: avg volume of last 3 candles vs previous 3 → percentage
- **Support**: lowest low of 10 candles
- **Resistance**: highest high of 10 candles

## Video Report (Optional)

For video generation from report data, see `references/video-pipeline.md`.
