---
name: public-company-analysis
description: Analyze any listed company with a structured professional report: overview, in-depth fundamentals (incl. DCF), technicals + sentiment. Input ticker, name, or exchange.
version: 1.0.0
author: fengwensheng
tags: [stock, finance, investment, DCF, fundamental-analysis, technical-analysis, valuation, earnings, sentiment]
keywords: [stock analysis, financial report, DCF valuation, equity research, stock picker, fundamentals, technicals, sentiment analysis]
---

# Public Company Deep Research Skill

**Activation Triggers**  
Immediately start this skill when the user expresses any of the following intents (support English + major other languages if possible):

- "Analyze [company/ticker]"
- "Give me a report on $TSLA / 600519.SH / 0700.HK"
- "Is [company] a good buy right now?"
- "Fundamental + technical analysis for AAPL"
- "Value [company] using DCF"
- "Compare [companyA] vs [companyB]"
- "Latest valuation and news on NVDA"

Before starting analysis, if the company is ambiguous, politely ask for clarification (ticker + exchange preferred, e.g. 600519.SH, TSLA, 0700.HK).

**Mandatory Output Structure**  
Always follow this exact 3-part format. Do not add, remove, or reorder major sections. Obtain real-time market data through online search tools. Use professional, neutral, data-driven tone. End with standard disclaimer.

## Part 1: Company Overview

- **Basic Information**  
  Ticker / Exchange / Latest market cap / Float cap / GICS sector & industry / Founded / Headquarters / IPO year (if applicable)

- **Business Model**  
  Concise description (≤200 words): core products/services, revenue breakdown (by segment/geography if available), moat / competitive advantages, key customers or suppliers (if material and public)

- **Industry Position**  
  Market share ranking (if known), top 3–5 competitors, industry growth stage / cycle, recent regulatory or macro events affecting the sector

## Part 2: Fundamental Analysis (Deep Dive)

1. **Financial Performance** (include trend commentary + simple ASCII charts or describe key visuals)  
   Last 5 years (or since IPO): Revenue, Net Income, Gross Margin, Operating Margin, ROE, ROA  
   Highlight inflection points and YoY / CAGR trends.

2. **Profitability Analysis**  
   Margin trends & drivers, cost control, quality of earnings (扣非 / non-recurring items), dependency on one-time gains

3. **Solvency & Liquidity Assessment**  
   Debt-to-Asset, Current Ratio, Quick Ratio, Interest Coverage, Operating / Free Cash Flow trends

4. **Growth Evaluation**  
   Historical 3–5 year revenue / EPS CAGR, visible growth drivers for next 2–3 years (new products, expansion, M&A, etc.), risks to growth thesis

5. **Valuation Analysis**
    - **DCF Valuation**  
      State main assumptions clearly: forecast period, revenue / FCF growth rates, terminal growth rate (2–3%), WACC / discount rate  
      Output: Intrinsic value per share, current price, implied upside / downside margin of safety (%)

    - **Relative Valuation Comparison Table** (use Markdown table)

      | Metric          | Current Company | Industry Avg | Peer A       | Peer B       | 5-Year Historical Median |
      |-----------------|-----------------|--------------|--------------|--------------|--------------------------|
      | Trailing P/E    |                 |              |              |              |                          |
      | Forward P/E     |                 |              |              |              |                          |
      | P/B             |                 |              |              |              |                          |
      | PEG Ratio       |                 |              |              |              |                          |
      | EV/EBITDA       |                 |              |              |              |                          |

## Part 3: Technical & Sentiment Analysis

1. **Price & Technical Setup**  
   Current price, 52-week range, performance (1M/3M/6M/12M), key support/resistance levels, moving average alignment (50/200 DMA), latest MACD / RSI / KDJ signals & interpretation

2. **Sentiment & News Flow**  
   Recent 30-day sentiment summary (bullish / neutral / bearish tilt)  
   Key catalysts / events (earnings, insider trades, analyst upgrades/downgrades, regulatory news)  
   3–5 most representative recent opinions from institutions / influential accounts / forums (X, Reddit, Seeking Alpha, etc.)

**Preferred Data Sources** (in priority order):  
Yahoo Finance, SEC/EDGAR, company IR website, HKEX/SSE/SZSE filings, Morningstar, Seeking Alpha, Finviz, TradingView, Bloomberg snippets (if accessible), recent analyst reports

**Tone & Disclaimer**  
Remain objective and fact-based. Never give explicit buy/sell/hold recommendations.  
Always close with:  
**"Investment involves risks. The above is for informational purposes only and not investment advice. Please conduct your own research."**

Start by confirming: Which listed company would you like analyzed? (Ticker + exchange is best)