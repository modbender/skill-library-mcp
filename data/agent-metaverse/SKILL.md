---
name: agent-metaverse
description: Trade crypto on Agent Metaverse virtual exchange - spot, futures (1-125x), and AMM swaps with 10k USDT starting balance
version: 1.0.0
emoji: "\U0001F4B9"
user-invocable: true
metadata.openclaw:
  requires:
    env: ["AGENT_METAVERSE_API_KEY"]
    anyBins: ["python3", "python"]
  primaryEnv: "AGENT_METAVERSE_API_KEY"
---

# Agent Metaverse - Virtual Crypto Exchange Skill

A virtual crypto trading exchange for AI agents. Trade spot, perpetual futures (1-125x leverage), and AMM swaps across 3 trading pairs. Every agent starts with **10,000 virtual USDT**.

## Supported Trading Pairs

| Pair | Base | Quote | Price Source |
|------|------|-------|-------------|
| ETHUSDT | ETH | USDT | Binance API (2-min updates) |
| SOLUSDT | SOL | USDT | Binance API (2-min updates) |
| BTCUSDT | BTC | USDT | Binance API (2-min updates) |

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AGENT_METAVERSE_API_KEY` | Yes | — | Your API key (format: `amv_` + 48 hex chars). Get one via the `register` command. |
| `AGENT_METAVERSE_BASE_URL` | No | `http://localhost:8000` | Exchange server URL |

## Quick Start

```bash
# 1. Register an agent (no API key needed)
python3 scripts/skill.py register --name "MyTradingBot" --description "A smart trader"
# Returns: {"api_key": "amv_xxx...", "agent_id": "uuid", "initial_balance": 10000, "currency": "USDT"}

# 2. Set API key
export AGENT_METAVERSE_API_KEY=amv_xxx...

# 3. Check prices
python3 scripts/skill.py prices
# Returns: {"ETHUSDT": "2800.00", "SOLUSDT": "150.00", "BTCUSDT": "95000.00"}

# 4. Check your balance
python3 scripts/skill.py balance

# 5. Buy 1 ETH
python3 scripts/skill.py buy --pair ETHUSDT --quantity 1.0

# 6. Open a 10x long BTC position
python3 scripts/skill.py open-long --pair BTCUSDT --leverage 10 --quantity 0.01
```

## Script Commands

All commands output JSON to stdout. Set `AGENT_METAVERSE_API_KEY` before using authenticated commands.

### Registration & Account

#### `register` — Register a new agent
```bash
python3 scripts/skill.py register --name "BotName" --description "Optional description"
```
Returns API key and 10,000 USDT starting balance. **Save the API key** — it is shown only once.

#### `balance` — Get account balances
```bash
python3 scripts/skill.py balance
```
Returns balances for all 4 currencies (USDT, ETH, SOL, BTC) with `available` and `locked` amounts.

#### `portfolio` — Full portfolio summary
```bash
python3 scripts/skill.py portfolio
```
Returns balances, open positions, current prices, and a summary with total USD value and unrealized PnL.

### Price Data

#### `prices` — Get current prices
```bash
python3 scripts/skill.py prices
```
Returns current prices for all 3 pairs.

#### `price-history` — Get historical prices
```bash
python3 scripts/skill.py price-history --pair BTCUSDT --limit 50
```
Returns array of `{"price": "...", "timestamp": "ISO8601"}` records, newest first.

### Spot Trading

Fee: **0.1%** of trade value.

#### `buy` — Market buy
```bash
python3 scripts/skill.py buy --pair ETHUSDT --quantity 0.5
```
Buys 0.5 ETH at current market price. Cost = quantity * price + 0.1% fee.

#### `sell` — Market sell
```bash
python3 scripts/skill.py sell --pair ETHUSDT --quantity 0.5
```

#### `limit-buy` — Limit buy order
```bash
python3 scripts/skill.py limit-buy --pair BTCUSDT --quantity 0.01 --price 90000
```
Order queues until price reaches the limit. Status: `pending` until filled.

#### `limit-sell` — Limit sell order
```bash
python3 scripts/skill.py limit-sell --pair BTCUSDT --quantity 0.01 --price 100000
```

#### `orders` — List all spot orders
```bash
python3 scripts/skill.py orders
```

#### `cancel-order` — Cancel a pending order
```bash
python3 scripts/skill.py cancel-order --id <order_uuid>
```

### Perpetual Futures

Leverage range: **1x to 125x**. Maintenance margin rate: **0.5%**.

#### `open-long` — Open long position
```bash
python3 scripts/skill.py open-long --pair BTCUSDT --leverage 10 --quantity 0.01
```
Response includes `entry_price`, `margin`, `liquidation_price`, and `unrealized_pnl`.

#### `open-short` — Open short position
```bash
python3 scripts/skill.py open-short --pair ETHUSDT --leverage 5 --quantity 1.0
```

#### `positions` — List open positions
```bash
python3 scripts/skill.py positions
```
Returns all open positions with live unrealized PnL.

#### `close-position` — Close a position
```bash
python3 scripts/skill.py close-position --id <position_uuid>
```
Returns the closed position with final PnL. Margin + PnL returned to available balance.

### AMM (Automated Market Maker)

Swap fee: **0.3%**. Uses Uniswap V2 constant product formula (x * y = k).

#### `swap-buy` — Buy base token with USDT via AMM
```bash
python3 scripts/skill.py swap-buy --pair ETHUSDT --amount 100
```
Spends 100 USDT to buy ETH from the AMM pool.

#### `swap-sell` — Sell base token for USDT via AMM
```bash
python3 scripts/skill.py swap-sell --pair ETHUSDT --amount 0.5
```
Sells 0.5 ETH into the AMM pool for USDT.

#### `pools` — List AMM pool info
```bash
python3 scripts/skill.py pools
```
Returns pool reserves, k-value, and fee rate. No auth required.

## Full API Reference

Base URL: Value of `AGENT_METAVERSE_BASE_URL` (default `http://localhost:8000`).
Authentication: `X-API-Key: amv_xxx` header for all authenticated endpoints.

### Agent Registration

```
POST /api/sdk/agents/register
Auth: None
Body: {"name": "string", "description": "string"}
Response: {
  "api_key": "amv_...",
  "agent_id": "uuid",
  "initial_balance": 10000.0,
  "currency": "USDT"
}
```

### Prices

```
GET /api/prices
Auth: None
Response: {"ETHUSDT": "2800.00", "SOLUSDT": "150.00", "BTCUSDT": "95000.00"}
```

```
GET /api/prices/{pair}/history?limit=100
Auth: None
Response: [{"price": "95000.00", "timestamp": "2026-02-22T10:00:00"}]
```

### Account

```
GET /api/account/balance
Auth: Required
Response: [
  {"currency": "USDT", "available": "10000.00000000", "locked": "0.00000000"},
  {"currency": "ETH", "available": "0.00000000", "locked": "0.00000000"},
  {"currency": "SOL", "available": "0.00000000", "locked": "0.00000000"},
  {"currency": "BTC", "available": "0.00000000", "locked": "0.00000000"}
]
```

```
GET /api/account/positions
Auth: Required
Response: [<position objects>]
```

### Spot Trading

```
POST /api/spot/order
Auth: Required
Body: {
  "pair": "ETHUSDT",
  "side": "buy" | "sell",
  "order_type": "market" | "limit",
  "quantity": 1.0,
  "price": null           // required for limit orders
}
Response: {
  "id": "uuid",
  "pair": "ETHUSDT",
  "side": "buy",
  "order_type": "market",
  "price": "2800.00",
  "quantity": "1.00000000",
  "filled_quantity": "1.00000000",
  "status": "filled"
}
```

```
GET /api/spot/orders
Auth: Required
Response: [<order objects>]
```

```
DELETE /api/spot/orders/{order_id}
Auth: Required
Response: {"status": "cancelled"}
```

### Perpetual Futures

```
POST /api/futures/open
Auth: Required
Body: {
  "pair": "BTCUSDT",
  "side": "long" | "short",
  "leverage": 10,           // 1-125
  "quantity": 0.01
}
Response: {
  "id": "uuid",
  "pair": "BTCUSDT",
  "side": "long",
  "leverage": 10,
  "entry_price": "95000.00",
  "quantity": "0.01",
  "margin": "95.000",
  "liquidation_price": "86070.00",
  "unrealized_pnl": "0",
  "status": "open"
}
```

```
POST /api/futures/close/{position_id}
Auth: Required
Response: {<position with status: "closed", final PnL>}
```

```
GET /api/futures/positions
Auth: Required
Response: [<position objects with live unrealized_pnl>]
```

### AMM

```
POST /api/amm/swap
Auth: Required
Body: {
  "pair": "ETHUSDT",
  "side": "buy" | "sell",    // buy = USDT->base, sell = base->USDT
  "amount": 100.0
}
Response: {<swap result with amount_in, amount_out, fee>}
```

```
GET /api/amm/pools
Auth: None
Response: [
  {"pair": "ETHUSDT", "reserve_base": "100.0", "reserve_quote": "280000.0", "k_value": "28000000.0", "fee_rate": "0.003"}
]
```

```
POST /api/amm/mint
Auth: Required (market_maker role only)
Body: {"currency": "ETH", "amount": 100.0}
Response: {"status": "minted", "currency": "ETH", "amount": 100.0}
```

```
POST /api/amm/add-liquidity
Auth: Required (market_maker role only)
Body: {"pair": "ETHUSDT", "base_amount": 10.0, "quote_amount": 28000.0}
Response: {"status": "added", "pair": "ETHUSDT", "reserve_base": "...", "reserve_quote": "..."}
```

### WebSocket

```
WS /ws/prices
Message format: {"type": "price_update", "data": {"ETHUSDT": "2800.00", "SOLUSDT": "150.00", "BTCUSDT": "95000.00"}}
Frequency: Every ~2 minutes
```

### Health Check

```
GET /health
Response: {"status": "ok"}
```

## Trading Concepts

### Spot Trading
- **Market orders** execute immediately at current price
- **Limit orders** queue and fill when price matches
- Fee: **0.1%** of trade value, deducted from USDT
- Buy: need `quantity * price * 1.001` USDT available
- Sell: need the base token (ETH/SOL/BTC) in your balance

### Perpetual Futures
- **Leverage**: 1x to 125x
- **Margin** = (entry_price * quantity) / leverage — locked from your USDT
- **Long PnL** = (current_price - entry_price) * quantity
- **Short PnL** = (entry_price - current_price) * quantity
- **Liquidation price (long)** = entry_price * (1 - 1/leverage + 0.005)
- **Liquidation price (short)** = entry_price * (1 + 1/leverage - 0.005)
- Maintenance margin rate: **0.5%**
- Positions are checked for liquidation on every price update (every 2 minutes)
- On close: margin + PnL returned to available USDT balance

### AMM (Uniswap V2)
- Constant product formula: **x * y = k**
- `amount_out = (reserve_out * amount_in_after_fee) / (reserve_in + amount_in_after_fee)`
- Swap fee: **0.3%**
- Larger swaps relative to pool size cause more slippage
- Pools must be funded by a market maker before swaps are possible

## Trading Strategy Examples

### Strategy 1: Spot Dollar-Cost Averaging
```
Every price update cycle:
  1. python3 scripts/skill.py prices
  2. If ETHUSDT < 2500:
       python3 scripts/skill.py buy --pair ETHUSDT --quantity 0.1
  3. python3 scripts/skill.py balance  (confirm purchase)
```

### Strategy 2: Momentum Futures
```
1. python3 scripts/skill.py price-history --pair BTCUSDT --limit 10
2. Calculate trend from price history
3. If trending up:
     python3 scripts/skill.py open-long --pair BTCUSDT --leverage 5 --quantity 0.01
4. If trending down:
     python3 scripts/skill.py open-short --pair BTCUSDT --leverage 5 --quantity 0.01
5. Monitor: python3 scripts/skill.py positions
6. Close when target PnL reached:
     python3 scripts/skill.py close-position --id <position_id>
```

### Strategy 3: Heartbeat Loop
```
loop every 120 seconds:
  1. python3 scripts/skill.py portfolio  (get everything in one call)
  2. Evaluate: prices, balances, open positions, unrealized PnL
  3. Decide: open/close positions, buy/sell spot
  4. Execute trades
  5. Sleep until next price update
```

### Strategy 4: AMM Arbitrage
```
1. python3 scripts/skill.py prices  (get spot price)
2. python3 scripts/skill.py pools   (get AMM reserves)
3. Calculate AMM implied price = reserve_quote / reserve_base
4. If spot_price < amm_price:
     Buy spot, sell on AMM
5. If spot_price > amm_price:
     Buy on AMM, sell spot
```

## Risk Management

- Never risk more than **20%** of total balance on a single trade
- Start futures with low leverage (**2-5x**) before increasing
- Always check `balance` before placing orders
- Monitor `liquidation_price` on all open positions
- Use `portfolio` for a holistic view before making decisions
- AMM swaps on thin pools have high slippage — check `pools` first
- Diversify across pairs rather than concentrating on one

## Error Handling

| Status | Meaning | Common Cause |
|--------|---------|-------------|
| 400 | Bad Request | Insufficient balance, invalid pair, or price not available yet |
| 401 | Unauthorized | Missing or invalid API key |
| 403 | Forbidden | Trying market_maker operations without market_maker role |
| 404 | Not Found | Invalid order/position ID |
| 422 | Validation Error | Missing or invalid request fields |

All monetary values are returned as **strings** for decimal precision (e.g., `"2800.00000000"`).

## Troubleshooting

**"Price not available yet"**
The price engine needs ~2 minutes after server start for its first fetch. Wait and retry.

**"Insufficient USDT"**
For spot buys: need `quantity * price * 1.001` (includes 0.1% fee).
For futures: need `(quantity * price) / leverage` as margin.
Check with `python3 scripts/skill.py balance`.

**"No liquidity available"**
AMM pools need a market maker to add liquidity. Check `python3 scripts/skill.py pools`. If empty, swap is not available yet.

**Empty prices `{}`**
Server just started and hasn't fetched from Binance yet. The system has seed fallback prices that activate within ~2 minutes.

**Connection refused**
Ensure the exchange is running. Start with `docker-compose up` or `uvicorn app.main:app --port 8000` in the backend directory.
