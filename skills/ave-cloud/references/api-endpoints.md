# AVE Cloud API Reference

Official docs: https://ave-cloud.gitbook.io/data-api

## Authentication

Header: `X-API-KEY: <your_api_key>`

Environment variables:
- `AVE_API_KEY` — your API key
- `API_PLAN` — your plan tier: `free`, `normal`, or `pro`

Rate limits by plan:

| Plan | RPS | Min interval |
|------|-----|-------------|
| free | 1 | 1.0s |
| normal | 5 | 0.2s |
| pro | 20 | 0.05s |

All errors return standard HTTP codes: 401 (invalid key), 403 (rate limit), 400 (bad params), 404 (not found).

## Base URLs

- **v2**: `https://data.ave-api.xyz/v2`
- **WebSocket**: `wss://wss.ave-api.xyz`

## Endpoints

### Search Tokens
```
GET /v2/tokens?keyword={keyword}
```
Params: `keyword` (required), `chain`, `limit` (default 100, max 300), `orderby` (tx_volume_u_24h|main_pair_tvl|fdv|market_cap)

### Platform Tokens
```
GET /v2/tokens/platform?tag={tag}&limit={limit}&orderby={orderby}
```
Returns tokens for a specific launchpad/platform tag. See `VALID_PLATFORMS` in `scripts/ave_client.py` for the full list of ~90 allowed values.

Params: `tag` (required), `limit` (default 100, max 300), `orderby` (`tx_volume_u_24h` default | `main_pair_tvl`)

Common tags: `hot`, `new`, `meme`, `pump_in_hot`, `pump_in_new`, `fourmeme_in_hot`, `bonk_in_hot`, `nadfun_in_hot`

### Batch Token Prices
```
POST /v2/tokens/price
Body: { "token_ids": ["address-chain", ...], "tvl_min": 0, "tx_24h_volume_min": 0 }
```
Max 200 tokens per request.

### Rank Topics
```
GET /v2/ranks/topics
```
Returns list of available topic strings.

Common topics: `hot`, `meme`, `gainer`, `loser`, `new`, `ai`, `depin`, `gamefi`, `rwa`, `l2`,
`eth`, `bsc`, `solana`, `base`, `arbitrum`, `optimism`, `avalanche`, `polygon`, `blast`, `merlin`

### Ranked Token List
```
GET /v2/ranks?topic={topic}
```

### Token Detail
```
GET /v2/tokens/{token_address}-{chain}
```
Returns: price (USD/ETH), market cap, FDV, TVL, volume 24h, tx count, supply, holder count,
price changes (5m/1h/4h/24h), lock/burn amounts, DEX pairs, creator, honeypot, tax, risk level.

### Kline by Pair
```
GET /v2/klines/pair/{pair_address}-{chain}?interval={minutes}&size={count}
```

### Kline by Token
```
GET /v2/klines/token/{token_address}-{chain}?interval={minutes}&size={count}
```
Valid intervals (minutes): `1, 5, 15, 30, 60, 120, 240, 1440, 4320, 10080, 43200, 525600, 2628000`
Default: interval=60, size=600, max size=1000

Kline category param (optional): `u` = USDT price, `r` = relative, `m` = main token price

### Top 100 Holders
```
GET /v2/tokens/top100/{token_address}-{chain}
```
Returns: holder address, balance, percentage, buy/sell history per holder.

### Swap Transactions
```
GET /v2/txs/{pair_address}-{chain}
```
Returns: time, tx_hash, type (buy/sell), sender, token amounts, price, AMM name.

### Supported Chains
```
GET /v2/supported_chains
```

### Chain Main Tokens
```
GET /v2/tokens/main?chain={chain_name}
```

### Chain Trending List
```
GET /v2/tokens/trending?chain={chain}&current_page={page}&page_size={size}
```
Default page_size=50. Response includes `next_page` cursor.

### Contract Risk Detection
```
GET /v2/contracts/{token_address}-{chain}
```
Returns: risk_level (LOW/MEDIUM/HIGH/CRITICAL), risk_score, honeypot flag, buy_tax, sell_tax,
owner address, ownership renounced, mint/burn functions, top holder concentration, DEX liquidity.

## Common Chain Identifiers

| Chain | ID |
|-------|----|
| Ethereum | `eth` |
| BNB Chain | `bsc` |
| Solana | `solana` |
| Base | `base` |
| Arbitrum | `arbitrum` |
| Optimism | `optimism` |
| Avalanche | `avax` |
| Polygon | `polygon` |
| TON | `ton` |

Full list: `python scripts/ave_client.py chains`

## Response Envelope (v2)

```json
{
  "status": 1,
  "msg": "SUCCESS",
  "data_type": 1,
  "data": { ... }
}
```

## WebSocket API

**Endpoint:** `wss://wss.ave-api.xyz`
**Auth header:** `X-API-KEY: <your_api_key>`
**Required plan:** `pro`

All messages use JSON-RPC 2.0 framing:
```json
{ "jsonrpc": "2.0", "method": "<method>", "params": [...], "id": 1 }
```

### Interactive REPL (`wss-repl`)

The `wss-repl` command maintains a persistent connection and accepts commands from stdin.
UI output goes to stderr; JSON event stream goes to stdout (clean for piping to `jq`).

```
> subscribe price <addr-chain> [<addr-chain> ...]
> subscribe tx|multi_tx|liq <pair_address> <chain>
> subscribe kline <pair_address> <chain> [interval]
> unsubscribe
> quit
```

### Heartbeat / Ping-Pong

The server sends periodic pings; the client library handles pong replies automatically.
The CLI uses `ping_interval=30, ping_timeout=10`.

To send a manual ping:
```json
{ "jsonrpc": "2.0", "method": "ping", "params": [], "id": 1 }
```

Server responds:
```json
{ "jsonrpc": "2.0", "result": "pong", "id": 1 }
```

### Subscribe: Live Transactions (`tx` / `multi_tx` / `liq`)

Subscribe message:
```json
{
  "jsonrpc": "2.0",
  "method": "subscribe",
  "params": ["<topic>", "<pair_address>", "<chain>"],
  "id": 1
}
```

| Field | Values |
|-------|--------|
| topic | `tx` (single swap), `multi_tx` (batch), `liq` (liquidity event) |
| pair_address | Trading pair contract address |
| chain | Chain identifier (e.g. `eth`, `bsc`, `solana`) |

**Example event (`tx`):**
```json
{
  "type": "tx",
  "pair": "0xabc...",
  "chain": "eth",
  "time": 1710000000,
  "tx_hash": "0xdef...",
  "side": "buy",
  "amount_usd": 1500.0,
  "price": 0.00042,
  "sender": "0x123..."
}
```

### Subscribe: Live Kline Updates

Subscribe message:
```json
{
  "jsonrpc": "2.0",
  "method": "subscribe",
  "params": ["kline", "<pair_address>", "<interval>", "<chain>"],
  "id": 1
}
```

| Field | Values |
|-------|--------|
| pair_address | Trading pair contract address |
| interval | `s1`, `k1`, `k5`, `k15`, `k30`, `k60`, `k120`, `k240`, `k1440`, `k10080` |
| chain | Chain identifier |

**Example event:**
```json
{
  "type": "kline",
  "pair": "0xabc...",
  "chain": "eth",
  "interval": "k60",
  "time": 1710000000,
  "open": 0.00040,
  "high": 0.00045,
  "low": 0.00038,
  "close": 0.00042,
  "volume": 85000.0
}
```

### Subscribe: Live Price Changes

Subscribe message:
```json
{
  "jsonrpc": "2.0",
  "method": "subscribe",
  "params": ["price", ["<address>-<chain>", ...]],
  "id": 1
}
```

| Field | Values |
|-------|--------|
| token list | Array of `address-chain` strings (e.g. `["0xabc-eth", "0xdef-bsc"]`) |

**Example event:**
```json
{
  "type": "price",
  "token_id": "0xabc-eth",
  "price": 0.00042,
  "price_change_5m": 0.8,
  "price_change_1h": -1.2,
  "time": 1710000000
}
```

### Unsubscribe

```json
{ "jsonrpc": "2.0", "method": "unsubscribe", "params": [], "id": 2 }
```
