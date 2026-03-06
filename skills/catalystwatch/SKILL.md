---
name: catalystwatch
description: Monitor and analyze market-moving catalysts for equities and other
  financial instruments.
---


# CatalystWatch

Monitor and analyze market-moving catalysts for equities and other financial instruments.

## What it does

CatalystWatch tracks upcoming and recent catalysts that can move stock prices, including:

- **Earnings reports** — scheduled dates, consensus estimates, whisper numbers, and historical surprise trends
- **FDA decisions** — PDUFA dates, advisory committee meetings, and approval/rejection outcomes
- **Economic data** — jobs reports, CPI/PPI, FOMC meetings, and other macro releases
- **Corporate events** — M&A announcements, spin-offs, share buybacks, insider transactions, and activist campaigns
- **Sector catalysts** — industry conferences, regulatory rulings, and commodity supply disruptions

## Usage

Ask your agent to monitor catalysts for a ticker, sector, or watchlist:

- "What catalysts are coming up for AAPL this month?"
- "Show me all FDA decision dates for biotech stocks this quarter"
- "Alert me when any stock on my watchlist has an earnings surprise above 10%"
- "Summarize today's macro calendar and expected market impact"

## Configuration

Set the following environment variables for data source access:

- `CATALYSTWATCH_API_KEY` — API key for CatalystWatch. Used to authenticate requests for earnings calendars, FDA event dates, macro release schedules, and corporate action data.
- `CATALYSTWATCH_WATCHLIST` — (optional) default watchlist of tickers to monitor, comma-separated (e.g., `AAPL,TSLA,NVDA`).
