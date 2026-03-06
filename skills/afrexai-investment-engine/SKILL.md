---
name: Investment Analysis & Portfolio Management Engine
description: Complete investment analysis, portfolio construction, risk
  management, and trade execution methodology. Works across stocks, crypto,
  ETFs, bonds, and alternatives. Zero dependencies — pure agent sk...
---

# Investment Analysis & Portfolio Management Engine

Complete investment analysis, portfolio construction, risk management, and trade execution methodology. Works across stocks, crypto, ETFs, bonds, and alternatives. Zero dependencies — pure agent skill.

## Quick Health Check (/8)

Before any investment activity, score your current state:

| Signal | ✅ Healthy | ❌ Fix First |
|--------|-----------|-------------|
| Investment thesis documented | Written with edge + invalidation | "I think it'll go up" |
| Position sizing calculated | Kelly/fixed-fractional with max cap | "I'll put in $5K" |
| Stop-loss defined | Price or thesis invalidation trigger | No exit plan |
| Portfolio heat tracked | Total exposure known, <15% | Unknown aggregate risk |
| Asset correlation checked | No >40% correlated concentration | All tech / all crypto |
| Rebalance schedule set | Monthly or threshold-based | Never rebalanced |
| Tax impact considered | Harvesting losses, holding periods | Tax-blind trading |
| Performance tracked | Benchmarked vs buy-and-hold | "I think I'm up" |

Score /8. Below 5 = fix fundamentals before any new positions.

---

## Phase 1: Investment Thesis Development

Every position starts with a thesis. No thesis = no trade.

### Thesis Brief Template

```yaml
thesis:
  ticker: "AAPL"
  asset_class: "equity"  # equity | crypto | etf | bond | commodity | real_estate
  date: "2026-02-22"
  
  # THE EDGE — why does this opportunity exist?
  edge:
    type: "mispricing"  # mispricing | catalyst | trend | mean_reversion | structural
    description: "Market pricing in worst-case regulation; actual impact is 5-10% revenue, not 30%"
    why_others_miss_it: "Headline risk scaring generalists; specialists still buying"
    
  # THESIS STATEMENT (one sentence)
  thesis_statement: "AAPL is undervalued by 20% due to regulatory FUD; earnings growth will re-rate within 2 quarters"
  
  # TIMEFRAME
  timeframe:
    horizon: "3-6 months"
    catalyst_date: "2026-04-15"  # earnings, FDA, macro event
    catalyst_type: "earnings_beat"
    
  # BULL / BASE / BEAR
  scenarios:
    bull:
      probability: 30
      target_price: 245
      thesis: "Regulation light + Services acceleration"
    base:
      probability: 50
      target_price: 215
      thesis: "Regulation moderate, priced in by Q3"
    bear:
      probability: 20
      target_price: 165
      thesis: "Full regulatory impact + macro downturn"
      
  # EXPECTED VALUE
  # EV = (P_bull × R_bull) + (P_base × R_base) + (P_bear × R_bear)
  current_price: 190
  expected_value: 213.5  # (0.3×245 + 0.5×215 + 0.2×165)
  ev_vs_current: "+12.4%"
  
  # INVALIDATION — when you're WRONG
  invalidation:
    price_stop: 175  # -7.9% from entry
    thesis_stop: "Revenue decline >10% YoY in any segment"
    time_stop: "No catalyst by 2026-07-01"
    
  # CONVICTION (1-5)
  conviction: 4
  conviction_factors:
    - "3 independent data sources confirm undervaluation"
    - "Insider buying last 90 days"
    - "Valuation below 5Y average on EV/EBITDA"
```

### Edge Type Framework

| Edge Type | Description | Validation Method | Decay Rate |
|-----------|-------------|-------------------|------------|
| Mispricing | Market wrong on fundamentals | Comp analysis + model | Slow (months) |
| Catalyst | Known upcoming event | Calendar + probability | Fast (event-driven) |
| Trend | Momentum / technical | Price action + volume | Medium (weeks) |
| Mean Reversion | Extreme deviation from norm | Z-score + history | Medium |
| Structural | Market structure creates opportunity | Flow analysis | Slow |

### Thesis Quality Checklist

- [ ] Edge clearly articulated (not just "it's cheap")
- [ ] Bull/base/bear with probabilities summing to 100%
- [ ] Expected value positive vs current price
- [ ] At least 2 independent data sources
- [ ] Invalidation criteria defined (price + thesis + time)
- [ ] Timeframe realistic for the edge type
- [ ] Not just consensus view repackaged
- [ ] Considered "what if I'm wrong?"

---

## Phase 2: Fundamental Analysis

### Equity Analysis Framework

#### Valuation Metrics (collect all, weight by sector)

```yaml
valuation:
  # Price Multiples
  pe_ratio: null          # Price / Earnings (TTM)
  forward_pe: null        # Price / Forward Earnings
  peg_ratio: null         # PE / Earnings Growth Rate
  ps_ratio: null          # Price / Sales
  pb_ratio: null          # Price / Book
  ev_ebitda: null         # Enterprise Value / EBITDA
  ev_revenue: null        # Enterprise Value / Revenue
  fcf_yield: null         # Free Cash Flow / Market Cap
  
  # Compare to:
  sector_median: null
  historical_5y_avg: null
  historical_range: [null, null]  # [low, high]
  
  # Verdict
  valuation_score: null   # 1-10 (1=very expensive, 10=very cheap)
  relative_to_sector: null  # premium | inline | discount
```

#### Financial Health Scorecard

| Dimension | Metric | Healthy | Warning | Danger |
|-----------|--------|---------|---------|--------|
| Profitability | Gross Margin | >50% | 30-50% | <30% |
| Profitability | Net Margin | >15% | 5-15% | <5% |
| Profitability | ROE | >15% | 8-15% | <8% |
| Profitability | ROIC | >12% | 6-12% | <6% |
| Growth | Revenue YoY | >15% | 5-15% | <5% |
| Growth | EPS YoY | >10% | 0-10% | Declining |
| Growth | FCF Growth | >10% | 0-10% | Declining |
| Leverage | Debt/Equity | <0.5 | 0.5-1.5 | >1.5 |
| Leverage | Interest Coverage | >8x | 3-8x | <3x |
| Leverage | Net Debt/EBITDA | <2x | 2-4x | >4x |
| Liquidity | Current Ratio | >1.5 | 1-1.5 | <1 |
| Liquidity | Quick Ratio | >1.0 | 0.5-1 | <0.5 |
| Efficiency | Asset Turnover | >0.8 | 0.4-0.8 | <0.4 |
| Efficiency | Inventory Days | <60 | 60-120 | >120 |
| Quality | FCF/Net Income | >80% | 50-80% | <50% |
| Quality | Accruals Ratio | <5% | 5-10% | >10% |

Score each dimension 1-3. Total /48. Above 36 = strong. Below 24 = avoid.

#### Moat Assessment (0-25 points)

| Moat Source | Score 0-5 | Evidence Required |
|-------------|-----------|-------------------|
| Network Effects | | Users increase value for other users |
| Switching Costs | | Painful to leave (data lock-in, integrations) |
| Cost Advantages | | Structural cost below competitors |
| Intangible Assets | | Brand, patents, regulatory licenses |
| Efficient Scale | | Market only supports limited competitors |

Score /25. Above 15 = wide moat. 8-15 = narrow. Below 8 = no moat.

### Crypto Analysis Framework

```yaml
crypto_analysis:
  # Network Fundamentals
  network:
    daily_active_addresses: null
    transaction_volume_24h: null
    hash_rate_trend: null        # BTC/PoW
    staking_ratio: null          # PoS chains
    developer_activity: null     # GitHub commits 90d
    tvl: null                    # DeFi protocols
    tvl_trend_30d: null
    
  # Tokenomics
  tokenomics:
    supply_schedule: null        # inflationary | deflationary | fixed
    circulating_vs_total: null   # % circulating
    unlock_schedule: null        # upcoming unlocks
    concentration: null          # top 10 holders %
    
  # On-Chain Signals
  on_chain:
    exchange_reserves_trend: null  # decreasing = bullish
    whale_accumulation: null       # large wallet changes
    realized_profit_loss: null     # NUPL
    mvrv_ratio: null               # Market Value / Realized Value
    
  # Market Structure
  market:
    funding_rate: null           # perpetuals funding
    open_interest_trend: null
    spot_vs_derivatives_volume: null
    correlation_to_btc: null
    correlation_to_sp500: null
```

### Crypto Valuation Methods

| Method | Best For | Formula |
|--------|----------|---------|
| Stock-to-Flow | BTC | Price = 0.4 × S2F^3 (check vs actual) |
| NVT Ratio | L1 chains | Network Value / Daily Transaction Value |
| TVL Ratio | DeFi | Market Cap / TVL (below 1 = undervalued) |
| Fee Revenue Multiple | Revenue-generating | MC / Annualized Fees |
| Metcalfe's Law | Network tokens | Value ∝ n² (active addresses) |

---

## Phase 3: Technical Analysis

### Price Action Framework

```yaml
technical_analysis:
  ticker: "BTC-USD"
  timeframe: "daily"
  date: "2026-02-22"
  
  # TREND
  trend:
    primary: "uptrend"    # uptrend | downtrend | range
    higher_highs: true
    higher_lows: true
    above_200ma: true
    above_50ma: true
    ma_alignment: "bullish"  # 20 > 50 > 200 = bullish
    
  # KEY LEVELS
  levels:
    resistance: [105000, 110000, 120000]
    support: [95000, 88000, 80000]
    current_price: 98500
    distance_to_resistance: "+6.6%"
    distance_to_support: "-3.6%"
    
  # MOMENTUM
  momentum:
    rsi_14: 58           # <30 oversold, >70 overbought
    rsi_divergence: null # bullish_div | bearish_div | none
    macd_signal: "bullish"  # bullish | bearish | neutral
    macd_histogram_trend: "increasing"
    
  # VOLUME
  volume:
    vs_20d_avg: "+15%"
    trend: "increasing_on_up_days"  # confirms trend
    
  # PATTERN
  pattern:
    current: "ascending_triangle"
    reliability: "high"
    target: 112000
    invalidation: 93000
```

### Signal Scoring Matrix

| Factor | Bullish (+) | Neutral (0) | Bearish (-) |
|--------|-------------|-------------|-------------|
| Trend (weight 3x) | Above 200MA, higher highs | Ranging | Below 200MA, lower lows |
| Momentum (weight 2x) | RSI 40-60 rising, MACD bull cross | RSI 45-55 flat | RSI >75 or bearish div |
| Volume (weight 2x) | Rising on up moves | Average | Rising on down moves |
| Support/Resistance (weight 1x) | Near strong support | Mid-range | Near strong resistance |
| Pattern (weight 1x) | Bullish continuation | No pattern | Bearish reversal |

Score -9 to +9. Above +5 = strong buy signal. Below -5 = strong sell signal.

---

## Phase 4: Position Sizing & Risk Management

### Position Sizing Rules (MANDATORY)

```yaml
risk_rules:
  # Per-Trade Risk
  max_risk_per_trade: 2%       # of total equity
  max_risk_aggressive: 3%      # only with 5/5 conviction
  
  # Portfolio Heat
  max_portfolio_heat: 15%      # total risk across all positions
  max_correlated_exposure: 25% # in correlated assets
  max_single_position: 10%     # of total equity
  
  # Position Size Formula
  # Position Size = (Account × Risk%) / (Entry - Stop Loss)
  # Example: ($100K × 2%) / ($190 - $175) = $2,000 / $15 = 133 shares
  
  # Kelly Criterion (optional, aggressive)
  # f* = (bp - q) / b
  # b = win/loss ratio, p = win probability, q = 1-p
  # ALWAYS use Half-Kelly or Quarter-Kelly (full Kelly = too aggressive)
```

### Position Size Calculator

```
Account Equity:     $___________
Risk Per Trade:     ___% (max 2%)
Dollar Risk:        $___________  (equity × risk%)
Entry Price:        $___________
Stop Loss Price:    $___________
Risk Per Share:     $___________  (entry - stop)
Position Size:      ___________ shares (dollar risk / risk per share)
Position Value:     $___________  (shares × entry)
Portfolio Weight:   ___%          (position value / equity)

CHECK: Portfolio weight < 10%?  ☐ Yes ☐ No (reduce if no)
CHECK: Portfolio heat < 15%?    ☐ Yes ☐ No (reduce if no)
CHECK: Correlated exposure ok?  ☐ Yes ☐ No (reduce if no)
```

### Stop-Loss Decision Tree

```
Is this a TREND trade?
├── YES → Trailing stop below swing low (ATR-based: 2× ATR)
│         Initial stop: Below last higher low
│         Trail: Move stop to below each new higher low
│
└── NO → Is this a CATALYST trade?
    ├── YES → Time-based + price stop
    │         Price: Below pre-catalyst support
    │         Time: Close if no move within 2 days post-catalyst
    │
    └── Is this a VALUE trade?
        ├── YES → Thesis invalidation stop
        │         Price: Below bear case scenario price
        │         Thesis: Close if fundamental thesis breaks
        │         Time: Close if no re-rating in stated timeframe
        │
        └── MEAN REVERSION → Tight stop
            Price: If moves further from mean (wider Z-score)
            Target: Mean / fair value level
```

### Risk Management Hard Rules

1. **Never average down without a plan** — Adding to losers kills accounts. Only add if: thesis intact AND price at predetermined add level AND total position still within limits
2. **Cut losses fast, let winners run** — Asymmetric payoff is the goal. 1:3 risk/reward minimum
3. **No revenge trading** — After a loss, wait 24 hours before next trade
4. **Daily loss limit** — Stop trading for the day after -3% account drawdown
5. **Weekly loss limit** — Reduce position sizes by 50% after -5% weekly drawdown
6. **Monthly loss limit** — Go to cash if -10% monthly drawdown. Review all positions.
7. **Correlation check** — Before every new position, check correlation to existing holdings
8. **Black swan rule** — If any asset moves >15% in 24h, review ALL positions immediately

---

## Phase 5: Portfolio Construction

### Asset Allocation Framework

```yaml
portfolio:
  name: "Growth + Income"
  target_allocation:
    # Core (60-70% — low turnover)
    core:
      us_large_cap: 25%      # S&P 500 / quality growth
      international: 10%      # Developed markets
      fixed_income: 15%       # Bonds / treasuries
      bitcoin: 10%            # Digital gold thesis
      real_estate: 5%         # REITs
      
    # Satellite (20-30% — active management)
    satellite:
      growth_stocks: 15%      # Individual stock picks
      crypto_alts: 5%         # L1s, DeFi
      thematic: 5%            # AI, clean energy, etc.
      
    # Cash (5-15%)
    cash: 10%                 # Dry powder for opportunities
    
  # Rebalance Rules
  rebalance:
    method: "threshold"       # calendar | threshold | hybrid
    threshold: 5%             # Rebalance when drift >5% from target
    calendar_check: "monthly" # Review allocations monthly
    tax_aware: true           # Use new contributions to rebalance first
```

### Portfolio Models by Risk Profile

| Profile | Stocks | Bonds | Crypto | Alts | Cash | Expected Return | Max Drawdown |
|---------|--------|-------|--------|------|------|----------------|--------------|
| Conservative | 30% | 40% | 5% | 10% | 15% | 6-8% | -15% |
| Balanced | 50% | 20% | 10% | 10% | 10% | 8-12% | -25% |
| Growth | 60% | 10% | 15% | 10% | 5% | 12-18% | -35% |
| Aggressive | 50% | 0% | 30% | 15% | 5% | 15-25% | -50% |
| Degen | 20% | 0% | 50% | 25% | 5% | 20-40%+ | -70%+ |

### Correlation Matrix Template

Track correlations between holdings. Target: no two positions with >0.7 correlation exceeding 20% combined weight.

```
         SPY    BTC    ETH    AAPL   MSFT   GLD    TLT
SPY      1.00
BTC      0.35   1.00
ETH      0.30   0.85   1.00
AAPL     0.82   0.25   0.20   1.00
MSFT     0.85   0.28   0.22   0.78   1.00
GLD     -0.10  -0.05  -0.08  -0.12  -0.10   1.00
TLT     -0.35  -0.15  -0.12  -0.30  -0.32   0.40   1.00
```

---

## Phase 6: Trade Execution

### Trade Journal Template

```yaml
trade:
  id: "T-2026-042"
  date_opened: "2026-02-22"
  date_closed: null
  
  # WHAT
  ticker: "BTC-USD"
  direction: "long"
  asset_class: "crypto"
  
  # SIZING
  entry_price: 98500
  position_size: 0.15  # BTC
  position_value: 14775
  portfolio_weight: "8.2%"
  
  # RISK
  stop_loss: 93000
  risk_amount: 825   # (98500-93000) × 0.15
  risk_percent: "0.82%"  # of portfolio
  
  # TARGETS
  target_1: 105000   # 50% of position
  target_2: 115000   # 30% of position
  target_3: 130000   # 20% of position (runner)
  risk_reward: "1:3.8"  # avg target vs risk
  
  # THESIS
  thesis: "BTC consolidating above 200MA, halving supply reduction, ETF inflows accelerating"
  edge_type: "trend + structural"
  conviction: 4
  
  # EXECUTION
  entry_type: "limit"  # market | limit | scaled
  scale_plan: null     # or: [{"price": 97000, "size": "50%"}, {"price": 95000, "size": "50%"}]
  
  # RESULT (fill on close)
  exit_price: null
  exit_reason: null    # target_hit | stop_hit | thesis_invalidated | time_stop | manual
  pnl_dollar: null
  pnl_percent: null
  r_multiple: null     # PnL / initial risk
  
  # REVIEW
  followed_plan: null  # yes | partially | no
  lessons: null
  mistakes: null
  grade: null          # A-F
```

### Execution Checklist (Before EVERY Trade)

- [ ] Thesis documented with edge, invalidation, timeframe
- [ ] Position size calculated (≤2% risk, ≤10% portfolio weight)
- [ ] Stop-loss set (price + thesis + time)
- [ ] At least 2 take-profit targets defined
- [ ] Risk/reward ≥1:2 (preferably 1:3+)
- [ ] Portfolio heat check (total risk <15%)
- [ ] Correlation check (not adding to concentrated exposure)
- [ ] No emotional driver (revenge, FOMO, boredom)
- [ ] Checked economic calendar (no surprise events imminent)
- [ ] Entry type decided (market/limit/scaled)

### Order Types Decision

| Situation | Order Type | Why |
|-----------|-----------|-----|
| Strong conviction, want in now | Market | Speed over price |
| Good setup, not urgent | Limit at support | Better entry |
| High-conviction, want scale in | Scaled limits (3 levels) | Average entry, reduce timing risk |
| Breakout trade | Stop-limit above resistance | Only enter if breakout confirms |
| Catalyst trade | Limit pre-catalyst | Position before event |

---

## Phase 7: Performance Tracking

### Daily Dashboard

```yaml
daily_dashboard:
  date: "2026-02-22"
  
  # PORTFOLIO SNAPSHOT
  portfolio:
    total_equity: null
    daily_pnl: null
    daily_pnl_percent: null
    weekly_pnl: null
    monthly_pnl: null
    ytd_pnl: null
    
  # POSITIONS
  open_positions: 0
  portfolio_heat: "0%"  # sum of all position risks
  cash_percent: "100%"
  
  # BENCHMARK
  benchmark:
    sp500_ytd: null
    btc_ytd: null
    portfolio_vs_sp500: null
    portfolio_vs_btc: null
    
  # ACTIVITY
  trades_today: 0
  alerts_triggered: []
```

### Performance Metrics (Track Weekly)

| Metric | Formula | Target |
|--------|---------|--------|
| Win Rate | Winning trades / Total trades | >50% |
| Average R | Average R-multiple of all trades | >1.5R |
| Profit Factor | Gross profit / Gross loss | >2.0 |
| Expectancy | (Win% × Avg Win) - (Loss% × Avg Loss) | Positive |
| Max Drawdown | Peak to trough decline | <-15% |
| Sharpe Ratio | (Return - RFR) / Std Dev | >1.5 |
| Sortino Ratio | (Return - RFR) / Downside Dev | >2.0 |
| Calmar Ratio | Annual Return / Max Drawdown | >1.0 |
| Recovery Factor | Net Profit / Max Drawdown | >3.0 |

### Monthly Review Template

```yaml
monthly_review:
  month: "2026-02"
  
  # PERFORMANCE
  portfolio_return: null
  benchmark_return: null  # vs S&P 500
  alpha: null             # portfolio - benchmark
  
  # TRADING STATS
  total_trades: 0
  winning_trades: 0
  losing_trades: 0
  win_rate: null
  average_winner: null
  average_loser: null
  largest_winner: null
  largest_loser: null
  profit_factor: null
  
  # RISK STATS
  max_drawdown: null
  avg_portfolio_heat: null
  risk_rule_violations: 0
  
  # BEHAVIOR ANALYSIS
  followed_plan_rate: null    # % of trades that followed the plan
  emotional_trades: 0          # trades driven by FOMO/revenge/boredom
  early_exits: 0               # cut winners short
  late_exits: 0                # held losers too long
  
  # TOP 3 LESSONS
  lessons:
    - null
    - null
    - null
    
  # ADJUSTMENTS FOR NEXT MONTH
  adjustments:
    - null
```

---

## Phase 8: Market Regime Detection

### Regime Framework

| Regime | Characteristics | Strategy | Position Size |
|--------|----------------|----------|---------------|
| Bull Trend | Rising 200MA, breadth >60%, VIX <20 | Trend following, buy dips | Full size |
| Bear Trend | Falling 200MA, breadth <40%, VIX >30 | Short / inverse, raise cash | Half size |
| Range/Chop | Flat 200MA, breadth 40-60% | Mean reversion, sell premium | Quarter size |
| High Vol | VIX >35, large daily swings | Reduce exposure, hedge | Minimum size |
| Euphoria | VIX <12, extreme bullish sentiment | Take profits, hedge | Scale down |
| Panic | VIX >50, capitulation signals | Accumulate quality | Scale in slowly |

### Macro Checklist (Weekly)

- [ ] Fed funds rate / next meeting: ___
- [ ] US 10Y yield trend: ___
- [ ] Dollar (DXY) trend: ___
- [ ] VIX level: ___
- [ ] Credit spreads: ___ (tightening/widening)
- [ ] Yield curve: ___ (inverted/flat/steep)
- [ ] Leading indicators: ___ (improving/declining)
- [ ] Global liquidity trend: ___ (expanding/contracting)
- [ ] Sector rotation: ___ (risk-on/risk-off)
- [ ] Crypto market cap trend: ___

### Sentiment Indicators

| Indicator | Extreme Fear (Buy) | Neutral | Extreme Greed (Sell) |
|-----------|-------------------|---------|---------------------|
| CNN Fear & Greed | <20 | 40-60 | >80 |
| AAII Bull-Bear | >-30% spread | ±10% | >+30% spread |
| Put/Call Ratio | >1.2 | 0.7-0.9 | <0.5 |
| VIX Term Structure | Backwardation | Flat | Steep contango |
| Crypto Fear & Greed | <15 | 40-60 | >85 |
| BTC Funding Rates | Deeply negative | Neutral | >0.05% |

---

## Phase 9: Dividend & Income Analysis

### Dividend Quality Score (0-100)

| Factor | Weight | Scoring |
|--------|--------|---------|
| Yield vs Sector | 15 | At/above median = 15, below = proportional |
| Payout Ratio | 20 | <50% = 20, 50-75% = 15, 75-100% = 5, >100% = 0 |
| Growth Rate (5Y CAGR) | 20 | >10% = 20, 5-10% = 15, 0-5% = 10, declining = 0 |
| Consecutive Years | 15 | >25y = 15 (Aristocrat), 10-25 = 10, 5-10 = 5, <5 = 0 |
| FCF Coverage | 15 | FCF/Div >1.5 = 15, 1-1.5 = 10, <1 = 0 |
| Debt/EBITDA | 15 | <2 = 15, 2-4 = 10, >4 = 5 |

Score /100. Above 75 = excellent income pick. Below 40 = dividend at risk.

### Income Portfolio Construction

- **Core income** (60%): Dividend Aristocrats, quality REITs, investment-grade bonds
- **Growth income** (25%): Dividend growers (low yield, high growth rate)
- **High yield** (15%): Higher risk, higher yield (junk bonds, BDCs, covered calls)
- **Yield target**: 4-6% blended, growing 5-8% annually

---

## Phase 10: Tax Optimization

### Tax-Loss Harvesting Rules

1. **When**: Position down >10% from cost basis AND held <12 months
2. **How**: Sell the position, immediately buy a correlated (not substantially identical) replacement
3. **Wash sale rule**: Cannot buy back the same security within 30 days (before or after)
4. **Replacement examples**: SPY→VOO, AAPL→QQQ, BTC spot→BTC futures ETF
5. **Track**: Cumulative harvested losses, offset against gains + $3K income deduction

### Holding Period Optimization

| Holding Period | Tax Rate (US) | Strategy |
|----------------|--------------|----------|
| <1 year | Ordinary income (up to 37%) | Only for high-conviction short-term trades |
| >1 year | Long-term CG (0/15/20%) | Default for all positions when possible |
| >5 years (QOZ) | Reduced + deferred | Qualified Opportunity Zone investments |

### Tax-Efficient Account Allocation

| Account Type | Best For | Why |
|-------------|----------|-----|
| Taxable | Long-term holds, tax-loss harvesting | Capital gains treatment |
| Traditional IRA/401k | Bonds, REITs, high-dividend | Defer high-tax income |
| Roth IRA | Highest growth potential | Tax-free growth |
| HSA | Aggressive growth | Triple tax advantage |

---

## Phase 11: Screening & Idea Generation

### Stock Screener Criteria Templates

**Value Screen:**
- P/E < sector median
- P/B < 1.5
- Debt/Equity < 0.5
- ROE > 12%
- FCF positive 5 consecutive years
- Insider buying last 90 days

**Growth Screen:**
- Revenue growth > 20% YoY
- EPS growth > 15% YoY
- Gross margin > 50%
- Net retention > 110% (SaaS)
- TAM > $10B

**Dividend Screen:**
- Dividend yield > 3%
- Payout ratio < 60%
- Dividend growth > 5% CAGR (5Y)
- Consecutive increases > 10 years
- Debt/EBITDA < 3

**Crypto Screen:**
- Market cap > $1B (avoid micro-caps)
- Daily volume > $50M
- Active development (GitHub commits)
- Not >90% held by top 10 wallets
- Clear revenue model or adoption metrics

### Research Sources (No API Required)

| Source | URL | Best For |
|--------|-----|----------|
| Yahoo Finance | finance.yahoo.com | Fundamentals, quotes |
| Finviz | finviz.com | Screening, heatmaps |
| Macrotrends | macrotrends.net | Historical financials |
| CoinGecko | coingecko.com | Crypto data |
| DeFiLlama | defillama.com | DeFi TVL, yields |
| FRED | fred.stlouisfed.org | Macro data |
| TradingView | tradingview.com | Charts, technicals |
| SEC EDGAR | sec.gov/edgar | Filings, insider trades |
| Glassnode | glassnode.com | On-chain data |
| Fear & Greed | alternative.me | Crypto sentiment |

---

## Phase 12: Advanced Strategies

### Options Basics (for hedging)

| Strategy | When | Risk | Reward |
|----------|------|------|--------|
| Protective Put | Own stock, want downside protection | Premium paid | Unlimited upside, limited downside |
| Covered Call | Own stock, willing to cap upside | Capped gains | Premium income |
| Cash-Secured Put | Want to buy at lower price | Must buy at strike | Premium + lower entry |
| Collar | Want protection, willing to cap upside | Capped both ways | Low/no cost protection |

### DCA (Dollar Cost Averaging) Framework

```yaml
dca_plan:
  asset: "BTC"
  frequency: "weekly"           # daily | weekly | biweekly | monthly
  amount: 250                   # per purchase
  day: "Monday"                 # specific day
  duration: "indefinite"        # or end date
  
  # SMART DCA (optional — buy more when cheap)
  smart_dca:
    enabled: true
    base_amount: 250
    multiplier_rules:
      - condition: "price < 200MA"
        multiplier: 1.5          # buy 50% more
      - condition: "RSI < 30"
        multiplier: 2.0          # double buy
      - condition: "price > 200MA × 1.5"
        multiplier: 0.5          # buy less in euphoria
```

### Rebalancing Decision Tree

```
Is any allocation >5% from target?
├── NO → No action needed. Check again next month.
│
└── YES → Is it a tax-advantaged account?
    ├── YES → Rebalance by selling overweight, buying underweight
    │
    └── NO (taxable) → Can you rebalance with new contributions?
        ├── YES → Direct new money to underweight positions
        │
        └── NO → Are there tax losses to harvest?
            ├── YES → Sell losers (harvest), redirect to underweight
            │
            └── NO → Is the drift >10%?
                ├── YES → Rebalance (accept tax hit for risk control)
                └── NO → Wait for next contribution or year-end
```

---

## Investor Psychology Rules

### 10 Cognitive Biases That Kill Returns

| Bias | Trap | Defense |
|------|------|---------|
| Loss Aversion | Holding losers, cutting winners | Pre-set stops, mechanical exits |
| Confirmation Bias | Only seeing data that supports thesis | Actively seek disconfirming evidence |
| Recency Bias | Extrapolating recent performance | Look at full cycle data (10+ years) |
| Anchoring | Fixating on purchase price | Focus on current value vs alternatives |
| FOMO | Chasing after 50%+ move | Stick to your screener, your edge |
| Overconfidence | Too large positions after wins | Fixed position sizing rules |
| Disposition Effect | Selling winners too early | Trailing stops, let runners run |
| Herding | Buying because everyone is | Contrarian checkpoints |
| Sunk Cost | "I've held this long, can't sell now" | Would you buy this TODAY at this price? |
| Hindsight | "I knew it all along" | Review trade journal honestly |

### Trading Psychology Checklist (Daily)

- [ ] Am I calm? (no anger, fear, or euphoria)
- [ ] Am I following my system? (not improvising)
- [ ] Am I within risk limits? (checked portfolio heat)
- [ ] Am I trading my plan? (not reacting to noise)
- [ ] Have I done my analysis? (not trading on tips)

---

## Quality Scoring (0-100)

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Thesis Quality | 20 | Clear edge, documented invalidation, realistic timeframe |
| Risk Management | 25 | Position sizing, stops, portfolio heat, correlation |
| Analysis Depth | 15 | Fundamental + technical + macro considered |
| Execution | 15 | Entry/exit discipline, order type selection, patience |
| Record Keeping | 10 | Trade journal, performance metrics, monthly reviews |
| Psychology | 10 | Emotional control, bias awareness, plan adherence |
| Tax Efficiency | 5 | Harvesting, account allocation, holding periods |

Score /100. Above 80 = professional-grade process. Below 50 = gambling.

---

## Natural Language Commands

| Command | Action |
|---------|--------|
| "Analyze [ticker]" | Full fundamental + technical analysis |
| "Compare [ticker1] vs [ticker2]" | Side-by-side comparison |
| "Build thesis for [ticker]" | Generate thesis brief template |
| "Size position for [ticker] at [price]" | Calculate position size with risk |
| "Portfolio health check" | Score current portfolio /8 |
| "Monthly review" | Generate performance review template |
| "Screen for [value/growth/dividend/crypto]" | Apply screening criteria |
| "What's the market regime?" | Assess current macro environment |
| "Tax harvest opportunities" | Identify positions for loss harvesting |
| "DCA plan for [asset]" | Generate dollar cost averaging plan |
| "Dividend score for [ticker]" | Run dividend quality analysis |
| "Risk report" | Portfolio heat, correlations, exposure summary |

---

*Built by AfrexAI — turning market noise into signal.* 🖤💛
