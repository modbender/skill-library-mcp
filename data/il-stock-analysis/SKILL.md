---
name: il-stock-analysis
description: Comprehensive Israeli stock analysis for TASE-listed securities including fundamental analysis (financial metrics, business quality, valuation), technical analysis (indicators, chart patterns, support/resistance), stock comparisons, and investment report generation. Supports Hebrew and English queries, TASE tickers, and ETF numbers. Use when user requests analysis of Israeli stocks (e.g., "analyze ALRT", "compare Bank Leumi vs Bank Hapoalim", "analyze ETF 510893"), evaluation of financial metrics, technical chart analysis, or investment recommendations for securities traded on TASE (Tel Aviv Stock Exchange).
---

# Israeli Stock Analysis

## Overview

Perform comprehensive analysis of Israeli stocks and ETFs traded on TASE (Tel Aviv Stock Exchange) covering fundamental analysis (financials, business quality, valuation), technical analysis (indicators, trends, patterns), peer comparisons, and generate detailed investment reports. Fetch real-time market data via web search and apply structured analytical frameworks. Support for both Hebrew and English analysis.

## Supported Identifiers

This skill supports three ways to identify Israeli securities:

1. **TASE Ticker Symbols** (e.g., ALRT, DSCT, TASE, PELEOT)
2. **ETF Numbers** (Israeli ETF identification numbers, e.g., 510893, 770001)
3. **Company Names** (Hebrew or English, e.g., "בנק לאומי", "Bank Leumi", "טבע")

## Data Sources & Fetch Strategy

Use available MCPs and direct API calls to gather current market data for Israeli securities:

**Primary Data to Fetch:**
1. **Current stock/ETF price and trading data** (price, volume, 52-week range, in ILS)
2. **Financial statements** (income statement, balance sheet, cash flow in ILS)
3. **Key metrics** (P/E, EPS, dividend yield, book value, ROE, debt ratios)
4. **Analyst ratings and price targets** (Israeli and international analysts)
5. **Recent news and developments** (Hebrew financial news sources)
6. **Peer/competitor data** (for Israeli market comparisons)
7. **Technical data** (moving averages, RSI, MACD when available)
8. **Dividend history and distribution policy**

**Data Fetching Methods (Priority Order):**

**Option 1: Bundled Scripts (Recommended)**
- Use `scripts/fetch_tase_data.py` (Python, more robust)
- Or `scripts/fetch_tase_data.sh` (Shell, lightweight)
- Both support:
  - TASE tickers (ALRT, DSCT, TASE, etc.)
  - ETF numbers (510893, 770001, etc.)
  - Hebrew company names (בנק לאומי, בנק הפועלים, etc.)
  - Multiple API sources (Finnhub, Alpha Vantage)
  - Automatic fallback to mock data if API not configured

**Option 2: Configure API Key**
- Sign up for free at **finnhub.io** for real-time TASE data
- Set environment variable: `export FINNHUB_API_KEY=your_key`
- Scripts will automatically use it for live data
- No configuration needed otherwise — scripts provide mock data

**Option 3: Available MCPs**
- If an MCP for financial data is configured, use it to fetch TASE data
- Examples: Bloomberg MCP, Yahoo Finance MCP, TASE API MCP
- Call via: `mcporter call <server>.<tool> [arguments]`

**Option 4: Direct API Calls**
- TASE API (if available): Direct HTTP calls to tase.co.il API
- ISA (Israel Securities Authority) data APIs
- Public financial data APIs (Alpha Vantage, Finnhub)

**Data Source Priority:**
1. MCPs (if configured and available)
2. Direct API calls to TASE or ISA
3. Public financial data APIs (Alpha Vantage, Finnhub, etc. with Israeli support)
4. Company investor relations pages (automated fetch via curl)

**Identifier Resolution:**
- For ticker lookups: Query ticker symbol directly (ALRT, DSCT, TASE, etc.)
- For ETF numbers: Map ETF number to ticker or fetch via ISA database
- For Hebrew names: Translate or query company databases for ticker mapping

**Quality Sources:**
- TASE official API or database
- ISA (Israel Securities Authority) filings and databases
- Company investor relations pages (Hebrew and English)
- Bank of Israel publications (macro context)
- Direct financial data providers

**Currency Note:** All Israeli securities are denominated in New Israeli Shekel (ILS/₪). Always present prices and financial metrics in ILS unless specifically requesting USD conversion.

## Analysis Types

This skill supports four types of analysis. Determine which type(s) the user needs:

1. **Basic Stock Info** - Quick overview with key metrics
2. **Fundamental Analysis** - Deep dive into business, financials, valuation
3. **Technical Analysis** - Chart patterns, indicators, trend analysis
4. **Comprehensive Report** - Complete analysis combining all approaches

## Analysis Workflows

### 1. Basic Stock Information

**When to Use:** User asks for quick overview or basic info about an Israeli security

**Steps:**
1. Identify the security (ticker, ETF number, or Hebrew name)
2. Search for current stock/ETF data (price in ILS, volume, market cap)
3. Gather key metrics (P/E, EPS, dividend yield, book value)
4. Get 52-week range and year-to-date performance
5. Find recent news or major developments (Hebrew sources prioritized)
6. Present in concise summary format (bilingual if Hebrew query)

**Output Format:**
- Company/Fund description (1-2 sentences in appropriate language)
- Current price in ILS and trading metrics
- Key valuation metrics (table)
- Recent performance
- Notable recent news (if any)
- Dividend information (if applicable)

### 2. Fundamental Analysis

**When to Use:** User wants financial analysis, valuation assessment, or business evaluation for Israeli stock

**Steps:**
1. **Gather comprehensive financial data:**
   - Revenue, earnings, cash flow in ILS (3-5 year trends)
   - Balance sheet metrics (debt in ILS, cash, working capital)
   - Profitability metrics (margins, ROE, ROIC)
   - Dividend policy and history
   
2. **Read references/fundamental-analysis.md** for Israeli market context and analytical framework

3. **Read references/financial-metrics.md** for metric definitions, calculations, and Israeli-specific considerations

4. **Analyze business quality:**
   - Competitive advantages in Israeli/regional market
   - Management track record
   - Industry position
   - Regulatory environment (ISA, Bank of Israel if applicable)
   
5. **Perform valuation analysis:**
   - Calculate key ratios (P/E vs Israeli market average, P/B, EV/EBITDA)
   - Compare to historical averages
   - Compare to peer group (Israeli and regional)
   - Estimate fair value range in ILS
   
6. **Identify risks:**
   - Company-specific risks
   - Market/macro risks (Israel-specific: political, security, currency)
   - Red flags from financial data
   - Regulatory risks
   
7. **Generate output** following references/report-template.md structure (with Hebrew translation if appropriate)

**Critical Analyses:**
- Profitability trends (improving/declining margins in ILS)
- Cash flow quality (FCF vs earnings)
- Balance sheet strength (debt levels relative to EBITDA, liquidity)
- Growth sustainability
- Valuation vs Israeli peers and historical average
- Dividend sustainability and growth trajectory

### 3. Technical Analysis

**When to Use:** User asks for technical analysis, chart patterns, or trading signals for TASE security

**Steps:**
1. **Gather technical data:**
   - Current price in ILS and recent price action
   - Volume trends (in shares and ILS)
   - Moving averages (20-day, 50-day, 200-day)
   - Technical indicators (RSI, MACD, Bollinger Bands)
   
2. **Read references/technical-analysis.md** for indicator definitions, patterns, and Israeli market considerations

3. **Identify trend:**
   - Uptrend, downtrend, or sideways
   - Strength of trend relative to TA25 (Tel Aviv 25 Index)
   
4. **Locate support and resistance levels:**
   - Recent highs and lows in ILS
   - Moving average levels
   - Round numbers (psychological levels)
   
5. **Analyze indicators:**
   - RSI: Overbought (>70) or oversold (<30)
   - MACD: Crossovers and divergences
   - Volume: Confirmation or divergence
   - Bollinger Bands: Squeeze or expansion
   
6. **Identify chart patterns:**
   - Reversal patterns (head and shoulders, double top/bottom)
   - Continuation patterns (flags, triangles)
   
7. **Generate technical outlook:**
   - Current trend assessment
   - Key levels to watch (in ILS)
   - Risk/reward analysis
   - Short and medium-term outlook

**Interpretation Guidelines:**
- Confirm signals with multiple indicators
- Consider volume for validation
- Note divergences between price and indicators
- Always identify risk levels (stop-loss in ILS)
- Account for TASE trading hours (09:30-17:15 Israel time)

### 4. Comprehensive Investment Report

**When to Use:** User asks for detailed report, investment recommendation, or complete analysis of Israeli security

**Steps:**
1. **Perform data gathering** (as in Basic Info)

2. **Execute fundamental analysis** (follow workflow above)

3. **Execute technical analysis** (follow workflow above)

4. **Read references/report-template.md** for complete report structure

5. **Synthesize findings:**
   - Integrate fundamental and technical insights
   - Develop bull and bear cases
   - Assess risk/reward
   - Consider macro environment (Israel-specific factors)
   
6. **Generate recommendation:**
   - Buy/Hold/Sell rating
   - Target price in ILS with timeframe
   - Conviction level
   - Entry strategy
   - Dividend consideration (if applicable)
   
7. **Create formatted report** following template structure

**Report Must Include:**
- Executive summary with recommendation
- Company/Fund overview
- Investment thesis (bull and bear cases)
- Fundamental analysis section
- Technical analysis section
- Valuation analysis
- Risk assessment (including Israel-specific risks)
- Catalysts and timeline
- Dividend analysis (if applicable)
- Conclusion

## Stock Comparison Analysis

**When to Use:** User asks to compare two or more Israeli stocks (e.g., "compare Bank Leumi vs Bank Hapoalim")

**Steps:**
1. **Gather data for all securities:**
   - Follow data gathering steps for each ticker/identifier
   - Ensure comparable timeframes and all data in ILS
   
2. **Read references/fundamental-analysis.md** and references/financial-metrics.md

3. **Create side-by-side comparison:**
   - Business models comparison
   - Financial metrics table (all key ratios in ILS)
   - Valuation metrics table
   - Growth rates comparison
   - Profitability comparison
   - Balance sheet strength
   - Dividend yield comparison
   
4. **Identify relative strengths:**
   - Where each company excels
   - Quantified advantages
   - Sector positioning
   
5. **Technical comparison:**
   - Relative strength vs TA25
   - Momentum comparison
   - Which is in better technical position
   
6. **Generate recommendation:**
   - Which security is more attractive and why
   - Consider both fundamental and technical factors
   - Portfolio allocation suggestion
   - Risk-adjusted return assessment

**Output Format:** Follow "Comparison Report Structure" in references/report-template.md

## Language Support

This skill supports both Hebrew and English analysis:

**Hebrew Queries:**
- Respond primarily in Hebrew
- Use proper Hebrew financial terminology (e.g., "שווי שוק" for market cap, "דיבידנד" for dividend)
- Include both Hebrew and English company names for clarity
- Use Hebrew sources (Calcalist, TheMarker, Globes) for market context

**English Queries:**
- Respond in English
- May cite Hebrew sources but translate key findings
- Use English financial terminology

**Mixed Language:**
- If query mixes languages, respond in the language of the primary request
- Always clarify company/ticker names in both languages

## Output Guidelines

**General Principles:**
- Use tables for financial data and comparisons (easy to scan)
- Bold key metrics and findings
- Include data sources and dates
- Quantify whenever possible
- Present both bull and bear perspectives
- Be clear about assumptions and uncertainties
- Always use ILS for prices and financial metrics (unless conversion requested)

**Formatting:**
- **Headers** for clear section separation
- **Tables** for metrics, comparisons, historical data
- **Bullet points** for lists, factors, risks
- **Bold text** for key findings, important metrics
- **Percentages** for growth rates, returns, margins
- **Currency** formatted consistently (₪ for ILS, show "B" for billions, "M" for millions)

**Tone:**
- Objective and balanced
- Acknowledge uncertainty
- Support claims with data
- Avoid hyperbole
- Present risks clearly
- Consider Israeli market context

## Reference Files

Load these references as needed during analysis:

**references/technical-analysis.md**
- When: Performing technical analysis or interpreting indicators
- Contains: Indicator definitions, chart patterns, support/resistance concepts, TASE-specific analysis workflow, Hebrew terminology

**references/fundamental-analysis.md**
- When: Performing fundamental analysis or business evaluation
- Contains: Business quality assessment, Israeli market context, financial health analysis, valuation frameworks for Israeli companies, risk assessment, red flags, macro environment considerations

**references/financial-metrics.md**
- When: Need definitions or calculation methods for financial ratios
- Contains: All key metrics with formulas (profitability, valuation, growth, liquidity, leverage, efficiency, cash flow), Israeli market benchmarks, currency considerations

**references/report-template.md**
- When: Creating comprehensive report or comparison
- Contains: Complete report structure, formatting guidelines, section templates, comparison format, bilingual templates

## Example Queries

**Basic Info:**
- "מה המחיר הנוכחי של בנק לאומי?" (What's the current price of Bank Leumi?)
- "Give me key metrics for TASE"
- "טבע -개요 מהיר" (Quick overview of Teva)
- "Current data for ETF 510893"

**Fundamental:**
- "Analyze Bank Hapoalim financials"
- "האם אלביט סיסטמס יקרה מדי?" (Is Elbit Systems overvalued?)
- "Evaluate Discount Bank's business quality"
- "מה מצב ההוצאות של טבע?" (What's Teva's debt situation?)

**Technical:**
- "Technical analysis of ALRT"
- "Is DSCT oversold?"
- "Show me support levels for TASE"
- "What's the trend for PELEOT?"

**Comprehensive:**
- "Complete analysis of Bank Leumi"
- "Give me a full report on ELBIT"
- "Should I invest in Teva? Give me detailed analysis"

**Comparison:**
- "Compare Bank Leumi vs Bank Hapoalim"
- "Discount Bank vs Israel Discount Bank - which is better?"
- "Analyze ALRT vs DSCT"
