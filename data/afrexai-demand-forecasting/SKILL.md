---
name: Demand Forecasting Framework
description: Build accurate demand forecasts using multiple methodologies.
  Combines statistical models with market intelligence for actionable
  predictions.
---

# Demand Forecasting Framework

Build accurate demand forecasts using multiple methodologies. Combines statistical models with market intelligence for actionable predictions.

## When to Use
- Quarterly/annual demand planning
- New product launch forecasting
- Inventory optimization
- Capacity planning decisions
- Budget cycle preparation

## Forecasting Methodologies

### 1. Time Series Analysis
Best for: Established products with 24+ months of history.

```
Decompose into: Trend + Seasonality + Cyclical + Residual

Moving Average (3-month):
  Forecast = (Month_n + Month_n-1 + Month_n-2) / 3

Weighted Moving Average:
  Forecast = (0.5 × Month_n) + (0.3 × Month_n-1) + (0.2 × Month_n-2)

Exponential Smoothing (α = 0.3):
  Forecast_t+1 = α × Actual_t + (1-α) × Forecast_t
```

### 2. Causal / Regression Models
Best for: Products where external factors drive demand.

Key drivers to model:
- **Price elasticity**: % demand change per 1% price change
- **Marketing spend**: Lag effect (typically 2-6 weeks)
- **Seasonality index**: Monthly coefficient vs annual average
- **Economic indicators**: GDP growth, consumer confidence, industry PMI
- **Competitor actions**: New entrants, price changes, promotions

```
Demand = β₀ + β₁(Price) + β₂(Marketing) + β₃(Season) + β₄(Economic) + ε
```

### 3. Judgmental / Qualitative
Best for: New products, market disruptions, limited data.

Methods:
- **Delphi method**: 3+ expert rounds, anonymous, converging estimates
- **Sales force composite**: Bottom-up from territory reps (apply 15-20% optimism correction)
- **Market research**: Survey-based purchase intent (apply 30-40% intent-to-purchase conversion)
- **Analogous forecasting**: Map to similar product launch curves

### 4. Blended Forecast (Recommended)
Combine methods using confidence-weighted average:

| Method | Weight (Mature Product) | Weight (New Product) |
|--------|------------------------|---------------------|
| Time Series | 50% | 10% |
| Causal | 30% | 20% |
| Judgmental | 20% | 70% |

## Forecast Accuracy Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| MAPE | Avg(|Actual - Forecast| / Actual) × 100 | <15% |
| Bias | Σ(Forecast - Actual) / n | Near 0 |
| Tracking Signal | Cumulative Error / MAD | -4 to +4 |
| Weighted MAPE | Revenue-weighted MAPE | <10% for top SKUs |

## Demand Planning Process

### Monthly Cycle
1. **Week 1**: Statistical forecast generation (auto-run models)
2. **Week 2**: Market intelligence overlay (sales input, competitor intel)
3. **Week 3**: Consensus meeting — align Sales, Marketing, Ops, Finance
4. **Week 4**: Finalize, communicate to supply chain, track vs prior forecast

### Demand Segmentation (ABC-XYZ)

| Segment | Volume | Variability | Approach |
|---------|--------|-------------|----------|
| AX | High | Low | Auto-replenish, tight safety stock |
| AY | High | Medium | Statistical + review quarterly |
| AZ | High | High | Collaborative planning, buffer stock |
| BX | Medium | Low | Statistical, periodic review |
| BY | Medium | Medium | Hybrid model |
| BZ | Medium | High | Judgmental + safety stock |
| CX | Low | Low | Min/max rules |
| CY | Low | Medium | Periodic review |
| CZ | Low | High | Make-to-order where possible |

## Safety Stock Calculation

```
Safety Stock = Z × σ_demand × √(Lead Time)

Where:
  Z = Service level factor (95% = 1.65, 98% = 2.05, 99% = 2.33)
  σ_demand = Standard deviation of demand
  Lead Time = In same units as demand period
```

## Scenario Planning

For each forecast, generate three scenarios:

| Scenario | Probability | Assumptions |
|----------|-------------|-------------|
| Bear | 20% | -15% to -25% vs base. Recession, market contraction, competitor disruption |
| Base | 60% | Historical trends + known pipeline. Most likely outcome |
| Bull | 20% | +15% to +25% vs base. Market expansion, product virality, competitor exit |

## Red Flags in Your Forecast

- [ ] MAPE consistently >20% — model needs retraining
- [ ] Persistent positive bias — sales team sandbagging
- [ ] Persistent negative bias — over-optimism, check incentive structure
- [ ] Tracking signal outside ±4 — systematic error, investigate root cause
- [ ] Forecast never changes — "spreadsheet copy-paste" problem
- [ ] No external inputs — pure statistical = blind to market shifts

## Industry Benchmarks

| Industry | Typical MAPE | Forecast Horizon | Key Driver |
|----------|-------------|-----------------|------------|
| CPG/FMCG | 20-30% | 3-6 months | Promotions, seasonality |
| Retail | 15-25% | 1-3 months | Trends, weather, events |
| Manufacturing | 10-20% | 6-12 months | Orders, lead times |
| SaaS | 10-15% | 12 months | Pipeline, churn, expansion |
| Healthcare | 15-25% | 3-6 months | Regulation, demographics |
| Construction | 20-35% | 12-24 months | Permits, economic cycle |

## ROI of Better Forecasting

For a company doing $10M revenue:
- **5% MAPE improvement** → $200K-$500K inventory savings
- **Reduced stockouts** → 2-5% revenue recovery ($200K-$500K)
- **Lower expediting costs** → $50K-$150K savings
- **Better capacity utilization** → 3-8% OpEx reduction

**Total impact: $450K-$1.15M annually from a 5-point MAPE improvement.**

---

## Full Industry Context Packs

These frameworks scratch the surface. For complete, deployment-ready agent configurations tailored to your industry:

**[AfrexAI Context Packs](https://afrexai-cto.github.io/context-packs/)** — $47 each

- 🏗️ Construction | 🏥 Healthcare | ⚖️ Legal | 💰 Fintech
- 🛒 Ecommerce | 💻 SaaS | 🏠 Real Estate | 👥 Recruitment
- 🏭 Manufacturing | 📋 Professional Services

**[AI Revenue Calculator](https://afrexai-cto.github.io/ai-revenue-calculator/)** — Find your automation ROI in 2 minutes

**[Agent Setup Wizard](https://afrexai-cto.github.io/agent-setup/)** — Configure your AI agent stack

### Bundles
- **Pick 3** — $97 (save 31%)
- **All 10** — $197 (save 58%)
- **Everything Bundle** — $247 (all packs + playbook + wizard)
