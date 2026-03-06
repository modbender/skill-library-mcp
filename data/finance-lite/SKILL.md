---
name: finance_lite
description: Daily macro + market brief (FRED + benchmarks + watchlist ticker) with critical-headline triage, explicit source/freshness notes, and graceful fallback behavior. Use when the user asks for a concise “what moved today and why” summary with practical context.
user-invocable: true
command-dispatch: tool
command-tool: exec
---

# Finance Lite (Core Publish Bundle)

Slim publish bundle focused on core briefing commands.

## Runtime requirements (explicit)
- Required environment variable: `FINNHUB_API_KEY`
- Optional environment variable: `NASDAQ_DATALINK_API_KEY` (alias: `NASDAQ_DATA_LINK_API_KEY`)
- Required binaries: `node`, `curl`

Set in environment:
- `export FINNHUB_API_KEY="<your_finnhub_key>"`
- `export NASDAQ_DATALINK_API_KEY="<your_nasdaq_key>"`

## Dispatch (deterministic)
- `brief` → `node ./scripts/finance_lite/brief.mjs brief`
- `macro` → `node ./scripts/finance_lite/brief.mjs macro`
- `bench` → `node ./scripts/finance_lite/brief.mjs bench`
- `list` → `node ./scripts/finance_lite/brief.mjs list`
- `add <TICKER>` → `node ./scripts/finance_lite/brief.mjs add <TICKER>`
- `add <TICKER> bench` → `node ./scripts/finance_lite/brief.mjs add <TICKER> bench`
- `remove <TICKER>` → `node ./scripts/finance_lite/brief.mjs remove <TICKER>`
- `<TICKER>` → `node ./scripts/finance_lite/brief.mjs <TICKER>`

## Behavior + persistence notes
- The tool performs outbound requests to finance/news endpoints (FRED/Finnhub/Nasdaq/Finviz-linked feeds).
- The tool writes local cache under `./scripts/finance_lite/.cache/` (inside the bundle runtime directory).
- `add/remove` commands modify bundled `./scripts/finance_lite/watchlist.json`.
- This core bundle does not include calendar/event-sync commands.

## Scope and guardrails
- Decision-support only (not investment advice).
- Lead with dominant active driver first, then secondary factors.
- Keep output concise, structured, and source-aware.

## Required output floor
Always include:
- Header: `📈 Finance Lite — YYYY-MM-DD (PT)`
- Macro blocks: Inflation, Labor, Growth, Rates/Risk, Housing
- Benchmarks: SPY and GLD
- NVDA line and critical headlines section
- Notes:
  - `Note: SPY/GLD trend uses Nasdaq (daily lag). NVDA is quote-only (no Finnhub candles).`
  - `⚠️ Decision-support only; watch upcoming macro events & earnings.`