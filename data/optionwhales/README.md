# Option Flow Intelligence — OpenClaw Skill

An [OpenClaw](https://openclaw.ai/) agent skill that provides real-time option flow intelligence from the [OptionWhales](https://www.optionwhales.io) Pro API.

## What It Does

This skill teaches AI agents to query institutional option flow data:

- **Intent Momentum** — clustered option trades scored for directional intent, coherence, and momentum across all major US equity tickers
- **Abnormal Trades** — large or unusual option activity flagged in real-time
- **WebSocket Streaming** — real-time push notifications for abnormal trades (Pro tier)

## Quick Start

### 1. Install the Skill

```bash
clawhub install option-flow
```

### 2. Get an API Key

Sign up at [optionwhales.io](https://www.optionwhales.io) — free keys are issued instantly (no credit card required).

### 3. Configure

Add your key to `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "option-flow": {
        "enabled": true,
        "env": {
          "OPTIONWHALES_API_KEY": "ow_free_your_key_here"
        }
      }
    }
  }
}
```

### 4. Use It

Ask your agent:
- *"What's the option flow on AAPL today?"*
- *"Show me the top momentum tickers"*
- *"Any unusual options activity?"*
- *"Is TSLA bullish or bearish right now?"*

## API Tiers

| Feature | Free | Pro |
|---------|------|-----|
| Tickers returned | Top 3 | All |
| Abnormal trades | Last 5 | All |
| Rate limit | 10/min, 200/day | 60/min, 5000/day |
| Historical sessions | ❌ | ✅ |
| WebSocket streaming | ❌ | ✅ |
| Momentum history | ❌ | ✅ |

## CLI Helper

A standalone Python script is included for direct API access:

```bash
export OPTIONWHALES_API_KEY="ow_free_your_key_here"

# Current flow rankings
python3 scripts/optionflow.py flow

# Specific ticker detail
python3 scripts/optionflow.py flow --ticker AAPL

# Momentum rankings (top 5)
python3 scripts/optionflow.py momentum --top 5

# Current abnormal trades
python3 scripts/optionflow.py abnormal

# Available sessions
python3 scripts/optionflow.py sessions

# Account usage
python3 scripts/optionflow.py usage
```

No dependencies beyond Python 3.7+ standard library.

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /v1/flow/current` | Current session intent rankings |
| `GET /v1/flow/current/{ticker}` | Ticker detail with clusters + time series |
| `GET /v1/flow/sessions` | List available sessions |
| `GET /v1/flow/{session}` | Historical session rankings |
| `GET /v1/flow/{session}/{ticker}` | Historical ticker detail |
| `GET /v1/momentum/rankings` | Momentum-sorted rankings |
| `GET /v1/momentum/{ticker}/history` | Ticker momentum history |
| `GET /v1/abnormal-trades/current` | Current session abnormal trades |
| `GET /v1/abnormal-trades/{session}` | Historical abnormal trades |
| `GET /v1/account/usage` | Rate limit & usage stats |
| `WS /v1/ws/abnormal-trades` | Real-time abnormal trade stream (Pro) |

## Links

- **Website:** https://www.optionwhales.io
- **API Docs:** https://www.optionwhales.io/developers
- **API Base:** https://api.optionwhales.io

## License

MIT
