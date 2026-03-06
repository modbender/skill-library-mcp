# Safety Architecture

## Defense Layers

1. **API Key Isolation** — Trade-only permissions, no withdrawals, IP whitelisted
2. **Guardrails** — Hard caps on order size, daily volume, price deviation
3. **Dry-Run Default** — All trades simulate unless `--live` is explicitly passed
4. **Kill Switch** — Instantly halt all trading and cancel open orders
5. **Audit Trail** — Every action logged to `~/.config/bitstamp-trader/audit.jsonl`

## Safety Config (defaults)

| Setting | Default | Purpose |
|---|---|---|
| `max_order_size_usd` | $100 | Hard cap per single order |
| `max_daily_volume_usd` | $500 | Daily trading limit |
| `price_deviation_pct` | 3% | Reject limit orders >3% from market |
| `large_trade_threshold_usd` | $50 | Requires CONFIRM prompt above this |
| `default_market` | BTC/USD | Default trading pair |
| `allowed_markets` | BTC/USD, ETH/USD, BTC/EUR, ETH/EUR | Whitelisted pairs |

### Adjusting Limits

```bash
bitstamp config --set max_order_size_usd=500
bitstamp config --set max_daily_volume_usd=2000
bitstamp config --set allowed_markets=BTC/USD,ETH/USD,SOL/USD
```

## Kill Switch

Activate (cancels all open orders + blocks new ones):
```bash
bitstamp kill-switch --reason "market crash"
```

Check status:
```bash
bitstamp kill-switch --status
```

Resume trading:
```bash
bitstamp kill-switch --deactivate
```

The kill switch creates a lock file at `~/.config/bitstamp-trader/KILL_SWITCH`.
All trade commands check for this file before executing.

## Audit Log

Structured JSONL at `~/.config/bitstamp-trader/audit.jsonl`.

Categories: ORDER, GUARDRAIL, ACCOUNT, CONFIG, KILL_SWITCH, AUTH

View recent:
```bash
bitstamp audit --limit 50
```

## Pre-Trade Check Sequence

Every buy/sell command runs these checks IN ORDER:
1. ✅ Kill switch inactive?
2. ✅ Market in allowed list?
3. ✅ Fetch current market price
4. ✅ Estimate USD value
5. ✅ Under max order size?
6. ✅ Under daily volume limit?
7. ✅ Price within deviation threshold? (limit orders)
8. ✅ Confirmation prompt if large trade + live mode
9. ➡️ Execute or simulate

Any failure = order rejected with audit log entry.
