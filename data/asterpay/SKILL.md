---
name: asterpay
description: EUR settlement and crypto data API for AI agents. Convert USDC to EUR via SEPA Instant. Access 16 pay-per-call endpoints for market data, AI tools, and crypto analytics.
metadata: {"clawdbot":{"emoji":"💶","requires":{"bins":["npx"],"env":[]},"primaryEnv":""}}
---

# AsterPay — EUR Settlement for AI Agents

## What it does

Gives your OpenClaw agent access to AsterPay's API — 16 endpoints for crypto market data, AI tools, and EUR settlement estimates. All endpoints use the x402 pay-per-call protocol (USDC on Base). Several endpoints are free.

## How to use

AsterPay runs as an MCP server. Add it to your OpenClaw configuration:

### Option 1: Via mcporter (recommended)

Tell your OpenClaw agent:

```
Install the AsterPay MCP server: npx -y @anthropic-ai/mcp-remote@latest https://x402-api-production-ba87.up.railway.app/mcp
```

### Option 2: Manual config in clawdbot.json

Add to your `clawdbot.json`:

```json
{
  "mcpServers": {
    "asterpay": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-remote@latest", "https://x402-api-production-ba87.up.railway.app/mcp"]
    }
  }
}
```

### Option 3: Local MCP server

```bash
npm install -g @asterpay/mcp-server
```

Then in `clawdbot.json`:

```json
{
  "mcpServers": {
    "asterpay": {
      "command": "asterpay-mcp-server"
    }
  }
}
```

## Available tools

### Free (no payment required)

| Tool | Description |
|------|------------|
| `discover_endpoints` | List all available API endpoints with pricing |
| `settlement_estimate` | Get USDC → EUR conversion estimate with real-time rates |
| `check_token_tiers` | View $ASTERPAY token discount tiers (up to 60% off) |
| `check_wallet_tier` | Check your wallet's token balance and discount tier |

### Market Data (paid via x402)

| Tool | Cost | Description |
|------|------|------------|
| `get_crypto_price` | $0.001 | Real-time price, market cap, 24h volume |
| `get_ohlcv` | $0.005 | OHLCV candlestick data for charting |
| `get_trending` | $0.002 | Currently trending tokens |

### AI Tools (paid via x402)

| Tool | Cost | Description |
|------|------|------------|
| `ai_summarize` | $0.01 | Summarize any text |
| `ai_sentiment` | $0.01 | Sentiment analysis (positive/negative/neutral) |
| `ai_translate` | $0.02 | Translate text to any language |
| `ai_code_review` | $0.05 | Code review with security analysis |

### Crypto Analytics (paid via x402)

| Tool | Cost | Description |
|------|------|------------|
| `wallet_score` | $0.05 | Wallet reputation and risk score |
| `token_analysis` | $0.10 | Token security audit (honeypots, rug pulls) |
| `whale_alerts` | $0.02 | Large crypto movements |

### Utilities (paid via x402)

| Tool | Cost | Description |
|------|------|------------|
| `generate_qr_code` | $0.005 | QR code generation |
| `take_screenshot` | $0.02 | Webpage screenshots |
| `generate_pdf` | $0.03 | HTML to PDF conversion |

## Example prompts

- "What's the current price of Ethereum?"
- "How much EUR would I get for 1000 USDC?"
- "Analyze the sentiment of this article about Bitcoin"
- "Check if this token contract is safe: 0x..."
- "Show me whale alerts on Base network"
- "What are the trending cryptocurrencies right now?"

## How x402 payments work

Paid endpoints return a 402 Payment Required response with payment details. To pay:

1. Install x402 fetch: `npm install @x402/fetch`
2. Configure a wallet with USDC on Base network
3. The SDK handles payment automatically per API call

Free endpoints (settlement_estimate, discover_endpoints, token tiers) work without any wallet.

## About AsterPay

AsterPay is the EUR settlement layer for AI agent commerce:

- **USDC → EUR** via SEPA Instant in under 10 seconds
- **Listed in Coinbase x402 ecosystem** — only EU EUR provider
- **MiCA-compliant** via licensed European partners
- **ERC-8004 registered** — Agent #16850 on Base
- **Certified on Arc Index** — on-chain NFT verification

Website: https://asterpay.io
Docs: https://asterpay.io/docs
API: https://x402-api-production-ba87.up.railway.app
GitHub: https://github.com/timolein74/asterpay-api
PyPI: `pip install asterpay`
npm: `@asterpay/mcp-server`

## Guardrails

- Never send more USDC than explicitly approved by the user
- Always show the settlement estimate before initiating any conversion
- Do not store or log wallet private keys
- Respect x402 payment confirmations — do not retry failed payments without user consent
