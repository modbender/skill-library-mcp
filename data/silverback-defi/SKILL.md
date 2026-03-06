---
name: silverback-defi
description: DeFi intelligence powered by Silverback — 19 x402 endpoints on Base chain. Market data, swap quotes, technical analysis, yield opportunities, token audits, whale tracking, and AI chat. Pay per call with USDC.
homepage: https://silverbackdefi.app
user-invocable: true
disable-model-invocation: true
metadata: {"clawdbot":{"requires":{"bins":["curl","jq"]},"emoji":"🦍","category":"Finance & Crypto","tags":["defi","trading","crypto","yield","swap","analysis","base-chain","x402"]}}
---

# Silverback DeFi Intelligence

19 x402-paid DeFi endpoints on Base chain. Pay per call with USDC — no API keys, no subscriptions. All endpoints use the x402 micropayment protocol.

Base URL: `https://x402.silverbackdefi.app`

## Endpoints

### Chat ($0.05)
AI chat with all 19 intelligence tools. Ask any DeFi question.

```bash
curl -s -X POST https://x402.silverbackdefi.app/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the top coins right now?"}'
```

### Market Data ($0.001 each)

```bash
# Top coins by market cap
curl -s -X POST https://x402.silverbackdefi.app/api/v1/top-coins \
  -H "Content-Type: application/json" -d '{}'

# Top liquidity pools on Base
curl -s -X POST https://x402.silverbackdefi.app/api/v1/top-pools \
  -H "Content-Type: application/json" -d '{}'

# Top DeFi protocols by TVL
curl -s -X POST https://x402.silverbackdefi.app/api/v1/top-protocols \
  -H "Content-Type: application/json" -d '{}'

# Trending tokens
curl -s -X POST https://x402.silverbackdefi.app/api/v1/trending-tokens \
  -H "Content-Type: application/json" -d '{}'

# Base gas prices
curl -s -X POST https://x402.silverbackdefi.app/api/v1/gas-price \
  -H "Content-Type: application/json" -d '{}'

# Token details
curl -s -X POST https://x402.silverbackdefi.app/api/v1/token-metadata \
  -H "Content-Type: application/json" -d '{"token": "ETH"}'
```

### Trading & Analysis

```bash
# Swap quote with routing ($0.002)
curl -s -X POST https://x402.silverbackdefi.app/api/v1/swap-quote \
  -H "Content-Type: application/json" \
  -d '{"fromToken": "ETH", "toToken": "USDC", "amount": "1"}'

# Technical analysis — RSI, MACD, Bollinger ($0.02)
curl -s -X POST https://x402.silverbackdefi.app/api/v1/technical-analysis \
  -H "Content-Type: application/json" \
  -d '{"token": "ETH"}'

# Backtest a strategy ($0.10)
curl -s -X POST https://x402.silverbackdefi.app/api/v1/backtest \
  -H "Content-Type: application/json" \
  -d '{"token": "ETH", "strategy": "rsi", "days": 30}'

# Token correlation matrix ($0.005)
curl -s -X POST https://x402.silverbackdefi.app/api/v1/correlation-matrix \
  -H "Content-Type: application/json" \
  -d '{"tokens": ["ETH", "BTC", "VIRTUAL"]}'
```

### Yield & DeFi

```bash
# Yield opportunities ($0.02)
curl -s -X POST https://x402.silverbackdefi.app/api/v1/defi-yield \
  -H "Content-Type: application/json" \
  -d '{"token": "USDC"}'

# Pool health analysis ($0.005)
curl -s -X POST https://x402.silverbackdefi.app/api/v1/pool-analysis \
  -H "Content-Type: application/json" \
  -d '{"pool": "ETH/USDC"}'
```

### Security & Intelligence

```bash
# Token contract audit ($0.01)
curl -s -X POST https://x402.silverbackdefi.app/api/v1/token-audit \
  -H "Content-Type: application/json" \
  -d '{"token": "0x558881c4959e9cf961a7E1815FCD6586906babd2"}'

# Whale movement tracking ($0.01)
curl -s -X POST https://x402.silverbackdefi.app/api/v1/whale-moves \
  -H "Content-Type: application/json" \
  -d '{"token": "VIRTUAL"}'

# Arbitrage scanner ($0.005)
curl -s -X POST https://x402.silverbackdefi.app/api/v1/arbitrage-scanner \
  -H "Content-Type: application/json" -d '{}'

# Agent reputation — ERC-8004 ($0.001)
curl -s -X POST https://x402.silverbackdefi.app/api/v1/agent-reputation \
  -H "Content-Type: application/json" \
  -d '{"agentId": "13026"}'

# Discover agents by capability ($0.002)
curl -s -X POST https://x402.silverbackdefi.app/api/v1/agent-discover \
  -H "Content-Type: application/json" \
  -d '{"capability": "defi"}'
```

### Non-custodial Swap ($0.05)
Returns unsigned EIP-712 Permit2 data for client-side signing.

```bash
curl -s -X POST https://x402.silverbackdefi.app/api/v1/swap \
  -H "Content-Type: application/json" \
  -d '{"fromToken": "USDC", "toToken": "ETH", "amount": "10", "walletAddress": "0xYOUR_WALLET"}'
```

## Payment (x402 Protocol)

All endpoints return HTTP 402 with a USDC payment requirement. Your agent handles payment using `@x402/fetch` or any x402-compatible client with its own wallet.

Prices range from $0.001 to $0.10 per call. The exact amount is specified in the 402 response.

## Free Endpoints

```bash
# Health check
curl -s https://x402.silverbackdefi.app/api/v1/health

# Pricing info
curl -s https://x402.silverbackdefi.app/api/v1/pricing

# Endpoint list
curl -s https://x402.silverbackdefi.app/api/v1/endpoints
```

## MCP Server

For Claude Desktop, Cursor, or Claude Code:
```bash
npm install -g silverback-x402-mcp
```
https://www.npmjs.com/package/silverback-x402-mcp

## Links

- **Website**: https://silverbackdefi.app
- **x402 Docs**: https://silverbackdefi.app/x402
- **API**: https://x402.silverbackdefi.app
- **Source**: https://github.com/RidingLiquid/silverback-skill
