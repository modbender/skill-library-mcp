---
name: agenthc-market-intelligence
description: Real-time stock market data and trading intelligence API. 85 intelligence modules, 40 encoded intelligence skills, and 7 named alert packages — equities, bonds, crypto, bitcoin, macro economics, Fed policy, treasury yields, VIX, options flow, sector rotation, regime detection, and technical analysis. Finance data for AI agents with Bitcoin Lightning micropayments.
homepage: https://api.traderhc.com/docs
metadata:
  clawdbot:
    emoji: "📊"
    requires:
      env: ["AGENTHC_API_KEY"]
      bins: ["curl", "jq", "python3"]
    primaryEnv: "AGENTHC_API_KEY"
---

# Stock Market Intelligence

Institutional-grade market intelligence API for AI agents. 85 intelligence modules, 40 encoded intelligence skills, and 7 named alert packages covering equities, bonds, crypto, macro, Fed, liquidity, regime detection, alpha signals, options flow, and more. Free tier includes regime detection with transition probabilities. Real-time alerts via webhook and Discord. Bitcoin Lightning micropayments. Built by @traderhc.

## Setup

### For AI Agents (copy-paste, zero friction)

```bash
export AGENTHC_API_KEY=$(curl -s -X POST "https://api.traderhc.com/api/v1/agents/register" \
  -H "Content-Type: application/json" \
  -d '{"name": "MyAgent"}' | jq -r '.api_key')
```

That's it. One command. Free, no KYC, no credit card. Now query any free module:

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/market_intelligence" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### For Humans (interactive setup)

```bash
bash scripts/setup.sh
```

Walks you through registration and prints your API key.

### Non-Interactive (CI/scripts)

```bash
export AGENTHC_API_KEY=$(bash scripts/setup.sh --auto)
```

## Free Modules (no payment required)

### Market Intelligence
Real-time market snapshot with institutional-grade regime detection. Includes S&P 500, VIX, treasury yields, DXY, commodities, Fear & Greed, and the full regime story — which of 12 market regimes we're in, confidence score, what's driving it, which regime is most likely next, and transition probabilities.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/market_intelligence" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '{regime: .data.regime, confidence: .data.regime_confidence, signals: .data.regime_signals, next_likely: .data.regime_next_most_likely, transition_gap: .data.regime_transition_gap, implications: .data.regime_implications, vix: .data.vix, fear_greed: .data.fear_greed_index}'
```

Example response:
```json
{
  "regime": "goldilocks",
  "confidence": 0.473,
  "signals": ["Tight HY spreads", "ISM at 51.0 - moderate expansion"],
  "next_likely": "recovery",
  "transition_gap": 2.8,
  "implications": ["Reflation (25% probability)", "Melt Up (20% probability)", "Growth Scare (15% probability)"],
  "vix": 19.09,
  "fear_greed": 69
}
```

### Educational Content
Trading concepts, historical lessons, and market psychology frameworks.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/educational_content" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Polymarket Intelligence
Fed/FOMC prediction markets, recession odds, crypto price predictions, political/regulatory odds.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/polymarket_intelligence" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### VIX Regime Intelligence
Historically-calibrated VIX regime classification (7 levels: ultra low → crisis) with 30-day forward SPX return expectations, mean-reversion probability, and vol-selling opportunity detection. Calibrated on 1990-2024 CBOE data.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/vix_regime_intelligence" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

## Premium Modules (100 sats/query)

These require Premium tier. Upgrade with Lightning payment or use L402 per-request payment.

### Technical Analysis
RSI, MACD, Bollinger Bands, support/resistance, volume analysis for any ticker.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/technical_analysis?ticker=AAPL" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Bond Intelligence
Treasury yields, yield curve dynamics, credit spreads, duration risk.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/bond_intelligence" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Fed Intelligence
Fed balance sheet, FOMC calendar, ISM PMI, yield curve analysis, RRP/repo, liquidity trends.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/fed_intelligence" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Macro Intelligence
CPI, PCE, NFP, unemployment, M2, credit spreads, ISM Services, consumer sentiment, housing.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/macro_intelligence" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Correlation Tracker
18+ cross-market correlation pairs with anomaly detection and regime classification.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/correlation_tracker" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Volatility Analyzer
VIX regime classification, term structure, VVIX, implied vs realized vol.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/volatility_analyzer" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Volatility Surface
VIX ecosystem (VIX, VIX9D, VIX3M, VIX6M, VVIX), term structure, skew analysis, vol regime detection.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/volatility_surface" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Crypto Intelligence
Bitcoin, Ethereum, BTC dominance, halving cycle, alt season detection, crypto Fear & Greed.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/crypto_intelligence" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Options Intelligence
Options open interest, volume, gamma exposure from OCC public data (T+1).

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/options_intelligence" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### CME FedWatch
Fed rate probability expectations from CME FedWatch proxy.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/cme_fedwatch" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

## Institutional Modules (500 sats/query)

### Alpha Signals
Systematic multi-factor signal composite: momentum, mean reversion, carry, value, volatility, flow, macro.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/alpha_signals" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Regime Engine
12 market regimes with transition probabilities, leading indicators, historical analogues.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/regime_engine" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Tail Risk Engine
Crisis detection with 12 crisis types, early warning indicators, historical playbooks, composite tail risk score.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/tail_risk_engine" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Liquidity Intelligence
Fed net liquidity (Balance Sheet - TGA - RRP), liquidity regime, bank stress signals.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/liquidity_intelligence" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Credit Cycle
HY/IG/BBB/CCC spreads, lending standards, default indicators, credit cycle phase, financial conditions.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/credit_cycle" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Institutional Positioning
CFTC COT data, AAII sentiment, NAAIM exposure, put/call ratios, crowded trade detection.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/institutional_positioning" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

## Agent-Optimized Format

For AI agents, use `format=agent` to get actionable signals with direction, confidence, urgency, and delta tracking:

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/market_intelligence?format=agent" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.signals'
```

Response includes:
- `signals.direction` — bullish/bearish/neutral/mixed
- `signals.confidence` — 0.0 to 1.0
- `signals.urgency` — low/medium/high/critical
- `signals.actionable` — true if action recommended
- `suggested_actions` — related modules to query next
- `delta` — what changed since your last query

## Compact Format (Token-Efficient)

Use `format=compact` for 60% fewer tokens in your context window:

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/market_intelligence?format=compact" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.'
```

## Batch Queries (Premium+)

Query multiple modules in one request:

```bash
curl -s -X POST "https://api.traderhc.com/api/v1/intelligence/batch" \
  -H "X-API-Key: $AGENTHC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"modules": ["market_intelligence", "bond_intelligence", "fed_intelligence"]}' | jq '.'
```

## Alert Packages

Named, curated alert products that deliver enriched market intelligence via **webhook** (AI agents) or **Discord** (human traders). Each alert includes signal data, regime context, positioning implications, affected tickers, and what to watch next. All 7 packages are live with 9 independent event scanners running every 120 seconds.

### List Available Packages

```bash
curl -s "https://api.traderhc.com/api/v1/alert-packages" | jq '.packages'
```

### Subscribe to a Package

```bash
# Webhook delivery (for AI agents)
curl -s -X POST "https://api.traderhc.com/api/v1/alert-packages/regime_shift/subscribe" \
  -H "X-API-Key: $AGENTHC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"delivery_channels": ["webhook"], "callback_url": "https://mybot.example.com/alerts"}' | jq '.'

# Discord delivery (for human traders)
curl -s -X POST "https://api.traderhc.com/api/v1/alert-packages/volatility/subscribe" \
  -H "X-API-Key: $AGENTHC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"delivery_channels": ["discord"], "discord_webhook_url": "https://discord.com/api/webhooks/..."}' | jq '.'
```

### Available Packages

| Package | Tier | Price | Triggers On |
|---------|------|-------|-------------|
| **Regime Shift Alerts** | Premium | 25K sats/mo | Market regime transitions (12 states) |
| **Tail Risk Alerts** | Institutional | 100K sats/mo | Crisis detection (score 0-100, 12 crisis types) |
| **Volatility Alerts** | Premium | 25K sats/mo | VIX spikes, vol regime changes, term structure |
| **Credit Cycle Alerts** | Premium | 25K sats/mo | Credit spread blowouts, cycle phase shifts, stress |
| **Liquidity Regime Alerts** | Institutional | 100K sats/mo | Fed net liquidity regime shifts |
| **Cross-Market Alerts** | Premium | 25K sats/mo | Correlation breaks, alpha signal flips |
| **Smart Money Alerts** | Institutional | 100K sats/mo | Smart vs dumb money divergence extremes |

### Alert Delivery

Every alert is enriched with:
- **Signal data** — raw trigger values (VIX level, regime name, score, etc.)
- **Regime context** — current market regime from the regime engine
- **Implications** — 3-4 actionable positioning recommendations
- **Affected tickers** — relevant instruments ($SPY, $VIX, $TLT, etc.)
- **What to watch** — key levels and events to monitor next
- **Related signals** — insights from encoded intelligence skills

Delivery channels:
- **Webhook** — HMAC-SHA256 signed JSON POST to your callback URL
- **Discord** — Rich embeds with urgency color-coding (red/orange/yellow/blue)
- **SSE** — Server-Sent Events stream for real-time push

### Discord Channel

Join **#agenthc-market-alerts** for live alert demos.

## Real-Time Events (Webhooks)

Subscribe to 20+ market event types via webhooks with HMAC-SHA256 signatures:

- Regime changes, VIX spikes, flash crashes
- Correlation breaks, credit stress spikes
- Alpha signal flips, tail risk alerts
- Breaking news, unusual options activity
- Fed rate probability shifts

## Lightning Payment (L402)

For per-request payment without registration:

1. Request a premium endpoint without auth
2. Receive 402 response with BOLT11 Lightning invoice + macaroon
3. Pay the invoice (any Lightning wallet)
4. Re-request with `Authorization: L402 <macaroon>:<preimage>`
5. Token valid for 24 hours — reuse across requests

## MCP Integration

Connect via Model Context Protocol (streamable-http transport):

```
Endpoint: https://api.traderhc.com/mcp
Protocol: 2025-03-26
Tools: 73
```

## All 85 Modules

### Base Intelligence Modules (45)

| Module | Tier | Description |
|--------|------|-------------|
| market_intelligence | Free | Market snapshot, regime detection (12 states), confidence, transition probabilities, Fear & Greed |
| educational_content | Free | Trading concepts, historical lessons |
| polymarket_intelligence | Free | Prediction market odds |
| technical_analysis | Premium | TA for any ticker (RSI, MACD, etc.) |
| economic_calendar | Premium | Economic events, beat/miss |
| fed_intelligence | Premium | Fed balance sheet, FOMC, ISM |
| macro_intelligence | Premium | Inflation, employment, M2, credit |
| bond_intelligence | Premium | Yields, curve, credit spreads |
| correlation_tracker | Premium | Cross-market correlation anomalies |
| volatility_analyzer | Premium | VIX regime, term structure, VVIX |
| volatility_surface | Premium | VIX ecosystem, skew, IV vs RV |
| crypto_intelligence | Premium | BTC, ETH, dominance, halving cycle |
| credit_cycle | Premium | Credit cycle phase, spreads, financial conditions |
| sector_rotation | Premium | Business cycle sector rotation |
| intermarket_analysis | Premium | Stock/bond/dollar/commodity signals |
| earnings_calendar | Premium | Upcoming earnings, reactions |
| news_sentiment | Premium | Breaking news with sentiment scoring |
| smart_money_tracker | Premium | Smart vs dumb money divergence |
| divergence_detection | Premium | Price/breadth/volume divergences |
| market_structure | Premium | Breadth, A/D, McClellan |
| exchange_stats | Premium | Market breadth, advance/decline |
| cme_fedwatch | Premium | Fed rate probability expectations |
| options_intelligence | Premium | OCC options OI, volume, gamma |
| alpha_signals | Institutional | Multi-factor signal composite |
| regime_engine | Institutional | 12 market regimes, transitions |
| tail_risk_engine | Institutional | Crisis detection, early warnings |
| liquidity_intelligence | Institutional | Fed net liquidity, regime |
| hedge_fund_playbooks | Institutional | 20+ institutional setups |
| institutional_positioning | Institutional | COT, sentiment, smart money |
| currency_intelligence | Institutional | DXY, carry trades, FX |
| factor_analysis | Institutional | Factor rotation, crowding |
| trend_exhaustion_scanner | Institutional | Trend exhaustion signals |
| advanced_risk | Institutional | Kelly, VaR, drawdown protocols |
| valuation_intelligence | Institutional | CAPE, Buffett indicator, ERP |
| global_flows | Institutional | Dollar cycle, capital rotation |
| geopolitical_risk | Institutional | Risk scoring, hedging |
| central_bank_dashboard | Institutional | All major central banks |
| market_microstructure | Institutional | Gamma, vanna, dealer positioning |
| narrative_tracker | Institutional | Market narrative lifecycle |
| wealth_knowledge | Institutional | Legendary investor wisdom |
| institutional_content | Institutional | Viral FinTwit content |
| market_knowledge | Institutional | Deep market knowledge base |
| sentiment_engine | Institutional | Multi-source sentiment |
| sec_edgar | Institutional | SEC insider filings |
| intelligence_service | Institutional | AI synthesis /ask endpoint |
| historical_parallels | Institutional | Historical analogue engine |
| agent_consensus | Institutional | Agent attention signal |

### Encoded Intelligence Skills (40)

Pre-scored, historically-calibrated pattern recognition. Each skill returns structured data with scores, labels, probabilities, historical analogues, and forward return expectations — not raw data.

| Skill | Tier | Description |
|-------|------|-------------|
| liquidity_fair_value | Institutional | Net Liquidity vs SPX fair value with deviation scoring |
| regime_duration | Institutional | How long current regime has persisted vs historical average |
| momentum_contagion | Institutional | Cross-asset momentum spillover detection |
| cross_asset_momentum | Institutional | Multi-asset momentum composite scoring |
| credit_impulse_sequence | Institutional | Credit cycle phase with 3-6 month equity lead |
| vol_regime_premium | Institutional | Implied vs realized vol premium by regime |
| sector_cycle_position | Institutional | ISM-based sector rotation positioning |
| institutional_conviction | Institutional | Smart money conviction scoring from COT/AAII/NAAIM |
| tail_risk_phase | Institutional | Crisis lifecycle phase (early warning → capitulation) |
| carry_unwind_cascade | Institutional | Yen carry trade stress with cascade probability |
| macro_inflection | Institutional | Economic surprise index with inflection detection |
| stress_propagation | Institutional | Cross-market stress contagion scoring |
| valuation_mean_reversion | Institutional | CAPE/Buffett forward return estimates by percentile |
| sentiment_exhaustion | Institutional | Multi-source sentiment exhaustion detection |
| regime_transition_probability | Institutional | 12-regime Markov transition matrix |
| signal_confluence_strength | Institutional | Multi-factor signal alignment scoring (82% hit rate >90) |
| signal_flip_velocity | Institutional | Category-level signal reversal detection |
| opex_gamma_mechanics | Institutional | OpEx gamma impact with dealer hedging mechanics |
| microstructure_flow_composite | Institutional | CTA/vol-target/pension/buyback flow scoring |
| central_bank_divergence_index | Institutional | Global CB policy divergence with FX implications |
| narrative_lifecycle_exhaustion | Institutional | Market narrative exhaustion and contrarian scoring |
| narrative_conflict_tension | Institutional | Competing narrative tension with resolution probability |
| factor_crowding_composite | Institutional | Factor crowding systemic risk detection |
| factor_leadership_momentum | Institutional | Factor rotation velocity and cycle alignment |
| crypto_leverage_cycle | Institutional | Derivatives leverage phase detection (5 phases) |
| onchain_miner_capitulation | Institutional | Hash rate distress and bottom signal detection |
| onchain_network_health | Institutional | Network activity and adoption trend scoring |
| crypto_halving_cycle_phase | Institutional | 7-phase halving cycle positioning |
| breadth_regime_confirmation | Institutional | Price-breadth divergence with correction probability |
| etf_flow_regime_shift | Institutional | Cross-asset ETF flow regime shift detection |
| risk_drawdown_expectation | Institutional | Risk-adjusted drawdown estimates with Kelly sizing |
| bond_yield_regime | Institutional | Yield regime classification with equity/credit implications |
| geopolitical_risk_premium | Institutional | Composite geopolitical risk premium in basis points |
| vix_regime_intelligence | **Free** | VIX regime (7 levels) with 30d forward SPX returns |
| yield_curve_stress_signal | Institutional | 2s10s recession probability, un-inversion alert |
| commodity_macro_signal | Institutional | Gold/Oil/Copper cross-commodity macro regime |
| dxy_impact_matrix | Institutional | Dollar regime with cross-asset impact mapping |
| cross_asset_momentum_regime | Institutional | Synchronized vs divergent momentum scoring |
| sector_dispersion_signal | Institutional | Macro-driven vs stock-picker market classification |
| fear_greed_extreme_signal | Institutional | Contrarian signal with calibrated forward returns |

## Pricing

- **Free**: 4 modules (includes regime detection with transition probabilities), 10/min, 100/day
- **Premium**: 23 modules, 60/min, 5,000/day, ~$50/mo (50K sats)
- **Institutional**: All 85 modules (including 40 encoded intelligence skills), 120/min, 50,000/day, ~$500/mo (500K sats)

Payment via Bitcoin Lightning Network. Instant settlement, no KYC.

## Example Workflows

### Morning Market Brief
```bash
# Get market overview + bonds + macro + crypto in one batch
curl -s -X POST "https://api.traderhc.com/api/v1/intelligence/batch" \
  -H "X-API-Key: $AGENTHC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"modules": ["market_intelligence", "bond_intelligence", "macro_intelligence", "crypto_intelligence"]}' | jq '.results'
```

### Risk Check
```bash
# Check tail risk + volatility + correlations
curl -s -X POST "https://api.traderhc.com/api/v1/intelligence/batch" \
  -H "X-API-Key: $AGENTHC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"modules": ["tail_risk_engine", "volatility_analyzer", "correlation_tracker"]}' | jq '.results'
```

### Ticker Deep Dive
```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/technical_analysis?ticker=NVDA&format=agent" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.'
```

## Disclaimer

All data and analysis is for educational and informational purposes only. Not financial advice. Not a registered investment advisor. Always do your own research.
