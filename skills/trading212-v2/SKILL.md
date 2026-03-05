---
name: trading212
description: Analyzes Trading212 portfolio, generates daily summaries with P&L and top gainers/losers, makes trade proposals based on configurable rules, and can place orders. Also supports dividend overview, order history, watchlist with price alerts, and portfolio allocation analysis with rebalancing proposals. Use when the user asks about portfolio, daily performance, trade actions, or requests a portfolio overview.
metadata: {"openclaw":{"requires":{"bins":["python3"],"env":["TRADING212_API_KEY","TRADING212_API_SECRET"]},"primaryEnv":"TRADING212_API_KEY"}}
---

# Trading212 Skill

Connects to the Trading212 API to provide portfolio analysis, trade proposals, and order execution.

**Important**: By default all operations run against the **demo** (paper-trading) environment. Set `TRADING212_DEMO=false` only when you are absolutely sure the user wants to trade with real money.

## Prerequisites

Install dependencies once from the skill's script directory:

```bash
pip install -r {baseDir}/requirements.txt
```

## Available Modes

### 1. summary -- Daily portfolio overview

```bash
python3 {baseDir}/scripts/trading212_skill.py --mode summary
```

Returns structured JSON with:
- Total portfolio value, cash, daily change (EUR + %)
- Per-position details (quantity, avg price, current price, unrealised P&L)
- Top gainers and top losers
- Notable events (orders filled today, dividends received)
- Multi-period performance (1 week, 1 month, 3 months, 1 year)

Use this when the user asks: "How did my portfolio do today?", "Give me a summary", "What happened in my portfolio?"

Present the JSON output as a readable English summary. Highlight the daily change prominently, list top gainers and losers, and mention notable events.

### 2. propose -- Trade proposals

```bash
python3 {baseDir}/scripts/trading212_skill.py --mode propose
python3 {baseDir}/scripts/trading212_skill.py --mode propose --risk low
python3 {baseDir}/scripts/trading212_skill.py --mode propose --risk high
```

Returns a list of suggested actions (buy, sell, reduce, hold) with quantities and reasons. Rules are configured in `config/rules.yaml`.

Active rules:
- **Reduce on drop**: Propose reducing positions that dropped significantly today with large weight
- **Take profit**: Propose selling small positions with high unrealised gain
- **DCA buy**: Propose buying tickers on the DCA list when enough cash is available
- **Stop-loss**: Propose selling when price drops below stop-loss threshold vs average purchase price
- **Max exposure**: Propose reducing when a single position exceeds maximum portfolio weight
- **Cost averaging**: Propose buying more when price is significantly below average purchase price
- **Cash reserve**: Warn when cash falls below minimum percentage of portfolio

Use this when the user asks: "What should I do?", "Any trade suggestions?", "Should I buy or sell anything?"

Present proposals clearly. Always ask the user for confirmation before executing any proposed trade. Never execute trades automatically.

### 3. execute_trade -- Place an order

```bash
python3 {baseDir}/scripts/trading212_skill.py --mode execute_trade --params '{"symbol":"AAPL_US_EQ","side":"buy","quantity":5,"order_type":"market"}'
```

Parameters (JSON):
- `symbol` (required): Trading212 ticker, e.g. "AAPL_US_EQ"
- `side` (required): "buy" or "sell"
- `quantity` (required): positive number of shares
- `order_type`: "market" (default) or "limit"
- `limit_price`: required when order_type is "limit"

Pre-trade validation is performed automatically:
- Buy orders: checks if enough cash is available
- Sell orders: checks if enough shares are held

**CRITICAL SAFETY RULES**:
1. NEVER execute a trade without explicit user confirmation.
2. Always show the user exactly what will be executed (symbol, side, quantity, order type) and ask "Shall I place this order?" before running.
3. If `TRADING212_DEMO=true` (the default), remind the user this is a paper-trade.
4. If `TRADING212_DEMO=false`, warn the user clearly that this is a REAL order with real money.

### 4. dividends -- Dividend overview

```bash
python3 {baseDir}/scripts/trading212_skill.py --mode dividends
```

Returns structured JSON with:
- Total dividends received (all time and last 12 months)
- Per-ticker breakdown with totals, last payment date, and estimated annual yield
- Dividend calendar (most recent payment per ticker)

Use this when the user asks: "How much dividend did I receive?", "What are my dividends?", "When was my last dividend?"

### 5. history -- Order history

```bash
python3 {baseDir}/scripts/trading212_skill.py --mode history
python3 {baseDir}/scripts/trading212_skill.py --mode history --params '{"ticker":"AAPL_US_EQ","days":30}'
```

Returns structured JSON with:
- Total number of historical orders
- Realized P&L per ticker and overall
- Full order list with dates, prices, and quantities

Optional parameters (JSON):
- `ticker`: Filter by specific ticker
- `days`: Limit to orders from the last N days

Use this when the user asks: "Show my order history", "How much profit did I realize?", "What did I trade last month?"

### 6. watchlist -- Price monitoring

```bash
python3 {baseDir}/scripts/trading212_skill.py --mode watchlist
```

Reads `config/watchlist.yaml` and checks price alerts for each ticker. Returns:
- List of watchlist items with current prices (if held)
- Triggered alerts (price above or below configured thresholds)

Configure the watchlist in `config/watchlist.yaml`:
```yaml
watchlist:
  - ticker: "NVDA_US_EQ"
    alert_below: 100.0
    alert_above: 150.0
```

Use this when the user asks: "Check my watchlist", "Any price alerts?", "What are my watched stocks doing?"

### 7. allocation -- Portfolio allocation analysis

```bash
python3 {baseDir}/scripts/trading212_skill.py --mode allocation
python3 {baseDir}/scripts/trading212_skill.py --mode allocation --rebalance
```

Returns structured JSON with:
- Current weight per position vs target allocation
- Deviation from target per position
- Missing target tickers (in target but not held)
- Cash allocation vs target

With `--rebalance` flag, also generates buy/sell proposals to move toward target allocation.

Configure target allocation in `config/allocation.yaml`:
```yaml
target_allocation:
  "VWCE.UK": 40.0
  "IWDA.UK": 30.0
  _cash: 5.0
```

Use this when the user asks: "How is my portfolio allocated?", "Am I balanced?", "What should I rebalance?"

## Output Format

All modes return structured JSON to stdout. Parse it and present a human-readable English summary to the user.

## Additional Resources

For full output schemas and API details, see [reference.md](reference.md).
