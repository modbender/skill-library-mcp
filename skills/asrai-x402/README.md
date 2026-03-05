# Asrai — Crypto Analysis Skill

Crypto market analysis skill for Claude Code and AI agents. Powered by [Asrai](https://asrai.me) via x402 — pay $0.005 USDC per call, no subscription needed.

## Install

```bash
npx skills add abuzerasr/asrai-skill
```

Or via [ClawHub](https://clawhub.ai/abuzerasr/asrai-x402) — one-click install.

## What it does

- Technical analysis — ALSAT, SuperALSAT, AlphaTrend, PSAR, MACD-DEMA, TD
- Market screeners — gainers, losers, RSI extremes, MACD, volume
- Sentiment — CBBI, CMC sentiment, AI insights
- Price forecasting — AI 3–7 day predictions
- Smart money — order blocks, FVGs, support/resistance
- Elliott Wave analysis
- Cashflow & capital flow
- DEX data via DexScreener
- Ask AI — natural language crypto analysis

## Requirements

- Node.js (for `npx asrai-mcp`)
- A Base network wallet with a small USDC balance (~$1–2)

## Setup

Add to your Claude Desktop config (`claude_desktop_config.json`):

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

```json
{
  "mcpServers": {
    "asrai": {
      "command": "npx",
      "args": ["-y", "asrai-mcp"]
    }
  }
}
```

```
# ~/.env
ASRAI_PRIVATE_KEY=0x<your_private_key>
```

Config file locations:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

### n8n / Remote connections

```
HTTP Streamable: https://mcp.asrai.me/mcp?key=0x<your_private_key>
SSE (legacy):    https://mcp.asrai.me/sse?key=0x<your_private_key>
```

## Pricing

| Call type | Cost |
|---|---|
| Most tools | $0.005 USDC |
| `ask_ai` | $0.01 USDC |
| `indicator_guide` | FREE |
| Session cap | $2.00 USDC (configurable via `ASRAI_MAX_SPEND`) |

## Links

- Website: https://asrai.me/agents
- MCP npm package: https://www.npmjs.com/package/asrai-mcp
- ClawHub: https://clawhub.ai/abuzerasr/asrai-x402
