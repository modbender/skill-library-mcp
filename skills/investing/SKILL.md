---
name: investing
version: 1.0.0
description: Personal investing assistant for Lithuanian investors. Monitors markets, ETFs, crypto, pension funds (III pakopa), and provides monthly investment suggestions based on research and market conditions.
author: Buba Draugelis
license: MIT
tags:
  - finance
  - investing
  - etf
  - crypto
  - lithuania
  - pension
metadata:
  openclaw:
    emoji: "💰"
---

# Investing Skill

A comprehensive investing assistant tailored for Lithuanian investors, inspired by šešiNuliai.lt philosophy.

## Core Philosophy

Based on evidence-based, passive investing:
- **VWCE & Chill** - Simple, low-cost global ETF strategy
- **Long-term focus** - 10+ year investment horizon
- **Diversification** - Across asset classes and geographies
- **Low costs** - Minimize fees, maximize returns

## Asset Allocation Framework

### Recommended Portfolio (Moderate Risk)

```
📊 Sample Allocation:
├── 70% Stocks (ETFs)
│   ├── 50% VWCE (All-World)
│   ├── 15% IXUS (Ex-US) or EIMI (Emerging)
│   └── 5% Small Cap Value
├── 10% Bonds
│   └── AGGH or Government Bonds
├── 10% Crypto
│   ├── 8% Bitcoin
│   └── 2% Ethereum
└── 10% Cash / Short-term
    └── Savings accounts, MMF
```

Adjust based on:
- Age (younger = more stocks)
- Risk tolerance
- Time horizon
- Income stability

## Data Sources

### Lithuanian Sources
- **šešiNuliai.lt** - Personal finance blog (LT)
- **Investuok.eu** - Investment news (LT)
- **Vz.lt** - Business news (LT)
- **Delfi Verslas** - Business section

### International Sources
- **Bogleheads** - Passive investing community
- **r/eupersonalfinance** - EU-focused Reddit
- **JustETF** - ETF comparison tool
- **Portfolio Visualizer** - Backtesting

### Market Data
- **Yahoo Finance** - Stock/ETF prices
- **TradingView** - Charts
- **CoinGecko** - Crypto prices
- **ECB** - EUR exchange rates, interest rates

## Scripts

### check-etf-prices.sh

```bash
#!/bin/bash
# Check key ETF prices
echo "📈 ETF Prices - $(date '+%Y-%m-%d')"
echo "================================"

# VWCE - Vanguard FTSE All-World
curl -s "https://query1.finance.yahoo.com/v8/finance/chart/VWCE.DE" | \
  jq -r '"VWCE: €" + (.chart.result[0].meta.regularMarketPrice | tostring)'

# EIMI - iShares Emerging Markets
curl -s "https://query1.finance.yahoo.com/v8/finance/chart/EIMI.L" | \
  jq -r '"EIMI: £" + (.chart.result[0].meta.regularMarketPrice | tostring)'

# Bitcoin
curl -s "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur" | \
  jq -r '"BTC: €" + (.bitcoin.eur | tostring)'
```

### monthly-dca.sh

```bash
#!/bin/bash
# Calculate monthly DCA amounts
BUDGET=${1:-500}  # Monthly investment budget

echo "💰 Monthly DCA Plan - €$BUDGET"
echo "================================"
echo "VWCE (70%):   €$((BUDGET * 70 / 100))"
echo "EIMI (10%):   €$((BUDGET * 10 / 100))"
echo "BTC (10%):    €$((BUDGET * 10 / 100))"
echo "Cash (10%):   €$((BUDGET * 10 / 100))"
```

## Monthly Investment Workflow

### 1. Market Check (5 min)

```
Run: check-etf-prices.sh
Check: Any significant drops (>10%) = buying opportunity
```

### 2. News Scan (10 min)

```
Scan:
- šešiNuliai.lt - new posts?
- r/eupersonalfinance - hot topics?
- ECB announcements - rate changes?
```

### 3. Execute DCA (5 min)

```
Run: monthly-dca.sh [budget]
Execute trades via:
- Interactive Brokers (ETFs)
- Bitstamp/Kraken (Crypto)
```

### 4. Record & Reflect (5 min)

```
Update:
- Portfolio tracker spreadsheet
- Note any deviations from plan
- Review annual progress
```

## III Pakopa (Pension) Strategy

### When III Pakopa Makes Sense

1. **Employer contribution** - Free money, always take it
2. **High tax bracket** - 32%+ marginal rate
3. **Long horizon** - 15+ years to retirement
4. **Old contract** - Pre-2019 rules may be better

### Recommended Funds

| Fund | TER | Notes |
|------|-----|-------|
| Goindex III pakopa | 0.40% | Index-tracking, low cost |
| Swedbank Index | 0.45% | Also index-based |
| Luminor Index | 0.50% | Decent alternative |

**Avoid:** High-fee active funds (1%+ TER)

### Yearly Optimization

1. Max out employer match first
2. Calculate tax benefit vs fees
3. Consider personal IBKR account for overflow
4. Review fund performance annually

## Crypto Strategy

### Core Holdings (90% of crypto allocation)

- **Bitcoin (BTC)** - 80% of crypto
- **Ethereum (ETH)** - 20% of crypto

### Rules

1. Never more than 10% of total portfolio
2. DCA monthly, don't time the market
3. Self-custody for large amounts (Ledger/Trezor)
4. Hold through cycles (5+ years)

### Where to Buy (EU)

- **Bitstamp** - Low fees, EU regulated
- **Kraken** - Good security, SEPA
- **Coinbase** - Easy, but higher fees

## Emergency Fund

Before investing, ensure:

```
Emergency Fund = 3-6 months expenses
Location: High-yield savings account
Current best rates (LT):
- Swedbank Taupomasis: ~3%
- SEB Taupomoji: ~2.5%
- Revolut Savings: ~3.5%
```

## Tax Considerations (Lithuania)

### Capital Gains

- **15%** tax on gains
- **Holding period:** No benefit for long-term (unlike US)
- **Losses:** Can offset gains in same year

### III Pakopa Tax Benefits

- **Contribution:** Deduct from taxable income (up to €1,500/year)
- **Withdrawal:** Taxed at 15% (or 0% if after retirement age)

### Crypto

- **15%** on realized gains
- Track cost basis carefully
- Report in annual declaration

## Cron Jobs

### Daily Price Alert

```javascript
{
  "name": "Daily Market Check",
  "schedule": { "kind": "cron", "expr": "0 9 * * 1-5" },
  "payload": {
    "kind": "agentTurn",
    "message": "Check VWCE, BTC prices. Alert if >5% change from yesterday."
  }
}
```

### Monthly Investment Reminder

```javascript
{
  "name": "Monthly DCA Reminder",
  "schedule": { "kind": "cron", "expr": "0 10 1 * *" },
  "payload": {
    "kind": "agentTurn",
    "message": "Monthly DCA time! Check budget, run monthly-dca.sh, execute trades."
  }
}
```

### Quarterly Review

```javascript
{
  "name": "Quarterly Portfolio Review",
  "schedule": { "kind": "cron", "expr": "0 10 1 1,4,7,10 *" },
  "payload": {
    "kind": "agentTurn",
    "message": "Quarterly review: Check allocation drift, rebalance if >5% off target, update spreadsheet."
  }
}
```

## Resources

### Books
- "The Simple Path to Wealth" - JL Collins
- "A Random Walk Down Wall Street" - Burton Malkiel
- "The Bogleheads' Guide to Investing"

### Websites
- šešiNuliai.lt (LT)
- Bogleheads.org
- JustETF.com
- r/eupersonalfinance

### Tools
- Portfolio Visualizer (backtesting)
- IBKR (brokerage)
- Notion/Sheets (tracking)

## Disclaimer

This is not financial advice. Do your own research. Past performance does not guarantee future results. Investing involves risk of loss.

---

*Skill created based on research from šešiNuliai.lt, Bogleheads, and EU personal finance communities.*
