# Financial Setup Guide

## Mercury Banking API

### Getting Your API Key
1. Log into [Mercury Dashboard](https://app.mercury.com)
2. Go to **Settings → API Tokens**
3. Click **Generate New Token**
4. Set permissions to **Read Only** (never use write access for monitoring)
5. Optionally whitelist your server IP for security
6. Copy the token and set as environment variable:
   ```bash
   export MERCURY_API_TOKEN="your-token-here"
   ```

### Mercury Accounts
Agent6ix LLC has 3 Mercury accounts:
- **Checking** — Primary operating account
- **Savings** — Reserve/runway fund
- **GHL Dedicated** — GoHighLevel revenue collection

### API Endpoints Used
| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/accounts` | List all accounts with balances |
| `GET /api/v1/account/{id}/transactions` | Transaction history with filters |

Query parameters for transactions:
- `offset` — Pagination offset
- `limit` — Max results (default 25)
- `start` — Start date (YYYY-MM-DD)
- `end` — End date (YYYY-MM-DD)
- `search` — Text search in descriptions

---

## Stripe API

### Getting Your API Key
1. Log into [Stripe Dashboard](https://dashboard.stripe.com)
2. Go to **Developers → API Keys**
3. Click **Create restricted key**
4. Enable **Read** access only for:
   - Balance
   - Charges
   - Invoices
   - Subscriptions
   - Customers
   - Payouts
5. Copy the restricted key:
   ```bash
   export STRIPE_API_KEY="rk_live_..."
   ```

### API Endpoints Used
| Endpoint | Purpose |
|----------|---------|
| `GET /v1/balance` | Current available and pending balance |
| `GET /v1/charges` | Payment history |
| `GET /v1/invoices` | Invoice list and aging |
| `GET /v1/subscriptions` | Active subscriptions for MRR |
| `GET /v1/customers` | Customer list |
| `GET /v1/payouts` | Bank payouts |

---

## OpenRouter API (AI Categorization)

Used to automatically categorize transactions via LLM:
```bash
export OPENROUTER_API_KEY="sk-or-..."
```

Model used: `openai/gpt-4o-mini` (fast, cheap, accurate for categorization).

---

## Expense Categories

Default categories (customizable in `ai_cfo.py`):

| Category | Description | Examples |
|----------|-------------|----------|
| Revenue | Incoming payments | Stripe payouts, client payments |
| COGS | Cost of goods sold | API costs, hosting for client deliverables |
| Marketing | Advertising & promotion | Google Ads, Meta Ads, sponsorships |
| Software/SaaS | Software subscriptions | AWS, Slack, Notion, GHL |
| Payroll | Salaries & contractors | Employee pay, freelancer invoices |
| Office | Office & operations | Supplies, co-working, utilities |
| Travel | Business travel | Flights, hotels, rideshare |
| Professional Services | Legal, accounting, consulting | Attorney fees, CPA, advisors |
| Tax | Tax payments | Federal, state, payroll taxes |
| Transfer | Inter-account transfers | Checking ↔ Savings (excluded from P&L) |
| Other | Uncategorized | Anything else |

### Customizing Categories
Edit the `EXPENSE_CATEGORIES` list in `ai_cfo.py` to add/remove categories. The AI categorizer adapts automatically.

---

## How the P&L is Calculated

```
Revenue (Stripe charges + Mercury inflows tagged as Revenue)
- Cost of Goods Sold
= Gross Profit
- Marketing
- Software/SaaS
- Payroll
- Office
- Travel
- Professional Services
- Tax
- Other
= Net Income
```

- **Revenue source**: Primarily Stripe succeeded charges; Mercury inflows categorized as Revenue
- **Expenses**: All Mercury outflows, AI-categorized
- **Transfers excluded**: Inter-account transfers don't appear in P&L
- **Period**: Any date range via `--start` and `--end` flags

---

## Cash Flow Forecasting

The forecast uses **linear regression** on weekly net cash flows:

1. Aggregates 90 days of transactions into weekly buckets
2. Calculates net flow (inflows - outflows) per week
3. Fits a linear trend line: `y = slope × week + intercept`
4. Projects forward 30/60/90 days
5. Combines with current cash position for projected balances

**Limitations**: Assumes linear trend continues. Works best for stable businesses. Seasonal patterns may reduce accuracy.

---

## Cron Setup

### Daily Brief (8 AM)
```bash
# In OpenClaw cron jobs or system crontab
0 8 * * * cd /path/to/skills/ai-cfo && python3 scripts/cfo_cron.py
```

### Weekly Report (Monday 9 AM)
```bash
0 9 * * 1 cd /path/to/skills/ai-cfo && python3 scripts/ai_cfo.py report --period weekly
```

### Monthly P&L (1st of month)
```bash
0 9 1 * * cd /path/to/skills/ai-cfo && python3 scripts/ai_cfo.py pnl --start $(date -d "last month" +%Y-%m-01) --end $(date -d "last month" +%Y-%m-%d)
```

---

## Data Storage

All data persists in SQLite at `.data/sqlite/cfo.db`:

| Table | Purpose |
|-------|---------|
| `transactions` | Categorized transaction history |
| `budgets` | Budget limits by category |
| `snapshots` | Daily financial snapshots |
| `pnl_monthly` | Monthly P&L summaries |

The database is created automatically on first run.

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need an AI CFO for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
