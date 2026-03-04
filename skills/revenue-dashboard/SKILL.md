---
description: Real-time revenue and portfolio dashboard — track crypto, freelance income, and services in one place.
---

# Revenue Dashboard

Track crypto holdings, freelance income, and service revenue from a single dashboard.

## Requirements

- Node.js 18+
- No external API keys required (uses CoinGecko free tier for crypto prices)

## Quick Start

```bash
cd {skill_dir}
npm install
npm run build
npm start -- --port 3020    # Production
# or
npm run dev                 # Development with hot reload
```

Open `http://localhost:3020` in your browser.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/portfolio` | Current portfolio summary |
| `GET` | `/api/revenue?from=YYYY-MM-DD&to=YYYY-MM-DD` | Revenue by date range |
| `POST` | `/api/transactions` | Add a crypto transaction |
| `GET` | `/api/holdings` | Current crypto holdings |
| `POST` | `/api/income` | Record freelance/service income |

## Dashboard Sections

1. **Portfolio Overview** — Total value, 24h change, allocation pie chart
2. **Revenue Timeline** — Income over time (line/bar chart)
3. **Holdings Table** — Individual asset performance
4. **Income Sources** — Breakdown by source (crypto, freelance, services)

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `3020` | Server port |
| `DB_PATH` | `./data/revenue.db` | SQLite database path |
| `COINGECKO_API` | Free tier URL | CoinGecko API base URL |

## Edge Cases & Troubleshooting

- **Port in use**: Change port via `PORT=3021 npm start` or kill the existing process.
- **DB locked**: SQLite doesn't support concurrent writes well. Ensure only one instance runs.
- **CoinGecko rate limit**: Free tier ~30 req/min. Dashboard caches prices for 60s.
- **Missing data**: API returns empty arrays (not errors) for date ranges with no entries.
- **First run**: Database and tables are created automatically on first start.

## Security

- Dashboard binds to `localhost` by default. Use a reverse proxy (nginx) for public access.
- No authentication built in — add basic auth or put behind a VPN for production use.
- Never expose the SQLite file publicly.

## Tech Stack

Next.js 14, shadcn/ui, Recharts, SQLite (better-sqlite3)
