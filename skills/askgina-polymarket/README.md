# askgina-polymarket

Polymarket via Gina. Search, trade, and automate prediction market strategies.

## Connect

```
https://askgina.ai/ai/predictions/mcp
```

1. Sign in at [askgina.ai](https://askgina.ai) and open **Agent Setup** (sidebar or `https://askgina.ai/agent-setup`).
2. Name your token (e.g. "OpenClaw on MacBook"), click **Generate Token**, and copy the config — it's only shown once.
3. Paste into your MCP client:

```json
{
  "mcpServers": {
    "gina-predictions": {
      "transport": "http",
      "url": "https://askgina.ai/ai/predictions/mcp",
      "headers": {
        "Authorization": "Bearer <PASTE_TOKEN_HERE>"
      }
    }
  }
}
```

4. Restart your MCP client and ask: `"What can you do with gina"`.

Tokens expire after 90 days. You can have up to 5 active tokens and revoke any from the Agent Setup page.

Works with: OpenClaw, Claude Code, Codex, Cursor, Windsurf, and any MCP client.

## What You Can Do

Just type natural language:

- **Search**: `"NBA markets tomorrow"`, `"Fed rate decision odds"`
- **Trending**: `"what's trending on Polymarket?"`, `"what are people betting on?"`
- **Crypto / stocks**: `"BTC 15 min up or down"`, `"AAPL daily market"`
- **Trade**: `"bet $10 on eagles to win"`, `"buy Yes at 0.40 or better"`
- **Positions**: `"show my positions"`, `"what's my P&L?"`
- **Automate**: `"daily market briefing at 9am"`, `"alert me on odds swings"`

Full features with all example prompts: https://docs.askgina.ai/predictions-mcp/features

## How It Works

- **Auth**: Long-lived JWT token from `https://askgina.ai/agent-setup`. Expires after 90 days; revoke anytime.
- **Wallets**: Self-custodial via [Privy](https://privy.io). You own your keys.
- **Trades**: On-chain on Polymarket (Polygon / USDC). Large trades require confirmation.
- **Gas**: Gina provides gas sponsorship to help cover fees.
- **Automations**: Create, list, pause, or delete anytime via prompts.
- **Security**: Treat your token like a private key — never share it publicly.

## Links

- **Docs**: https://docs.askgina.ai
- **Quick start**: https://docs.askgina.ai/predictions-mcp/quick-start
- **Client setup**: https://docs.askgina.ai/predictions-mcp/client-setup
- **Terms**: https://askgina.ai/terms-and-conditions
- **Twitter**: https://x.com/askginadotai

## About Gina

Gina is agentic onchain infrastructure — trade, analyze, and automate across 12+ chains, prediction markets, and perpetual futures, all through natural language.

https://askgina.ai
