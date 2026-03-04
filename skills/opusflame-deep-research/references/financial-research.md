# Financial Research Reference

## Priority Sources (by reliability)

1. **Regulatory filings**: SEC EDGAR, Companies House (UK), SEDAR (Canada)
2. **Exchange data**: LSE RNS announcements, NYSE filings
3. **Earnings transcripts**: Seeking Alpha, The Motley Fool transcripts
4. **Analyst reports**: Visible Alpha, TipRanks, MarketBeat consensus
5. **Financial data**: Yahoo Finance, Google Finance, Finnhub, GuruFocus
6. **News**: Reuters, Bloomberg, FT, WSJ
7. **Community**: r/investing, r/wallstreetbets, StockTwits (sentiment only, not facts)

## Key Metrics to Collect

### Valuation
- Market cap, P/E (trailing & forward), P/S, P/B, EV/EBITDA

### Profitability
- Revenue + YoY growth, gross margin, operating margin, net margin, FCF

### Balance Sheet
- Cash, total debt, D/E ratio, current ratio, quick ratio

### Momentum
- 52-week range, % from high/low, RSI, short interest

### Ownership
- Institutional %, insider transactions (last 6 months), major holders

## UK-Listed Companies (AIM/LSE)

- Primary source: Investegate (investegate.co.uk) for RNS announcements
- Companies House for filings: find-and-update.company-information.service.gov.uk
- AIM companies report H1 + Full Year (no quarterly requirement)
- Watch for: trading updates, director dealings, significant shareholder notices

## Search Patterns

```
# SEC filings
site:sec.gov "[company name]" 10-K OR 10-Q

# UK RNS
site:investegate.co.uk "[company name]"

# Earnings transcripts
site:seekingalpha.com "[ticker]" earnings call transcript

# Analyst consensus
"[ticker]" analyst "price target" consensus

# Insider trades
"[ticker]" insider buying OR selling 2026
```
