---
name: asrai-x402
description: Crypto market analysis using Asrai API. Covers technical analysis, screeners, sentiment, forecasting, smart money, Elliott Wave, cashflow, DEX data, and AI-powered insights. Requires asrai-mcp installed and ASRAI_PRIVATE_KEY env var set. Each API call costs $0.005 USDC from your own wallet on Base mainnet via x402.
license: MIT
---

# Asrai — Crypto Analysis via x402

## Prerequisites

This skill requires **asrai-mcp** (Node.js, zero install). Add to Claude Desktop config:

```json
{
  "mcpServers": {
    "asrai": {
      "command": "npx",
      "args": ["-y", "asrai-mcp"],
      "env": { "ASRAI_PRIVATE_KEY": "0x<your_private_key>" }
    }
  }
}
```

Or store the key in `~/.env` and omit the `env` block:
```
ASRAI_PRIVATE_KEY=0x<your_private_key>
```

Config file location: macOS `~/Library/Application Support/Claude/claude_desktop_config.json`, Windows `%APPDATA%\Claude\claude_desktop_config.json`, Linux `~/.config/Claude/claude_desktop_config.json`.

For **n8n / remote connections**, use the hosted SSE server — no install needed:
- HTTP Streamable: `https://mcp.asrai.me/mcp?key=0x<your_private_key>`
- SSE (legacy): `https://mcp.asrai.me/sse?key=0x<your_private_key>`

Each API call costs **$0.005 USDC** from your wallet on Base mainnet ($0.01 for `ask_ai`). `indicator_guide` is FREE.

## Payment transparency

- Always inform the user of the cost before making calls if they ask.
- The `ASRAI_MAX_SPEND` env var sets a per-session cap (default $2.00).
- Payments are signed by the user's own wallet — never a shared key.

## MCP tools available

| Tool | What it does | Cost |
|---|---|---|
| `market_overview` | Trending, gainers/losers, RSI, top/bottom, CMC AI, CBBI, channel narratives, cashflow, sentiment, social dominance + 9 screeners (ATH, ichimoku-trend, bounce-dip, SAR, MACD, EMA cross, tech rating, volume, high-vol low-cap) | $0.095 (19 calls) |
| `technical_analysis(symbol, timeframe)` | Signal, ALSAT, SuperALSAT, PSAR, MACD-DEMA, AlphaTrend, TD, forecast, smart money, support/resistance, Elliott Wave, Ichimoku | $0.06 (12 calls) |
| `sentiment` | CBBI, CMC sentiment, CMC AI | $0.015 (3 calls) |
| `forecast(symbol)` | AI price forecast | $0.005 |
| `screener(type)` | Find coins by criteria | $0.005 |
| `smart_money(symbol, timeframe)` | SMC, order blocks, FVGs, support/resistance | $0.01 (2 calls) |
| `elliott_wave(symbol, timeframe)` | Elliott Wave analysis | $0.005 |
| `ichimoku(symbol, timeframe)` | Ichimoku cloud | $0.005 |
| `cashflow(mode, symbol)` | Capital flow | $0.005 |
| `coin_info(symbol)` | Stats, info, price, tags, CMC AI + auto DEX data via contract address if available | $0.025–$0.03 (5–6 calls) |
| `dexscreener(contract)` | DEX data | $0.005 |
| `chain_tokens(chain, max_mcap)` | Low-cap tokens on chain | $0.005 |
| `portfolio` | Abu's curated model portfolio — use when asked for investment advice or "what to buy". No symbol = full portfolio. Symbol = Abu's position for that coin. | $0.005 |
| `channel_summary` | Latest narratives | $0.005 |
| `ask_ai(question)` | AI analyst answer | $0.01 |
| `indicator_guide(name)` | Guide for Asrai custom indicators (ALSAT, SuperALSAT, PMax, AlphaTrend, MavilimW etc.) | FREE |

## indicator_guide usage

Call only when you encounter an unfamiliar indicator name in tool output. Standard indicators (RSI, MACD, Ichimoku, BB, Elliott Wave) are well-known — skip them.

- `indicator_guide()` or `indicator_guide("list")` → compact 1-line summary of all custom indicators
- `indicator_guide("ALSAT")` → full details for that indicator
- `indicator_guide("all")` → full guide for everything (avoid unless necessary)

## Output rules

- Write like an experienced trader explaining to a friend — conversational, confident, direct. Not a report template.
- Think like both a trader AND a long-term investor. Default to investor mode (macro thesis, cycle position, accumulation zones). Switch to trader mode only when user asks for entry/when to buy.
- Keep responses 200-400 words — thorough but easy to read. Short lines, breathing room between sections.
- Use emojis sparingly to mark section breaks where helpful — but don't force a fixed template. Let the response shape itself around what matters most.
- Never list raw indicator values — synthesize into plain language verdict.
- Avoid low-liquidity noise: prefer signals that appear across multiple indicators, have meaningful volume, or a clear catalyst.
- Never mention tool names, endpoints, or API calls in responses.
- End with 1 clear action bias: accumulate / wait / avoid — and why.

## Default analysis pattern

1. **Set regime** — BTC/ETH trend + market mood (CBBI)
2. **Find signals** — ALSAT/SuperALSAT cycle position, PMax trend, momentum
3. **Translate to action** — clear verdict: accumulate / wait / avoid + price zones

## References

- Full endpoint catalog: `skills/asrai/references/endpoints.md`
