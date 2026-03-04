# Trading Strategies Reference

This document details the six built-in strategies for Kalshi Autopilot. Each strategy has different risk profiles, market focus, and execution approaches.

## Strategy Overview

| Strategy | Risk Level | Sports Focus | Edge Threshold | Position Size | Trades/Day |
|----------|------------|--------------|----------------|---------------|------------|
| Model Follower | Medium | All Sports | 3%+ | 2% bankroll | 10-15 |
| Spread Sniper | Medium | CBB/NBA | 4%+ | 2% bankroll | 6-10 |
| Totals Specialist | Medium-Low | CBB/NBA | 3.5%+ | 1.5% bankroll | 8-12 |
| Contrarian | Low | All Sports | 4%+ | 1% bankroll | 5-8 |
| Conservative | Very Low | All Sports | 5%+ | 1% bankroll | 3-5 |
| Custom | Variable | User Defined | User Defined | User Defined | Variable |

---

## 1. Model Follower (Default)

**Philosophy:** Trust the Fuku model and bet whenever there's a meaningful edge across any sport.

**Configuration:**
```json
{
  "strategy": "model_follower",
  "sports": ["cbb", "nba", "nhl", "soccer"],
  "min_edge_pct": 3.0,
  "sizing": {
    "method": "flat_pct",
    "flat_pct": 2.0,
    "kelly_fraction": 0.25,
    "max_position_pct": 5.0
  },
  "risk": {
    "max_daily_loss_pct": 10.0,
    "max_open_positions": 10,
    "max_daily_bets": 15,
    "stop_loss_enabled": true
  }
}
```

**Strengths:**
- ✅ Diversified across all sports
- ✅ Captures edges in any available market
- ✅ Balanced risk/reward profile
- ✅ Good for beginners

**Weaknesses:**
- ❌ May chase weaker edges in unfamiliar sports
- ❌ No specialization advantage
- ❌ Higher volume = more transaction costs

**Best For:** Users who want a balanced approach and trust the Fuku model across all sports.

---

## 2. Spread Sniper

**Philosophy:** Focus exclusively on spread markets where we have the strongest predictive edge. Target games where point spreads are significantly off from our model.

**Configuration:**
```json
{
  "strategy": "spread_sniper",
  "sports": ["cbb", "nba"],
  "min_edge_pct": 4.0,
  "sizing": {
    "method": "flat_pct",
    "flat_pct": 2.0,
    "max_position_pct": 5.0
  },
  "risk": {
    "max_daily_loss_pct": 8.0,
    "max_open_positions": 8,
    "max_daily_bets": 10,
    "stop_loss_enabled": true
  }
}
```

**Market Types:**
- ✅ Game spreads (team A -X points)
- ✅ Alternative spreads
- ❌ Totals (over/under)
- ❌ Player props
- ❌ Game winners (unless spread-equivalent)

**Edge Calculation:**
- Fuku spread vs. Kalshi implied spread
- Minimum 2-point difference required
- Higher threshold (4%+ probability edge) for quality

**Strengths:**
- ✅ Focus on our strongest predictive area
- ✅ CBB model is particularly strong on spreads
- ✅ Fewer but higher-quality opportunities
- ✅ Easy to track and analyze

**Weaknesses:**
- ❌ Limited to basketball markets
- ❌ May miss opportunities in totals/props
- ❌ Lower volume of bets

**Best For:** Users who believe spread prediction is our core competency and want focused, high-conviction bets.

---

## 3. Totals Specialist

**Philosophy:** Target over/under markets where our pace and scoring models show significant edges. Focus on game totals rather than spreads.

**Configuration:**
```json
{
  "strategy": "totals_specialist",
  "sports": ["cbb", "nba"],
  "min_edge_pct": 3.5,
  "sizing": {
    "method": "flat_pct",
    "flat_pct": 1.5,
    "max_position_pct": 4.0
  },
  "risk": {
    "max_daily_loss_pct": 7.0,
    "max_open_positions": 12,
    "max_daily_bets": 12,
    "stop_loss_enabled": true
  }
}
```

**Market Types:**
- ✅ Game totals (over/under combined score)
- ✅ Team totals (team A over/under X points)
- ❌ Spreads
- ❌ Player props
- ❌ Game winners

**Edge Calculation:**
- Fuku total vs. Kalshi implied total
- Minimum 3-point difference required
- Focus on pace and efficiency mismatches

**Key Factors:**
- **Pace Disparities:** Fast team vs. slow team
- **Defensive Efficiency:** Strong defense → Under edge
- **Offensive Efficiency:** High-scoring teams → Over edge
- **Situational Spots:** Back-to-backs, travel, motivation

**Strengths:**
- ✅ Totals often have softer lines than spreads
- ✅ Less influenced by public betting patterns
- ✅ Good for lower-variance betting
- ✅ Pace analysis is data-driven

**Weaknesses:**
- ❌ Totals can be unpredictable (variance)
- ❌ Limited to basketball
- ❌ Fewer total markets available

**Best For:** Users who prefer lower variance and believe in our pace/efficiency models.

---

## 4. Contrarian

**Philosophy:** Fade heavily-favored public sides when our model shows disagreement. Look for spots where the public is overconfident and Kalshi markets are skewed.

**Configuration:**
```json
{
  "strategy": "contrarian",
  "sports": ["cbb", "nba", "nhl", "soccer"],
  "min_edge_pct": 4.0,
  "sizing": {
    "method": "flat_pct",
    "flat_pct": 1.0,
    "max_position_pct": 3.0
  },
  "risk": {
    "max_daily_loss_pct": 5.0,
    "max_open_positions": 8,
    "max_daily_bets": 8,
    "stop_loss_enabled": true
  }
}
```

**Contrarian Signals:**
- **Model Disagreement:** Our model significantly disagrees with market
- **Public Favorites:** Heavy public betting on popular teams
- **Narrative Bias:** Markets overreacting to recent results
- **Value on Underdogs:** Finding value on unpopular sides

**Example Scenarios:**
- Duke favored by 8, our model has them by 4 → Fade Duke
- Lakers heavily bet, our model sees value on opponent → Fade Lakers
- Team coming off big upset win, market overvalues them → Fade

**Strengths:**
- ✅ Exploits predictable public biases
- ✅ Lower position sizes = safer
- ✅ Often finds value on unpopular sides
- ✅ Works across multiple sports

**Weaknesses:**
- ❌ Requires strong conviction to bet against public
- ❌ Lower volume of opportunities
- ❌ Can be frustrating when favorites cover

**Best For:** Experienced bettors who understand market psychology and are comfortable betting against public sentiment.

---

## 5. Conservative

**Philosophy:** Only bet the strongest edges with minimal risk. Focus on capital preservation while still capturing long-term value.

**Configuration:**
```json
{
  "strategy": "conservative",
  "sports": ["cbb", "nba", "nhl", "soccer"],
  "min_edge_pct": 5.0,
  "sizing": {
    "method": "flat_pct",
    "flat_pct": 1.0,
    "kelly_fraction": 0.1,
    "max_position_pct": 2.0
  },
  "risk": {
    "max_daily_loss_pct": 3.0,
    "max_open_positions": 5,
    "max_daily_bets": 5,
    "stop_loss_enabled": true
  }
}
```

**Selection Criteria:**
- **High Edge Threshold:** Only 5%+ probability edges
- **High Confidence:** Strong model conviction required
- **Quality over Quantity:** Very selective betting
- **Risk Aversion:** Tight stop-losses and position limits

**Trade Characteristics:**
- Fewer bets (3-5 per day max)
- Smaller position sizes (1% of bankroll)
- Higher win rate expected
- Lower absolute returns but better Sharpe ratio

**Strengths:**
- ✅ Lowest risk profile
- ✅ Capital preservation focus
- ✅ High win rate expected
- ✅ Good for beginners or risk-averse users

**Weaknesses:**
- ❌ Lower absolute returns
- ❌ May miss profitable opportunities
- ❌ Very low volume

**Best For:** Risk-averse users prioritizing capital preservation over maximum returns.

---

## 6. Custom Strategy

**Philosophy:** Build your own strategy with complete control over all parameters.

**Configuration Process:**
1. **Sports Selection:** Choose which sports to trade
2. **Edge Threshold:** Set minimum probability edge
3. **Position Sizing:** Choose flat percentage, flat dollar, or Kelly
4. **Risk Limits:** Set daily loss limits, position counts, etc.
5. **Advanced Options:** Scan frequency, auto-trade settings

**Sizing Methods:**

### Flat Percentage
- Fixed percentage of bankroll per bet
- Simple and predictable
- Good for most users
```json
"sizing": {
  "method": "flat_pct",
  "flat_pct": 2.0  // 2% of bankroll per bet
}
```

### Flat Dollar Amount
- Fixed dollar amount per bet
- Good for accounts with varying balance
- Easier to track absolute risk
```json
"sizing": {
  "method": "flat_amount",
  "flat_amount": 100.0  // $100 per bet
}
```

### Kelly Criterion
- Position size based on edge and odds
- Theoretically optimal for long-term growth
- Can be volatile
```json
"sizing": {
  "method": "kelly",
  "kelly_fraction": 0.25  // Quarter-Kelly for safety
}
```

**Advanced Settings:**
```json
{
  "auto_trade": false,           // Require manual approval
  "dry_run": true,              // No real trades, just logging
  "scan_interval_minutes": 30,   // How often to scan for opportunities
  "stop_loss_enabled": true,     // Enable daily loss limits
  "min_liquidity": 1000,        // Minimum market volume (if available)
  "max_spread": 5               // Maximum bid-ask spread (if available)
}
```

**Best For:** Experienced users who want complete control and have specific risk/return preferences.

---

## Risk Management

All strategies include built-in risk management:

### Daily Limits
- **Max Daily Loss:** Stop trading if daily loss exceeds threshold
- **Max Daily Bets:** Prevent overtrading
- **Max Open Positions:** Control portfolio concentration

### Position Limits
- **Max Position Size:** Cap individual bet size
- **Bankroll Percentage:** Never risk too much on single bet
- **Stop Loss:** Automatic halt if losses mount

### Safety Features
- **Kill Switch:** Manual file to instantly halt all trading
- **Dry Run Mode:** Test strategies without real money
- **Manual Approval:** Require confirmation for each trade

---

## Strategy Selection Guide

Choose based on your:

**Risk Tolerance:**
- High: Model Follower, Spread Sniper
- Medium: Totals Specialist
- Low: Contrarian, Conservative

**Sports Knowledge:**
- All Sports: Model Follower, Contrarian, Conservative
- Basketball Focus: Spread Sniper, Totals Specialist

**Time Commitment:**
- High Volume: Model Follower (10-15 bets/day)
- Medium Volume: Spread Sniper, Totals Specialist (6-12 bets/day)
- Low Volume: Contrarian, Conservative (3-8 bets/day)

**Experience Level:**
- Beginner: Conservative, Model Follower
- Intermediate: Spread Sniper, Totals Specialist
- Advanced: Contrarian, Custom

---

## Performance Expectations

**Realistic Expectations:**
- **Win Rate:** 52-58% (depending on strategy)
- **ROI:** 3-8% per month (if edges are real)
- **Drawdowns:** Expect 10-20% drawdowns even with good strategies
- **Volume:** 50-300 bets per month depending on strategy

**Key Metrics to Track:**
- Win rate by sport
- Average edge captured
- Return on investment (ROI)
- Maximum drawdown
- Sharpe ratio
- Trades per strategy/sport

Remember: Past performance doesn't guarantee future results. All trading involves risk of loss.