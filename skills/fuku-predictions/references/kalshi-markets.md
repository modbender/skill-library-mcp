# Kalshi Sports Markets Guide

Understanding how Kalshi prediction markets work is crucial for successful automated trading. This guide covers market structure, pricing, and conversion between traditional betting lines and Kalshi contracts.

## How Kalshi Markets Work

### Binary Contracts
Every Kalshi market is a **YES/NO** question resolved to exactly 0¢ or 100¢:
- **YES wins:** Contract pays 100¢ ($1.00)
- **NO wins:** Contract pays 0¢ ($0.00)
- **Price range:** 1¢ to 99¢ (representing probability)

### Market Examples
```
"Will the Lakers beat the Celtics?"
YES 65¢ | NO 35¢
→ Market implies 65% chance Lakers win

"Will the game total go over 225.5 points?"
YES 48¢ | NO 52¢
→ Market implies 48% chance of over
```

### Profit Calculation
```
Buy YES at 65¢:
- If YES wins: Profit = 100¢ - 65¢ = 35¢ per contract
- If NO wins: Loss = 65¢ per contract
- Breakeven: Need >65% probability to be profitable
```

---

## Sports Market Structure

### Basketball (NBA/CBB)

#### Game Winner Markets
```
Ticker Pattern: KXNBAGAME-YYYYMMDD-TEAM1-TEAM2
Question: "Will [Team A] beat [Team B]?"
Example: KXNBAGAME-20241215-LAL-BOS
```

#### Spread Markets
```
Ticker Pattern: KXNBASPREAD-YYYYMMDD-TEAM-SPREAD
Question: "Will [Team A] win by more than X points?"
Example: KXNBASPREAD-20241215-LAL-4.5
→ "Will Lakers win by more than 4.5 points?"
```

#### Total Points Markets
```
Ticker Pattern: KXNBATOTAL-YYYYMMDD-TEAM1-TEAM2-TOTAL
Question: "Will the total points go over X?"
Example: KXNBATOTAL-20241215-LAL-BOS-225.5
→ "Will total points exceed 225.5?"
```

#### Team Total Markets
```
Ticker Pattern: KXNBATEAMTOTAL-YYYYMMDD-TEAM-TOTAL
Question: "Will [Team A] score more than X points?"
Example: KXNBATEAMTOTAL-20241215-LAL-112.5
→ "Will Lakers score over 112.5 points?"
```

### Hockey (NHL)

#### Game Winner Markets
```
Ticker Pattern: KXNHL-YYYYMMDD-TEAM1-TEAM2
Question: "Will [Team A] beat [Team B] (regulation + OT + SO)?"
```

#### Puck Line Markets
```
Ticker Pattern: KXNHLSPREAD-YYYYMMDD-TEAM-SPREAD
Question: "Will [Team A] win by more than X goals?"
Example: KXNHLSPREAD-20241215-BOS-1.5
→ "Will Bruins win by 2+ goals?"
```

#### Goal Total Markets
```
Ticker Pattern: KXNHLTOTAL-YYYYMMDD-TEAM1-TEAM2-TOTAL
Question: "Will total goals exceed X?"
Example: KXNHLTOTAL-20241215-BOS-NYR-5.5
```

### Soccer

#### Match Result Markets
```
Ticker Pattern: KXSOCCER-YYYYMMDD-TEAM1-TEAM2
Question: "Will [Team A] beat [Team B] (90 minutes + stoppage)?"
Note: This is usually 3-way (Win/Draw/Lose) but Kalshi uses binary
```

#### Goal Total Markets
```
Ticker Pattern: KXSOCCERTOTAL-YYYYMMDD-TEAM1-TEAM2-TOTAL
Question: "Will total goals exceed X?"
Example: KXSOCCERTOTAL-20241215-MCI-ARS-2.5
```

#### Both Teams to Score
```
Ticker Pattern: KXSOCCERBTTS-YYYYMMDD-TEAM1-TEAM2
Question: "Will both teams score at least one goal?"
```

---

## Converting Traditional Lines to Kalshi Prices

### Spread Conversion

**Traditional Spread:** Lakers -4.5 (-110 both sides)
**Kalshi Equivalent:** "Will Lakers win by more than 4.5 points?"

```python
# Traditional: Lakers -4.5 implies ~52.4% chance
traditional_prob = 110 / (110 + 100) = 0.524

# Kalshi price should be around 52¢ for YES
kalshi_yes_price = traditional_prob * 100 = 52¢
kalshi_no_price = 100 - 52 = 48¢
```

### Total Conversion

**Traditional Total:** Over 225.5 (-105) / Under 225.5 (-115)
**Kalshi Equivalent:** "Will total points exceed 225.5?"

```python
# Over -105 implies: 105 / (105 + 100) = 51.2%
over_prob = 105 / 205 = 0.512
kalshi_yes_price = 51¢

# Under -115 implies: 115 / (115 + 100) = 53.5%  
under_prob = 115 / 215 = 0.535
kalshi_no_price = 53¢

# Note: Prices don't always add to 100¢ due to vig
```

### Moneyline Conversion

**Traditional Moneyline:** Lakers -150 / Celtics +130
**Kalshi Equivalent:** "Will Lakers beat Celtics?"

```python
# Lakers -150: 150 / (150 + 100) = 60%
lakers_prob = 150 / 250 = 0.60
kalshi_yes_price = 60¢

# Celtics +130: 100 / (130 + 100) = 43.5%
celtics_prob = 100 / 230 = 0.435
kalshi_no_price = 43.5¢

# Note: Total is 103.5% due to vig
```

---

## Edge Calculation

### Point Spread Edge

```python
def calculate_spread_edge(fuku_spread, kalshi_price, side):
    """
    Calculate edge on spread bet
    
    Args:
        fuku_spread: Our model's spread (negative = favorite)
        kalshi_price: Current YES price (0-100)
        side: "yes" or "no"
    
    Returns:
        Probability edge percentage
    """
    
    # Convert spread to win probability (simplified)
    # This is sport-specific and could be improved
    if abs(fuku_spread) <= 3:
        fuku_prob = 0.55  # Close game
    elif abs(fuku_spread) <= 7:
        fuku_prob = 0.60  # Medium favorite
    elif abs(fuku_spread) <= 14:
        fuku_prob = 0.70  # Strong favorite
    else:
        fuku_prob = 0.80  # Heavy favorite
    
    # Adjust for actual spread direction
    if fuku_spread > 0:  # We're betting on underdog
        fuku_prob = 1 - fuku_prob
    
    # Compare to Kalshi implied probability
    kalshi_prob = kalshi_price / 100
    
    if side == "yes":
        edge = fuku_prob - kalshi_prob
    else:
        edge = (1 - fuku_prob) - (1 - kalshi_prob)
    
    return edge * 100  # Return as percentage
```

### Point Total Edge

```python
def calculate_total_edge(fuku_total, book_total, kalshi_price, side):
    """
    Calculate edge on total bet
    
    Args:
        fuku_total: Our model's total
        book_total: Kalshi market's total
        kalshi_price: Current YES price for over
        side: "yes" (over) or "no" (under)
    
    Returns:
        Probability edge percentage
    """
    
    # Calculate point difference
    total_diff = fuku_total - book_total
    
    # Convert to probability (sport-specific)
    # Basketball: ~1.5-2% per point
    # Hockey: ~8-10% per goal  
    # Soccer: ~15-20% per goal
    
    if total_diff > 0:  # Our model predicts higher scoring
        over_edge_pct = abs(total_diff) * 2.0  # 2% per point
        fuku_over_prob = 0.50 + (over_edge_pct / 100)
    else:  # Our model predicts lower scoring  
        under_edge_pct = abs(total_diff) * 2.0
        fuku_over_prob = 0.50 - (under_edge_pct / 100)
    
    # Cap probabilities
    fuku_over_prob = max(0.1, min(0.9, fuku_over_prob))
    
    # Compare to Kalshi
    kalshi_over_prob = kalshi_price / 100
    
    if side == "yes":  # Betting over
        edge = fuku_over_prob - kalshi_over_prob
    else:  # Betting under
        edge = (1 - fuku_over_prob) - (1 - kalshi_over_prob)
    
    return edge * 100
```

---

## Market Timing and Liquidity

### When Markets Open
- **NBA:** Usually 2-3 hours before game
- **CBB:** Usually 1-2 hours before game  
- **NHL:** Usually 2-3 hours before game
- **Soccer:** Usually 4-6 hours before match

### Liquidity Considerations
- **Volume:** Check `open_interest` and `volume` fields
- **Spread:** Wide bid-ask spreads indicate low liquidity
- **Market Making:** Kalshi has official market makers but volume varies

### Optimal Trading Times
- **Early:** Right when markets open (soft lines)
- **Late:** 30 minutes before game (sharp but moving)
- **Avoid:** 10 minutes before game (market may halt)

---

## Market Resolution

### Basketball
- **Game Winner:** Final score after regulation + OT
- **Spread:** Final margin of victory
- **Total:** Combined final score of both teams
- **Player Props:** Official stats from game

### Hockey  
- **Game Winner:** Result after regulation + OT + shootout
- **Puck Line:** Final margin (shootout = 1 goal margin)
- **Total:** Goals in regulation + OT + shootout

### Soccer
- **Match Result:** After 90 minutes + stoppage time only
- **Total Goals:** Goals in regulation + stoppage (no ET)
- **Both Teams Score:** At least 1 goal each team

### Resolution Timing
- Markets typically resolve within 30-60 minutes after game ends
- Disputed outcomes may take longer
- Payouts processed within 24 hours

---

## Common Pitfalls

### Market Structure Misunderstanding
❌ **Wrong:** Thinking Kalshi prices are like traditional odds
✅ **Right:** Kalshi prices represent probabilities (0-100%)

❌ **Wrong:** Assuming prices always sum to 100¢  
✅ **Right:** Vig can make sum ≠ 100¢

### Resolution Confusion
❌ **Wrong:** NBA overtime doesn't count for totals
✅ **Right:** All NBA markets include OT

❌ **Wrong:** Soccer markets include extra time
✅ **Right:** Soccer markets are 90 minutes + stoppage only

### Liquidity Issues
❌ **Wrong:** Placing large orders in thin markets
✅ **Right:** Check volume and start with small positions

### Edge Calculation Errors
❌ **Wrong:** Using same conversion for all sports
✅ **Right:** Sport-specific probability models

---

## Advanced Concepts

### Correlated Markets
Some markets are highly correlated:
- Team total + opponent total ≈ Game total
- Large spread + low total = likely blowout
- High-scoring game = more variance in spread

### Line Movement
Kalshi prices move based on:
- Trading volume and flow
- Information from traditional sportsbooks  
- News and injury reports
- Model updates

### Arbitrage Opportunities
Rare but possible between:
- Different Kalshi markets (team totals vs game total)
- Kalshi vs traditional sportsbooks (complex due to format differences)
- Early vs late markets on same event

### Risk Management
- **Correlation:** Don't bet correlated markets heavily
- **Bankroll:** Never risk more than 5% on single market
- **Diversification:** Spread bets across sports/market types
- **Stop Losses:** Exit if daily losses mount

---

## API Integration Notes

### Market Search
```python
# Search for NBA games on specific date
markets = kalshi_client.search_markets("NBA 2024-12-15")

# Filter by series
nba_spreads = kalshi_client.get_markets(series_ticker="KXNBASPREAD")
```

### Price Monitoring
```python
# Get current price for market
market = kalshi_client.get_market("KXNBASPREAD-20241215-LAL-4.5")
current_yes_price = market["yes_price"]
```

### Order Placement
```python
# Place limit order
result = kalshi_client.place_order(
    ticker="KXNBASPREAD-20241215-LAL-4.5",
    side="yes",
    action="buy", 
    count=10,
    yes_price=55  # Bid 55¢ for YES
)
```

Understanding these market mechanics is essential for profitable automated trading. The key is correctly converting between traditional betting concepts and Kalshi's binary market structure.