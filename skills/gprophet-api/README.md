# G-Prophet API Skills

AI-powered stock prediction and market analysis capabilities for OpenClaw agents.

## Features

- 📈 Stock price prediction (1-30 days)
- 🌍 Multi-market support (US, CN, HK, Crypto)
- 🤖 Multiple AI algorithms (G-Prophet2026V1, LSTM, Transformer, etc.)
- 📊 Technical analysis (RSI, MACD, Bollinger Bands, KDJ)
- 💹 Market sentiment analysis
- 🔍 Deep multi-agent analysis

## Installation

This skill requires a G-Prophet API key. Get yours at:
https://www.gprophet.com/settings/api-keys

Set your API key:
```bash
export GPROPHET_API_KEY="gp_sk_your_key_here"
```

Or add to `~/.openclaw/agents/main/agent/auth-profiles.json`:
```json
{
  "gprophet": "gp_sk_your_key_here"
}
```

## Usage

### Predict Stock Price
```
/gprophet predict AAPL US 7
```

### Technical Analysis
```
/gprophet analyze TSLA US
```

### Market Overview
```
/gprophet market CN
```

## Documentation

See [SKILL.md](./SKILL.md) for complete API documentation.

## License

MIT
