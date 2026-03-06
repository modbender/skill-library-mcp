# Trading212 Skill -- Reference

## Output Schemas

### summary mode

```json
{
  "mode": "summary",
  "date": "2026-02-15",
  "environment": "demo",
  "portfolio": {
    "total_value": 12500.00,
    "cash": 450.00,
    "invested": 12050.00,
    "daily_change_eur": 154.33,
    "daily_change_pct": 1.25
  },
  "performance": {
    "1w": {"change_eur": 50.0, "change_pct": 0.4},
    "1m": {"change_eur": 200.0, "change_pct": 1.6},
    "3m": {"change_eur": -100.0, "change_pct": -0.8},
    "1y": null
  },
  "positions": [
    {
      "ticker": "AAPL_US_EQ",
      "name": "Apple Inc",
      "isin": "US0378331005",
      "currency": "USD",
      "quantity": 10,
      "avg_price": 150.00,
      "current_price": 155.00,
      "value": 1550.00,
      "total_cost": 1500.00,
      "unrealized_pnl": 50.00,
      "fx_impact": -2.30,
      "wallet_currency": "EUR",
      "daily_change_eur": 20.00,
      "daily_change_pct": 1.31
    }
  ],
  "top_gainers": [
    {
      "ticker": "AAPL_US_EQ",
      "name": "Apple Inc",
      "daily_pct": 2.5,
      "contribution_eur": 50.00
    }
  ],
  "top_losers": [
    {
      "ticker": "TSLA_US_EQ",
      "name": "Tesla Inc",
      "daily_pct": -1.8,
      "contribution_eur": -30.00
    }
  ],
  "notable_events": [
    {
      "type": "buy",
      "ticker": "AAPL_US_EQ",
      "desc": "Koop 5x Apple Inc"
    },
    {
      "type": "dividend",
      "ticker": "MSFT_US_EQ",
      "desc": "Dividend 1.25 EUR voor Microsoft Corp"
    }
  ]
}
```

Notes:
- `daily_change_eur` and `daily_change_pct` are `null` when no previous snapshot exists.
- `top_gainers` / `top_losers` lists max 5 entries each.
- `performance` keys are `null` when no snapshot exists for that period.
- A snapshot is saved automatically on each summary run to `snapshots/YYYY-MM-DD.json`.

### propose mode

```json
{
  "mode": "propose",
  "date": "2026-02-15",
  "environment": "demo",
  "portfolio_value": 12500.00,
  "cash": 450.00,
  "proposals": [
    {
      "symbol": "AAPL_US_EQ",
      "action": "reduce",
      "quantity": 5,
      "reason": "Position dropped 3.2% today and represents 8.0% of portfolio..."
    },
    {
      "symbol": "TSLA_US_EQ",
      "action": "sell",
      "quantity": 10,
      "reason": "Stop-loss: current price (180.00) is 12.0% below average purchase price (204.55)..."
    },
    {
      "symbol": "VWCE.UK",
      "action": "buy",
      "quantity": 2,
      "reason": "DCA buy: VWCE.UK is on your DCA list..."
    },
    {
      "symbol": "MSFT_US_EQ",
      "action": "reduce",
      "quantity": 3,
      "reason": "Max exposure: MSFT_US_EQ represents 22.5% of portfolio (max allowed: 20%)..."
    },
    {
      "symbol": "IWDA.UK",
      "action": "buy",
      "quantity": 1,
      "reason": "Cost averaging: IWDA.UK current price (70.00) is 11.2% below average (78.85)..."
    },
    {
      "symbol": "",
      "action": "hold",
      "quantity": 0,
      "reason": "Cash reserve warning: cash is 2.5% of portfolio (minimum: 5%)..."
    }
  ]
}
```

Possible `action` values: `buy`, `sell`, `reduce`, `increase`, `hold`.

### execute_trade mode

Success:
```json
{
  "mode": "execute_trade",
  "environment": "demo",
  "order_id": 12345,
  "status": "FILLED",
  "side": "BUY",
  "ticker": "AAPL_US_EQ",
  "quantity": 5,
  "order_type": "MARKET",
  "error": null
}
```

Failure:
```json
{
  "mode": "execute_trade",
  "environment": "demo",
  "order_id": null,
  "status": "REJECTED",
  "error": "Insufficient funds"
}
```

Validation error (pre-trade check):
```json
{
  "status": "error",
  "code": "validation_error",
  "message": "Onvoldoende cash voor koop. Geschatte kosten: 775.00, beschikbaar: 450.00."
}
```

Possible `status` values (from Trading212):
`LOCAL`, `UNCONFIRMED`, `CONFIRMED`, `NEW`, `CANCELLING`, `CANCELLED`,
`PARTIALLY_FILLED`, `FILLED`, `REJECTED`, `REPLACING`, `REPLACED`.

### dividends mode

```json
{
  "mode": "dividends",
  "date": "2026-02-15",
  "environment": "demo",
  "total_dividends_received": 245.50,
  "last_12_months": 180.00,
  "per_ticker": [
    {
      "ticker": "AAPL_US_EQ",
      "total": 45.00,
      "last_12m": 32.00,
      "last_paid": "2026-01-15",
      "estimated_annual": 40.00
    }
  ],
  "calendar": [
    {
      "ticker": "AAPL_US_EQ",
      "last_paid": "2026-01-15",
      "amount": 8.50
    }
  ]
}
```

### history mode

```json
{
  "mode": "history",
  "date": "2026-02-15",
  "environment": "demo",
  "period_days": 30,
  "total_orders": 15,
  "realized_pnl": 320.50,
  "per_ticker": [
    {
      "ticker": "AAPL_US_EQ",
      "buys": 3,
      "sells": 1,
      "realized_pnl": 120.00
    }
  ],
  "orders": [
    {
      "ticker": "AAPL_US_EQ",
      "side": "buy",
      "quantity": 5,
      "price": 150.00,
      "status": "FILLED",
      "date": "2026-02-10T14:30:00Z"
    }
  ]
}
```

### watchlist mode

```json
{
  "mode": "watchlist",
  "date": "2026-02-15",
  "environment": "demo",
  "items": [
    {
      "ticker": "NVDA_US_EQ",
      "held": true,
      "current_price": 95.00,
      "alert_below": 100.0,
      "alert_above": 150.0,
      "triggered_alerts": [
        {
          "ticker": "NVDA_US_EQ",
          "type": "below",
          "threshold": 100.0,
          "current_price": 95.00,
          "message": "NVDA_US_EQ prijs (95.00) is onder de drempel (100.00)."
        }
      ]
    }
  ],
  "triggered_alerts": [
    {
      "ticker": "NVDA_US_EQ",
      "type": "below",
      "threshold": 100.0,
      "current_price": 95.00,
      "message": "NVDA_US_EQ prijs (95.00) is onder de drempel (100.00)."
    }
  ]
}
```

### allocation mode

```json
{
  "mode": "allocation",
  "date": "2026-02-15",
  "environment": "demo",
  "portfolio_value": 12500.00,
  "cash": {
    "value": 450.00,
    "current_weight_pct": 3.60,
    "target_weight_pct": 5.0,
    "deviation_pct": -1.40
  },
  "positions": [
    {
      "ticker": "VWCE.UK",
      "name": "Vanguard FTSE All-World",
      "value": 5000.00,
      "current_weight_pct": 40.00,
      "target_weight_pct": 40.0,
      "deviation_pct": 0.00
    },
    {
      "ticker": "AAPL_US_EQ",
      "name": "Apple Inc",
      "value": 1550.00,
      "current_weight_pct": 12.40,
      "target_weight_pct": 10.0,
      "deviation_pct": 2.40
    }
  ],
  "missing_targets": [
    {
      "ticker": "IWDA.UK",
      "target_weight_pct": 30.0,
      "current_weight_pct": 0.0,
      "deviation_pct": -30.0
    }
  ],
  "rebalance_proposals": [
    {
      "symbol": "AAPL_US_EQ",
      "action": "sell",
      "quantity": 2,
      "reason": "Rebalance: AAPL_US_EQ is 2.4% boven target (10.0%). Verkoop 2 aandelen om dichter bij doelallocatie te komen."
    },
    {
      "symbol": "IWDA.UK",
      "action": "buy",
      "quantity": null,
      "reason": "Rebalance: IWDA.UK is niet in portfolio maar heeft target allocatie van 30.0%. Overweeg ~3750.00 te investeren."
    }
  ]
}
```

Note: `rebalance_proposals` only appears when `--rebalance` flag is used.

## Configuration

### Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `TRADING212_API_KEY` | Yes | -- | API key from Trading212 app |
| `TRADING212_API_SECRET` | Yes | -- | API secret from Trading212 app |
| `TRADING212_DEMO` | No | `true` | `true` = demo/paper environment, `false` = live |
| `TRADING212_SNAPSHOT_DIR` | No | `<project>/snapshots/` | Custom snapshot directory |
| `TRADING212_RULES_PATH` | No | `<project>/config/rules.yaml` | Custom rules file |

### Rules (config/rules.yaml)

```yaml
proposal_rules:
  # Reduce on drop
  drop_threshold_pct: 3.0       # daily drop % to trigger reduce proposal
  min_weight_pct: 5.0           # min portfolio weight to trigger reduce

  # Take profit
  small_position_pct: 2.0       # positions below this % are "small"
  min_gain_pct: 5.0             # unrealised gain % to trigger take-profit

  # DCA (Dollar-Cost Averaging)
  dca_min_cash: 100.0           # minimum cash for DCA proposals
  dca_amount: 50.0              # amount to buy per DCA ticker
  dca_tickers:                  # tickers for DCA strategy
    - "VWCE.UK"
    - "IWDA.UK"

  # Risk mode
  risk_mode: medium             # low / medium / high

  # Stop-loss
  stop_loss_pct: 10.0           # sell when price drops this % below avg purchase price

  # Max exposure
  max_exposure_pct: 20.0        # max portfolio weight for a single position
  max_exposure_target_pct: 15.0 # target weight after reduction

  # Cost averaging
  cost_avg_threshold_pct: 10.0  # buy more when price drops this % below avg
  cost_avg_amount: 50.0         # amount to buy
  cost_avg_tickers:             # tickers eligible for cost averaging
    - "VWCE.UK"
    - "IWDA.UK"

  # Cash reserve
  cash_reserve_pct: 5.0         # warn when cash falls below this % of portfolio
```

Risk multipliers control max position fraction per trade:
- `low`: 25%
- `medium`: 50%
- `high`: 100%

### Watchlist (config/watchlist.yaml)

```yaml
watchlist:
  - ticker: "NVDA_US_EQ"
    alert_below: 100.0
    alert_above: 150.0
  - ticker: "TSLA_US_EQ"
    alert_below: 200.0
```

### Target Allocation (config/allocation.yaml)

```yaml
target_allocation:
  "VWCE.UK": 40.0
  "IWDA.UK": 30.0
  "AAPL_US_EQ": 10.0
  _cash: 5.0
```

Special key `_cash` sets the target cash percentage. Percentages do not need to sum to 100.

## Trading212 API Details

Base URLs:
- Demo: `https://demo.trading212.com/api/v0`
- Live: `https://live.trading212.com/api/v0`

Authentication: HTTP Basic (API_KEY:API_SECRET, Base64-encoded).

Rate limits enforced by the client:
- Positions: 1 req/s
- Pending orders: 1 req/5s
- Market orders: 50 req/min
- Limit orders: 1 req/2s
- Historical orders / dividends / transactions: 6 req/min

Sell orders require **negative** quantity (handled automatically by the skill).

### Retry logic

The client retries up to 3 times with exponential backoff for:
- HTTP 429 (rate limited) -- respects `Retry-After` header
- HTTP 5xx (server errors)
- Connection errors and timeouts

### Caching

Positions and cash balance are cached in-memory for 60 seconds. The cache is automatically invalidated when placing or cancelling orders.

## Extending with new rules

1. Open `scripts/proposal_rules.py`.
2. Write a new function with signature:
   ```python
   def rule_my_new_rule(pos, ctx, cfg) -> Optional[Dict]:
   ```
   Available context keys in `ctx`:
   - `total_value`: total portfolio value
   - `cash`: available cash
   - `risk_mode`: "low" / "medium" / "high"
   - `risk_multiplier`: 0.25 / 0.50 / 1.00
   - `positions`: full list of position dicts
3. Append it to the `RULES` list.
4. Add any new parameters to `config/rules.yaml`.
