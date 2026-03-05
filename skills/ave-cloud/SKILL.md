---
name: ave-cloud
version: 1.1.2
description: |
  Query on-chain crypto data via the AVE Cloud API (https://cloud.ave.ai/).
  Use this skill whenever the user wants to:
  - Search for tokens by name, symbol, or contract address
  - Get token prices, market cap, TVL, volume, or price change data
  - View kline/candlestick (OHLCV) chart data for a token or trading pair
  - Check top 100 token holders and their distribution
  - Browse recent swap transactions for a trading pair
  - View trending or ranked tokens by chain or topic (hot, meme, gainer, loser, AI, DePIN, etc.)
  - Run a contract security/risk detection report (honeypot, tax, ownership)
  - List supported chains or main tokens on a chain
  - Stream real-time swap/liquidity events for a trading pair (pro plan)
  - Monitor live kline/candlestick updates for a pair in real time (pro plan)
  - Subscribe to live price change notifications for one or more tokens (pro plan)
  - Run an interactive WebSocket REPL to manage subscriptions live (pro plan)
  Trigger on /ave-cloud or any query involving on-chain token data, DEX analytics,
metadata:
  openclaw:
    primaryEnv: AVE_API_KEY
    requires:
      env:
        - AVE_API_KEY
        - API_PLAN
      bins:
        - python3
---

# AVE Cloud Skill

The AVE Cloud API provides on-chain analytics across 130+ blockchains and 300+ DEXs.
This skill runs Python scripts to call the API and returns results as clear summaries.

## Setup

Two environment variables are required:

```bash
export AVE_API_KEY="your_api_key_here"
export API_PLAN="free"   # allowed: free, normal, pro
```

Get a free key at https://cloud.ave.ai/register. For higher limits, contact support on Telegram: @ave_ai_cloud.

**Rate limiting** is handled by a built-in file-based limiter by default — no packages needed beyond the Python standard library.

**Docker** (sandboxed, uses `requests` + `requests-ratelimiter` for in-process rate limiting):

```bash
# Build once
docker build -f scripts/Dockerfile.txt -t ave-cloud .

# Run a command (example: search)
docker run --rm \
  -e AVE_API_KEY="your_key" \
  -e API_PLAN=free \
  ave-cloud search --keyword WBNB --chain bsc
```

The Docker image sets `AVE_USE_DOCKER=true` automatically, enabling in-process rate limiting via `requests-ratelimiter`. No volume mount needed.

If you want to run locally with the same in-process rate limiter (requires `pip install -r scripts/requirements.txt`):

```bash
export AVE_USE_DOCKER=true
python scripts/ave_client.py <command> [options]
```

## How to use this skill

1. Identify what the user wants from the list of operations below
2. Run the appropriate command using `scripts/ave_client.py`
3. Format the JSON response as a readable summary or table

The script is at `scripts/ave_client.py` relative to the skill root.

All commands output JSON to stdout. Errors are printed to stderr with a non-zero exit code.

## Operations

### Search tokens
Find tokens by symbol, name, or contract address.

```bash
python scripts/ave_client.py search --keyword <keyword> [--chain <chain>] [--limit 20]
```

Useful when the user gives a token name/symbol and you need to resolve it to a contract address.

### Platform tokens
Tokens from a specific launchpad or platform (e.g. pump.fun, fourmeme, bonk, nadfun).

```bash
python scripts/ave_client.py platform-tokens --platform <platform>
```

Common platforms: `hot`, `new`, `meme`, `pump_in_hot`, `pump_in_new`, `fourmeme_in_hot`, `bonk_in_hot`, `nadfun_in_hot`
Full list of ~90 values is enforced by the CLI (`--help` to list them).

### Token detail
Full data for a specific token: price, market cap, TVL, volume, supply, holders, DEX pairs.

```bash
python scripts/ave_client.py token --address <contract_address> --chain <chain>
```

### Token prices (batch)
Prices for up to 200 tokens at once.

```bash
python scripts/ave_client.py price --tokens <addr1>-<chain1> <addr2>-<chain2> ...
```

### Kline / candlestick data
OHLCV price history. Use `kline-token` when you have a token address; use `kline-pair` when you have a pair address.

```bash
python scripts/ave_client.py kline-token --address <token> --chain <chain> \
  [--interval <minutes>] [--size <count>]

python scripts/ave_client.py kline-pair --address <pair> --chain <chain> \
  [--interval <minutes>] [--size <count>]
```

Valid intervals (minutes): `1 5 15 30 60 120 240 1440 4320 10080`
Default: interval=60, size=24

### Top 100 holders
Holder distribution for a token.

```bash
python scripts/ave_client.py holders --address <token> --chain <chain>
```

### Swap transactions
Recent swap history for a trading pair.

```bash
python scripts/ave_client.py txs --address <pair> --chain <chain>
```

### Trending tokens
Currently trending tokens on a specific chain.

```bash
python scripts/ave_client.py trending --chain <chain> [--page 0] [--page-size 20]
```

### Ranked tokens by topic
Token rankings for a topic category.

First, list available topics:
```bash
python scripts/ave_client.py rank-topics
```

Then get tokens for a topic:
```bash
python scripts/ave_client.py ranks --topic <topic>
```

Common topics: `hot`, `meme`, `gainer`, `loser`, `new`, `ai`, `depin`, `gamefi`, `rwa`,
`eth`, `bsc`, `solana`, `base`, `arbitrum`, `optimism`, `avalanche`

### Contract risk report
Security analysis: honeypot detection, buy/sell tax, ownership, liquidity lock.

```bash
python scripts/ave_client.py risk --address <token> --chain <chain>
```

This is useful before the user considers interacting with an unknown token.

### Supported chains
Full list of supported chain identifiers.

```bash
python scripts/ave_client.py chains
```

### Main tokens on a chain
The primary/native tokens for a given chain.

```bash
python scripts/ave_client.py main-tokens --chain <chain>
```

## WebSocket Streams (pro plan)

Real-time data streams require `API_PLAN=pro` and `websocket-client` installed (`pip install -r scripts/requirements.txt`).
Each event is printed as pretty-printed JSON followed by `---`. Press Ctrl+C to stop.

### Interactive REPL (recommended for live monitoring)

Start a persistent WebSocket connection with an interactive command prompt:

```bash
docker run -it \
  -e AVE_API_KEY="your_key" \
  -e API_PLAN=pro \
  ave-cloud wss-repl
```

Or locally (requires `pip install -r scripts/requirements.txt`):

```bash
API_PLAN=pro AVE_API_KEY="your_key" python scripts/ave_client.py wss-repl
```

Once connected, type commands at the `>` prompt. JSON events stream to stdout; UI messages go to stderr.

| Command | Description |
|---------|-------------|
| `subscribe price <addr-chain> [...]` | Live price updates for one or more tokens |
| `subscribe tx <pair> <chain> [tx\|multi_tx\|liq]` | Swaps or liquidity events for a pair |
| `subscribe kline <pair> <chain> [interval]` | Kline candle updates for a pair |
| `unsubscribe` | Cancel current subscription |
| `help` | Show command reference |
| `quit` | Close connection and exit |

Example session:
```
> subscribe price 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2-eth
{...price event...}
---
> unsubscribe
> subscribe kline 0xabc-eth solana k5
{...kline event...}
---
> quit
```

### Stream live swap/liquidity events for a pair

```bash
python scripts/ave_client.py watch-tx --address <pair_address> --chain <chain> [--topic tx]
```

`--topic` choices: `tx` (swaps, default), `multi_tx` (batch swaps), `liq` (liquidity add/remove)

### Stream live kline updates for a pair

```bash
python scripts/ave_client.py watch-kline --address <pair_address> --chain <chain> [--interval k60]
```

`--interval` choices: `s1 k1 k5 k15 k30 k60 k120 k240 k1440 k10080`

### Stream live price changes for tokens

```bash
python scripts/ave_client.py watch-price --tokens <addr1>-<chain1> [<addr2>-<chain2> ...]
```

Multiple token IDs can be provided space-separated.

## Formatting responses

When presenting results to the user:

- **Token detail**: show price, 24h change, market cap, volume, TVL, top DEX pairs, risk level
- **Kline data**: summarize trend (up/down), high/low/close over the period; an ASCII table works well for recent candles
- **Holders**: show top 5-10 holders with % share, flag if top 10 hold >50% (concentration risk)
- **Swap txs**: show most recent 10 as a table with time, type (buy/sell), amount USD, wallet
- **Trending/ranks**: show as a ranked table with price, 24h change, volume
- **Risk report**: lead with the risk level (LOW/MEDIUM/HIGH/CRITICAL), then key findings (honeypot, tax rates, ownership renounced/not)
- **Search results**: show as a table — symbol, name, chain, contract address, price, 24h change
- **WebSocket streams**: each event arrives as a JSON object; summarize key fields (time, type, price, amount) as they arrive; for `wss-repl`, remind the user to type `quit` or Ctrl+C to stop

If a chain identifier is unclear, run `chains` first to look it up.

## Reference

See `references/api-endpoints.md` for the full endpoint reference with parameters and response fields.
