# Strategy Reference

All 11 built-in trading strategies. Each runs as a standalone Python class — pick one in `config.yaml` or combine them with the `ensemble` meta-strategy.

## Table of Contents

| # | Strategy | Type | External API | Complexity |
|---|----------|------|:---:|:---:|
| 1 | [momentum](#1-momentum) | Mean Reversion | - | Easy |
| 2 | [trend_breakout](#2-trend_breakout) | Trend Following | - | Easy |
| 3 | [pair_arb](#3-pair_arb) | Arbitrage | - | Easy |
| 4 | [logic_arb](#4-logic_arb) | LLM Arbitrage | LLM | Hard |
| 5 | [market_making](#5-market_making) | Market Making | - | Medium |
| 6 | [ensemble](#6-ensemble) | Meta-Strategy | - | Medium |
| 7 | [weather_arb](#7-weather_arb) | Data Arbitrage | NOAA | Medium |
| 8 | [value_investor](#8-value_investor) | Value Investing | - | Medium |
| 9 | [whale_tracking](#9-whale_tracking) | Copy Trading | - | Easy |
| 10 | [sentiment](#10-sentiment) | NLP Divergence | FinBERT | Hard |
| 11 | [expiration_timing](#11-expiration_timing) | Volatility | - | Easy |

---

## 1. momentum

**AI Contrarian Momentum** — mean reversion on breaking markets.

**Idea:** When a market drops sharply (panic selling), buy the dip betting on price recovery. Contrarian bet against the crowd during overreaction.

**How it works:**
1. Fetches breaking markets from prob.trade (biggest 24h price drops)
2. Filters by: drop >= threshold, minimum liquidity, minimum volume, price in range
3. BUY YES at current price — confidence scales with drop magnitude

**Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `drop_threshold` | -0.10 | Minimum 24h price drop (absolute) |
| `take_profit` | 0.10 | Target price rise for exit |
| `min_liquidity` | 5000 | Minimum market liquidity ($) |
| `min_volume_24h` | 1000 | Minimum 24h volume ($) |
| `min_yes_price` | 0.10 | Skip dead markets |
| `max_yes_price` | 0.85 | Skip overpriced markets |
| `order_size` | 5 | USDC per order |

**Config example:**
```yaml
strategy: momentum
strategy_params:
  drop_threshold: -0.10
  min_liquidity: 5000
  min_volume_24h: 1000
  order_size: 5
```

**When to use:** High-volatility periods, breaking news events. Works best on markets that overreact to short-term news.

---

## 2. trend_breakout

**TBO Trend Breakout** — ride the momentum.

**Idea:** Opposite of momentum. When a market is rising with high volume, the trend is likely to continue. Follow the momentum instead of betting against it.

**How it works:**
1. Finds markets with positive 24h price change (rising)
2. Filters for high volume (confirms real momentum, not noise)
3. BUY YES on rising markets — confidence = volume + price change
4. Target quick exit — capture the impulse, don't hold

**Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `rise_threshold` | 0.08 | Minimum 24h price rise |
| `min_volume_24h` | 5000 | High volume confirms momentum |
| `min_liquidity` | 3000 | Need liquidity to enter/exit |
| `max_yes_price` | 0.80 | Don't buy near certainty |
| `min_yes_price` | 0.20 | Skip noise |
| `order_size` | 5 | USDC per order |

**Config example:**
```yaml
strategy: trend_breakout
strategy_params:
  rise_threshold: 0.08
  min_volume_24h: 5000
  order_size: 5
```

**When to use:** Trending markets with sustained volume. Works best on election/sports markets where new information shifts consensus.

---

## 3. pair_arb

**Async Pair Cost Arbitrage** — guaranteed profit from mispricing.

**Idea:** On Polymarket, YES + NO tokens always resolve to $1.00. If you can buy both for less than $1.00, you profit regardless of outcome.

**How it works:**
1. Scans markets where YES price + NO price < target (e.g., $0.95)
2. Buys the cheaper side
3. Over time, accumulates both sides at below $1.00 total cost
4. Guaranteed profit when the market resolves

**Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `target_sum` | 0.95 | Max combined YES+NO price to enter |
| `min_liquidity` | 5000 | Minimum market liquidity ($) |
| `min_volume_24h` | 2000 | Minimum 24h volume ($) |
| `order_size` | 5 | USDC per order |

**Config example:**
```yaml
strategy: pair_arb
strategy_params:
  target_sum: 0.95
  min_liquidity: 5000
  order_size: 5
```

**When to use:** Always. This is a low-risk strategy that works in any market condition. Spreads are rare on popular markets but common on new or low-volume ones.

---

## 4. logic_arb

**Logic Arbitrage (PolyClaw)** — LLM finds correlated markets.

**Idea:** Use an LLM (Claude, GPT-4) to find logical relationships between markets. If "A wins election" implies "Party B loses majority", their prices should be consistent. Trade the inconsistencies.

**How it works:**
1. Fetches active markets from prob.trade
2. Sends market questions to LLM for correlation analysis
3. LLM returns pairs with relationship type ("implies" or "contradicts") and confidence
4. Checks if prices are inconsistent with the logical relationship
5. Builds trades to exploit the mismatch

**Requires:** LLM API key (Anthropic or OpenAI)

**Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `min_confidence` | 0.90 | LLM must be 90%+ confident in correlation |
| `min_spread` | 0.05 | Minimum price inconsistency to trade |
| `search_limit` | 20 | Markets to analyze per cycle |
| `order_size` | 5 | USDC per order |
| `llm_provider` | "" | `"anthropic"` or `"openai"` |
| `llm_api_key` | "" | API key (or set `LLM_API_KEY` env var) |
| `llm_model` | "" | Model name |

**Config example (Claude):**
```yaml
strategy: logic_arb
strategy_params:
  llm_provider: anthropic
  llm_api_key: sk-ant-your-key
  llm_model: claude-sonnet-4-20250514
  min_confidence: 0.90
  min_spread: 0.05
  search_limit: 20
  order_size: 5
```

**Config example (OpenAI):**
```yaml
strategy: logic_arb
strategy_params:
  llm_provider: openai
  llm_api_key: sk-your-key
  llm_model: gpt-4o-mini
  min_confidence: 0.90
  order_size: 5
```

**When to use:** During events with multiple related markets (elections, geopolitical events). Requires LLM API costs — approximately $0.01-0.05 per cycle.

---

## 5. market_making

**Dynamic Spread Market Making** — provide two-sided liquidity.

**Idea:** Place buy orders below mid-price and sell orders above mid-price. Capture the bid-ask spread as profit. Widen spread during volatile periods.

**How it works:**
1. Finds liquid, high-volume markets
2. Calculates mid-price from YES and NO prices
3. Places BUY at mid - spread/2, SELL at mid + spread/2
4. Widens spread when market is volatile (24h price change > 5%)
5. Tracks inventory — stops buying if too exposed to one side

**Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `base_spread` | 0.04 | Base spread width (each side from mid) |
| `volatility_mult` | 2.0 | Spread multiplier when volatile |
| `min_liquidity` | 5000 | Only liquid markets |
| `min_volume_24h` | 5000 | Active markets only |
| `order_size` | 5 | USDC per side |
| `max_inventory` | 3 | Max positions in one market |

**Config example:**
```yaml
strategy: market_making
strategy_params:
  base_spread: 0.04
  volatility_mult: 2.0
  min_liquidity: 5000
  min_volume_24h: 5000
  order_size: 5
  max_inventory: 3
```

**When to use:** Stable, liquid markets. Best when markets are range-bound. Not suitable for trending or volatile markets. Note: production market-makers need sub-second execution — this simplified version runs on the scan interval.

---

## 6. ensemble

**Multi-Agent Ensemble (Swarm)** — Byzantine consensus voting.

**Idea:** Run multiple strategies simultaneously. Only trade when a quorum agrees — protects against single-strategy failures and LLM hallucinations.

**How it works:**
1. Initializes multiple sub-strategies
2. Each sub-strategy independently scans markets and produces signals
3. Groups votes by (market, side, outcome)
4. Only passes signals where quorum is reached (e.g., 3/5 strategies agree)
5. Aggregates confidence, picks best price, combines reasons

**Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `sub_strategies` | `momentum,trend_breakout,value_investor` | Comma-separated strategy names |
| `quorum` | 0.6 | Fraction of strategies that must agree |
| `order_size` | 5 | USDC per order (overrides sub-strategies) |

**Config example (5-strategy consensus):**
```yaml
strategy: ensemble
strategy_params:
  sub_strategies: momentum,trend_breakout,value_investor,pair_arb,whale_tracking
  quorum: 0.6          # 3/5 must agree
  order_size: 5
  # shared params for sub-strategies
  min_liquidity: 5000
  min_volume_24h: 3000
```

**Config example (3-strategy strict):**
```yaml
strategy: ensemble
strategy_params:
  sub_strategies: momentum,pair_arb,expiration_timing
  quorum: 1.0          # all 3 must agree
  order_size: 3
```

**When to use:** When you want maximum safety. Consensus reduces false signals but also reduces trading frequency. Good for live trading with real money.

---

## 7. weather_arb

**Weather Forecast Arbitrage** — NOAA forecast vs market price.

**Idea:** Official weather forecasts (NOAA, ECMWF) are more accurate than crowd predictions on Polymarket. Trade when the forecast probability diverges from market price.

**How it works:**
1. Searches prob.trade for weather-related markets (temperature, hurricane, snow, etc.)
2. Fetches official forecast data from NOAA API
3. Compares forecast probability vs market YES price
4. Trades when divergence exceeds threshold (15%+)

**Requires:** NOAA API token (free)

**Note:** The `_get_forecast_probability()` method is a documented stub. You need to implement the NOAA integration for your specific weather markets.

**Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `min_delta` | 0.15 | Minimum forecast-price divergence |
| `search_keywords` | `temperature,weather,heat,cold,snow,hurricane` | Keywords to search |
| `noaa_api_token` | "" | NOAA token (or `NOAA_API_TOKEN` env var) |
| `order_size` | 5 | USDC per order |

**Config example:**
```yaml
strategy: weather_arb
strategy_params:
  noaa_api_token: your_token
  min_delta: 0.15
  search_keywords: temperature,weather,hurricane
  order_size: 5
```

**Implementation guide:**

Override `_get_forecast_probability()` to integrate with NOAA:
```python
# lib/strategies/my_weather.py
from lib.strategies.weather_arb import WeatherArbStrategy

class MyWeatherStrategy(WeatherArbStrategy):
    name = "my_weather"

    def _get_forecast_probability(self, question):
        # 1. Parse location from question (e.g., "NYC temperature above 90°F")
        # 2. Call NOAA: GET https://api.weather.gov/gridpoints/{office}/{x},{y}/forecast
        # 3. Extract probability from forecast data
        # 4. Return float 0.0-1.0
        pass
```

---

## 8. value_investor

**Value Investor** — buy undervalued markets.

**Idea:** Estimate the "fair" probability of an event and buy when the market price is significantly lower. Uses Kelly criterion for position sizing.

**How it works:**
1. Scans markets with good fundamentals (volume, liquidity)
2. Estimates fair value using heuristic (or LLM — see override)
3. Buys when market price is below fair value by `value_gap`
4. Uses quarter-Kelly criterion for position sizing

**Default heuristic:** If price recently dropped but volume is high, the drop may be an overreaction. Fair value = current price + (recovery adjustment).

**Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `value_gap` | 0.15 | Minimum gap between fair value and price |
| `min_volume_24h` | 3000 | Minimum volume |
| `min_liquidity` | 5000 | Minimum liquidity |
| `order_size` | 5 | Max USDC per order |
| `kelly_fraction` | 0.25 | Fraction of Kelly criterion (quarter-Kelly) |

**Config example:**
```yaml
strategy: value_investor
strategy_params:
  value_gap: 0.15
  kelly_fraction: 0.25
  min_liquidity: 5000
  order_size: 10
```

**LLM-powered version:**
```python
# lib/strategies/llm_value.py
from lib.strategies.value_investor import ValueInvestorStrategy

class LLMValueStrategy(ValueInvestorStrategy):
    name = "llm_value"

    def _estimate_fair_value(self, market):
        question = market.get("question", "")
        # Call Claude/GPT-4 to estimate probability
        response = call_llm(f"Estimate probability (0-1): {question}")
        return parse_float(response)
```

---

## 9. whale_tracking

**Whale Portfolio Tracking** — follow smart money wallets.

**Idea:** Track wallets with high win rates (>65%) on prob.trade leaderboard. When these wallets are active in a market, follow their direction.

**How it works:**
1. Fetches top traders from `/traders/top` endpoint (sorted by win rate)
2. Filters for wallets with `winRate > threshold` and `trades > min_trades`
3. Scans markets for unusual activity (high volume/liquidity ratio)
4. Buys the underdog side (low price = higher potential) in active markets

**Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `min_win_rate` | 0.65 | Minimum win rate for "smart" wallet |
| `min_trades` | 50 | Minimum trades to filter noise |
| `min_volume_24h` | 5000 | Only trade liquid markets |
| `order_size` | 5 | USDC per order |
| `trader_period` | `7d` | Leaderboard period: `all`, `30d`, `7d`, `24h` |
| `trader_limit` | 20 | Number of top traders to fetch |

**Config example:**
```yaml
strategy: whale_tracking
strategy_params:
  min_win_rate: 0.65
  min_trades: 50
  min_volume_24h: 5000
  trader_period: 7d
  order_size: 5
```

**When to use:** Any market condition. Smart money signals are strongest on niche markets where retail traders are less informed.

---

## 10. sentiment

**Social Sentiment Divergence** — NLP sentiment vs market price.

**Idea:** Analyze social media sentiment (Twitter/X, Reddit) using NLP (FinBERT) and trade when sentiment diverges from market price significantly.

**How it works:**
1. For each market, gets the question text
2. Analyzes social media sentiment using NLP model
3. Compares sentiment score (0-1) with YES price
4. Trades when divergence > threshold:
   - Sentiment bullish + low price → BUY YES
   - Sentiment bearish + high price → BUY NO

**Requires:** FinBERT model + social media API access (stub — implement your pipeline)

**Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `min_divergence` | 0.15 | Minimum sentiment-price gap |
| `min_mentions` | 10 | Minimum mentions to trust sentiment |
| `min_volume_24h` | 3000 | Liquid markets only |
| `order_size` | 5 | USDC per order |
| `sentiment_source` | "" | `"twitter"`, `"reddit"`, or custom |

**Config example:**
```yaml
strategy: sentiment
strategy_params:
  sentiment_source: twitter
  min_divergence: 0.15
  min_mentions: 10
  order_size: 5
```

**Implementation guide:**
```python
# lib/strategies/my_sentiment.py
from transformers import pipeline
from lib.strategies.sentiment import SentimentStrategy

nlp = pipeline("sentiment-analysis", model="ProsusAI/finbert")

class MySentimentStrategy(SentimentStrategy):
    name = "my_sentiment"

    def _analyze_sentiment(self, question, market_id):
        import tweepy
        client = tweepy.Client(bearer_token="YOUR_TOKEN")
        tweets = client.search_recent_tweets(query=question, max_results=100)

        if not tweets.data:
            return None

        texts = [t.text for t in tweets.data]
        scores = [nlp(t[:512])[0] for t in texts]
        avg_positive = sum(
            s['score'] for s in scores if s['label'] == 'positive'
        ) / max(len(scores), 1)

        return (avg_positive, len(texts))
```

---

## 11. expiration_timing

**Expiration Timing Volatility** — trade before market resolution.

**Idea:** Markets near expiration (24-72h) exhibit increased volatility as the outcome becomes clearer. Enter before resolution to capture late price swings. Exit before final resolution — don't hold to expiry.

**How it works:**
1. Filters markets expiring within a configurable time window (24-72h)
2. Checks for price movement and minimum volume
3. Follows momentum direction (if rising → YES, if falling → NO)
4. Higher urgency (closer to expiry) = higher confidence

**Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `hours_before_min` | 24 | Earliest to enter (hours before expiry) |
| `hours_before_max` | 72 | Latest window start |
| `min_volume_24h` | 3000 | Minimum volume |
| `min_liquidity` | 2000 | Minimum liquidity |
| `order_size` | 5 | USDC per order |
| `min_price` | 0.15 | Skip very cheap markets |
| `max_price` | 0.85 | Skip near-certain markets |

**Config example:**
```yaml
strategy: expiration_timing
strategy_params:
  hours_before_min: 24
  hours_before_max: 72
  min_volume_24h: 3000
  order_size: 5
```

**When to use:** Always active — works alongside any other strategy. Most effective on markets with binary outcomes (yes/no) where resolution is time-bound.

---

## Creating Your Own Strategy

Drop a Python file in `lib/strategies/` — the bot discovers it automatically.

```python
# lib/strategies/my_strategy.py
from lib.strategy_base import Strategy, Signal, get_yes_price, get_price_change

class MyStrategy(Strategy):
    name = "my_strategy"  # this name goes in config.yaml

    def initialize(self, config):
        """Called once at startup. Read your params from config."""
        self.threshold = config.get("my_param", 0.15)

    def scan(self, markets, positions, balance):
        """Called every cycle. Return list of Signal objects."""
        signals = []
        held = {p.get("conditionId") for p in positions}

        for m in markets:
            cid = m.get("condition_id")
            if not cid or cid in held:
                continue
            if not m.get("active") or not m.get("accepting_orders"):
                continue

            price = get_yes_price(m)
            if price and price < self.threshold:
                signals.append(Signal(
                    market=cid,
                    side="BUY",
                    outcome="Yes",
                    order_type="LIMIT",
                    amount=5,
                    price=price,
                    confidence=0.8,
                    reason=f"Price {price:.2f} below threshold"
                ))
        return signals
```

Set `strategy: my_strategy` in `config.yaml` and run.

### Available helpers

```python
from lib.strategy_base import (
    get_yes_price,     # → 0.45 (float or None)
    get_no_price,      # → 0.55
    get_price_change,  # → -0.12 (24h absolute change)
    get_liquidity,     # → 8000.0
    get_volume_24h,    # → 12500.0
)
```

### Extending built-in strategies

You can subclass any built-in strategy:

```python
from lib.strategies.value_investor import ValueInvestorStrategy

class MyValueStrategy(ValueInvestorStrategy):
    name = "my_value"

    def _estimate_fair_value(self, market):
        # Your custom valuation logic
        return 0.65
```

### Accessing prob.trade API directly

```python
import sys, os
sys.path.insert(0, os.environ.get("PROBTRADE_SKILL_PATH", "../openclaw-skill/lib"))
from api_client import fetch, trading_request

# Public API
data = fetch("/markets/breaking", {"limit": 10})

# Trading API (authenticated)
balance = trading_request("GET", "/balance")
```

### Signal fields

| Field | Type | Description |
|-------|------|-------------|
| `market` | str | Polymarket condition_id |
| `side` | str | `"BUY"` or `"SELL"` |
| `outcome` | str | `"Yes"` or `"No"` |
| `order_type` | str | `"MARKET"` or `"LIMIT"` |
| `amount` | float | USDC to spend |
| `price` | float/None | Price for LIMIT orders (0.01-0.99) |
| `confidence` | float | 0.0-1.0 (used for sorting, logging) |
| `reason` | str | Human-readable explanation |
