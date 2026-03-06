# SEC Watcher — Free AI/Tech Filing Monitor

> An OpenClaw skill that monitors SEC EDGAR for new filings from 30+ AI and technology companies.

## What it does

SEC Watcher queries the SEC's EDGAR full-text search API and surfaces recent filings, sorted by signal importance. It flags high-signal events like leadership changes (Item 5.02), material agreements (Item 1.01), and acquisitions (Item 2.01) so you catch what matters without reading every filing.

## Install

**Via ClawHub:**
```bash
npx clawhub@latest install sec-watcher
```

**Manual install:**
```bash
# Global (available in all sessions)
cp -r sec-watcher/ ~/.openclaw/skills/sec-watcher

# Or workspace-local
cp -r sec-watcher/ ./skills/sec-watcher
```

## Usage

Once installed, just ask your OpenClaw agent:

- *"Check SEC filings for NVIDIA"*
- *"Any new 8-K filings today?"*
- *"Show me recent SEC filings for AI companies"*
- *"What did Palantir file this week?"*

The agent will run the fetcher script and present results grouped by signal level.

## Requirements

- Python 3.8+
- No external packages (stdlib only: `urllib`, `json`, `argparse`)
- No API keys needed — EDGAR is free and public

## Customizing the watchlist

Edit `scripts/fetch-filings.py` and modify the `WATCHLIST` array to add or remove companies.

## Publishing to ClawHub

```bash
openclaw skill validate ./sec-watcher
openclaw auth login
openclaw skill publish ./sec-watcher
```

## Full Intelligence

This skill provides raw SEC filing alerts. For cross-source signal correlation (SEC + hiring data + AI research papers + social signals + pattern detection), check out [Signal Report](https://signal-report.com).

## License

MIT
