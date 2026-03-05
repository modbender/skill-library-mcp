# Trading (Swaps, Strategy, Reports)

## Token Swaps (Uniswap V3)

Best fee tier (0.05%, 0.3%, 1%) found automatically.

### Workflow

1. Check balance: `GET /agents/NAME/wallet/balance`
2. Get quote: `GET /agents/NAME/wallet/swap/quote`
3. Present quote to human with balance info
4. Wait for explicit approval
5. Execute: `POST /agents/NAME/wallet/swap`

### How to Present a Quote

**With balance:**
```
Swap Quote:

• Selling: 0.1 MON (I have 0.39 MON)
• Receiving: ~0.019 USDC (minimum: 0.0189 USDC)
• Price: 1 MON = 0.019 USDC
• Route: WMON -> USDC

Execute this swap?
```

**Without balance:**
```
Swap Quote:

• Selling: 1 USDC (I have 0 USDC)
• Receiving: ~52.6 MON

I can't execute — I have 0 USDC. Send to `0xYourAddress` to proceed.
```

Bullet points (•), blank lines after header and before closing question.

### Get Quote

```bash
GET {BASE_URL}/agents/NAME/wallet/swap/quote?sellToken=MON&buyToken=USDC&sellAmount=100000000000000000&slippage=0.5
```

Params: `sellToken` (symbol or address), `buyToken`, `sellAmount` (smallest units), `slippage` (default 0.5%).

Amount conversion: MON/WETH (18 dec) 0.1 = 1e17. USDC/USDT (6 dec) 1 = 1e6.

### Execute Swap

```bash
curl -X POST {BASE_URL}/agents/NAME/wallet/swap \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "sellToken": "MON", "buyToken": "USDC",
    "sellAmount": "100000000000000000", "slippage": "0.5",
    "reasoning": {
      "strategy": "diversification",
      "summary": "Portfolio 100% MON, adding USDC",
      "confidence": 0.8,
      "marketContext": "MON up 15%"
    }
  }'
```

**Reasoning fields:** `strategy` (diversification/rebalance/take-profit/buy-dip/market-opportunity/hedge/other), `summary` (500 chars), `confidence` (0-1, vary honestly), `marketContext` (300 chars).

### Multiple Swaps: Gas

Reserve gas upfront: `available = balance - (num_swaps × 0.003 MON)`.

### Swap Examples

```json
// 0.1 MON → USDC
{"sellToken": "MON", "buyToken": "USDC", "sellAmount": "100000000000000000", "slippage": "0.5"}

// 1 USDC → MON
{"sellToken": "USDC", "buyToken": "MON", "sellAmount": "1000000", "slippage": "0.5"}
```

---

## Trading Strategy

Trade autonomously within server-enforced limits. No per-trade human approval needed.

### Status & Prices

```bash
GET {BASE_URL}/agents/NAME/trading/status   # Portfolio + limits + recent trades
GET {BASE_URL}/tokens/prices                # All token prices (cached 60s)
```

### Limits

```bash
PUT {BASE_URL}/agents/NAME/trading/config \
  -d '{"enabled": true, "maxPerTradeMON": "0.1", "dailyCapMON": "0.5", "allowedTokens": ["MON","USDC","WETH"]}'
```

Defaults: maxPerTrade 1000 MON (~$20), dailyCap 10000 MON (~$200). Platform max: 50000/250000.

Daily volume resets UTC midnight. Violations return 403.

### Strategy Thinking

- Concentration risk: diversify if too much in one token
- Gas reserves: keep ~0.01 MON minimum
- Daily limits: plan trades within cap
- Start small on speculative moves

### Report Trades

After executing: show trade details, reasoning, daily limit remaining, tx link.

---

## Strategy Performance Reports

After time-boxed sessions: snapshot before → trade → snapshot after → submit report.

```bash
curl -X POST {BASE_URL}/agents/NAME/strategy/report \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "rebalance",
    "summary": "Diversified from 99% MON into WETH and USDC.",
    "timeWindow": {"start": "2026-02-07T08:41:00Z", "end": "2026-02-07T08:51:00Z", "durationMinutes": 10},
    "portfolioBefore": {"totalValueMON": "8.768", "holdings": [{"symbol": "MON", "balance": "8.768", "valueMON": "8.768"}]},
    "portfolioAfter": {"totalValueMON": "8.770", "holdings": [{"symbol": "MON", "balance": "7.768", "valueMON": "7.768"}, {"symbol": "USDC", "balance": "0.010", "valueMON": "0.527"}]},
    "trades": [{"hash": "0x...", "sellSymbol": "MON", "buySymbol": "USDC", "sellAmount": "0.5", "buyAmount": "0.009", "timestamp": "2026-02-07T08:45:00Z"}],
    "confidence": 0.75
  }'
```

Server calculates P&L. Present: "Strategy Complete: Rebalance (10 min) • P&L: +0.002 MON (+0.02%) • Trades: 2"

Retrieve: `GET /agents/NAME/strategy/reports?limit=20`
