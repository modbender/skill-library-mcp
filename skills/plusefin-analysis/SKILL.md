---
name: plusefin-analysis
description: AI-ready stock analysis - ticker data, options, sentiment, predictions. Get your free API key at https://plusefin.com
metadata:
  {
    "openclaw":
      {
        "emoji": "📈",
        "homepage": "https://github.com/plusefin/plusefin-skill",
        "requires": { "bins": ["python3"], "env": ["PLUSEFIN_API_KEY"] },
        "primaryEnv": "PLUSEFIN_API_KEY"
      }
  }
---

# PlusE Financial Analysis

AI-ready financial data. ML-processed so your AI understands it directly.

**Free tier available** - [Get API Key](https://console.plusefin.com)

## Setup

```bash
# Required: Your PlusE API key (get free at https://plusefin.com)
export PLUSEFIN_API_KEY=your_api_key
```

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `ticker` | Company overview, valuation, ratings | `python {baseDir}/plusefin.py ticker AAPL` |
| `price-history` | Historical prices + signals | `python {baseDir}/plusefin.py price-history NVDA 1y` |
| `statements` | Financial statements | `python {baseDir}/plusefin.py statements AAPL income` |
| `earnings` | Earnings history | `python {baseDir}/plusefin.py earnings NVDA` |
| `news` | Stock news | `python {baseDir}/plusefin.py news TSLA` |
| `options` | Options chain | `python {baseDir}/plusefin.py options TSLA 20` |
| `options-analyze` | Options analysis | `python {baseDir}/plusefin.py options-analyze AAPL` |
| `sentiment` | Market Fear & Greed | `python {baseDir}/plusefin.py sentiment` |
| `sentiment-history` | Historical sentiment | `python {baseDir}/plusefin.py sentiment-history 10` |
| `prediction` | Price prediction | `python {baseDir}/plusefin.py prediction AAPL` |
| `fred` | Economic data (GDP, etc.) | `python {baseDir}/plusefin.py fred GDP` |
| `fred-search` | Search indicators | `python {baseDir}/plusefin.py fred-search unemployment` |
| `holders` | Institutional holdings | `python {baseDir}/plusefin.py holders SPY` |
| `insiders` | Insider trading | `python {baseDir}/plusefin.py insiders NVDA` |

## Parameters

- `price-history`: period = `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`
- `options`: num = number of options (default: 20)
- `statements`: type = `income`, `balance`, `cash`
- `sentiment-history/trend`: days (default: 10)
