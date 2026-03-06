# openclaw-monitor

[![Tests](https://img.shields.io/badge/tests-10%20passing-brightgreen)]() [![Node](https://img.shields.io/badge/node-%3E%3D18-blue)]() [![License: MIT](https://img.shields.io/badge/license-MIT-yellow)]()

> System health monitoring — token spend, task success rates, cron health, and cost analysis.

Track everything your AI agents are spending and doing. Monitor token usage by model and skill, watch task success rates, keep tabs on cron job health, and generate cost breakdowns — all from the command line with `.md` interchange reports.

## Features

- **Token spend tracking** — ingest and report on token usage by model and skill
- **Task success rates** — track success, failure, and timeout rates
- **Cron health** — monitor job execution with pass/fail and duration stats
- **Cost analysis** — breakdowns by model, day, week, or month
- **Daily aggregation** — automatic rollup of metrics into daily summaries
- **Status dashboard** — quick system health summary with emoji indicators
- **Interchange reports** — generate `.md` files for cross-skill visibility
- **Backup & restore** — full database backup and recovery

## Quick Start

```bash
cd skills/monitoring
npm install

# Quick health check
node src/cli.js status

# Ingest some events
node src/cli.js ingest token --model gpt-4 --in 1500 --out 500 --cost 0.045 --skill crm
node src/cli.js ingest task --command "deal-sync" --status success --duration 1200

# View reports
node src/cli.js tokens --period 7d --by model
node src/cli.js cost --period week
```

## CLI Reference

### Reports

```bash
monitor status                          # System health summary
monitor tokens [--period <7d>] [--by <model|skill>]   # Token usage report
monitor tasks [--failed]                # Task history (optionally failures only)
monitor crons                           # Cron job health
monitor cost [--period <week|month>]    # Cost breakdown
```

### Event Ingestion

```bash
monitor ingest token --model <model> --in <n> --out <n> --cost <usd> [--skill <name>]
monitor ingest task --command <cmd> --status <success|failure|timeout> --duration <ms> [--error <msg>]
monitor ingest cron --job <name> --status <success|failure> --duration <ms> [--error <msg>]
```

### Utilities

```bash
monitor aggregate [--date <YYYY-MM-DD>]   # Compute daily aggregates
monitor refresh                            # Regenerate interchange .md files
monitor backup [--output <path>]
monitor restore <backup-file>
```

## Architecture

SQLite database (`data/`) stores raw events (tokens, tasks, crons) and daily aggregates. Events are ingested with deduplication. The aggregator rolls up raw events into daily summaries for fast reporting.

## .md Interchange

Running `monitor refresh` generates health report `.md` files in the `interchange/` directory. Other skills and agents can read these to understand system health, spending trends, and operational status.

## Testing

```bash
npm test
```

10 tests covering event ingestion, deduplication, aggregation, reporting, and interchange generation.

## Part of the OpenClaw Ecosystem

Monitoring is the observability layer. It tracks token spend from any skill, task outcomes from `orchestration`, and cron health. Reports are published via `@openclaw/interchange` for cross-skill consumption.

## License

MIT
