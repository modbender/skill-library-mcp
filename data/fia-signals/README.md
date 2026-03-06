# Fía Signals — OpenClaw Skill

Real-time crypto market intelligence for AI agents. Powered by Fía Signals' live trading system.

## What it does

Gives any OpenClaw agent instant access to professional-grade crypto market data:

- **Market regime** — TRENDING UP/DOWN/RANGING/VOLATILE with confidence score, RSI, ADX
- **Fear & Greed** — Current index with 7-day history and contrarian signal
- **Technical signals** — RSI-14, MACD, Bollinger Bands for any symbol
- **Funding rates** — Top perpetual futures funding rates (squeeze detector)
- **Prices** — Real-time spot prices for any symbols
- **Liquidations** — Recent liquidation events
- **Macro bundle** — Cross-asset signal bundle

## Quick start

```bash
# Free preview (no payment needed)
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh preview

# Paid endpoints (0.001-0.005 USDC via x402 on Base)
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh regime
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh fear-greed
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh signals BTCUSDT
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh funding
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh prices BTC,ETH,SOL
```

## Pricing

| Endpoint | Price |
|----------|-------|
| /preview | Free |
| /regime | $0.001 USDC |
| /fear-greed | $0.001 USDC |
| /funding | $0.001 USDC |
| /prices | $0.001 USDC |
| /signals | $0.005 USDC |
| /macro | $0.005 USDC |
| /correlation | $0.005 USDC |

Payment via x402 protocol on Base network (eip155:84532). USDC only.

## API

Live gateway: https://x402.fiasignals.com  
Discovery: https://x402.fiasignals.com/.well-known/x402.json  
Contact: fia-trading@agentmail.to

## About

Built by Fía Signals — an autonomous AI trading system running 24/7 on live crypto markets with real capital. The same intelligence that drives the trades, available per-call to any agent.

---

## Submitting to ClaWHub

1. Visit https://clawhub.com
2. Click "Submit a skill"
3. Fill in:
   - **Name:** fia-signals
   - **Description:** Real-time crypto market intelligence — regime, RSI, F&G, funding rates, liquidations (paste from SKILL.md description)
   - **Repository/Source:** Link to this skill directory or zip upload
   - **Category:** Finance / Market Data
   - **Tags:** crypto, trading, bitcoin, market-regime, signals, x402
4. Submit for review

Skills are reviewed and listed within 24-48 hours.
