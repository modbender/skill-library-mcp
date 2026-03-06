# Moltearn Heartbeat 📊

*This runs periodically, but you can also check your markets anytime you want!*

Time to check in on your trading activity across all enabled markets!

---

## First: Check for skill updates

```bash
curl -s https://clawearn.xyz/skills/SKILL.md | grep '^version:'
```

# Update main files
curl -s https://clawearn.xyz/skills/SKILL.md > ~/.clawearn/skills/SKILL.md
curl -s https://clawearn.xyz/skills/HEARTBEAT.md > ~/.clawearn/skills/HEARTBEAT.md

# Update core files
curl -s https://clawearn.xyz/skills/core/WALLET.md > ~/.clawearn/skills/core/WALLET.md

# Update enabled markets (check your config)
for market in $(cat ~/.clawearn/config.json | jq -r '.enabled_markets[]'); do
  curl -s http://localhost:3000/skills/markets/$market/SKILL.md > ~/.clawearn/skills/markets/$market/SKILL.md
done
```

**Check for updates:** Once a day is plenty. New markets and features get added!

---

## Check Your Configuration

```bash
cat ~/.clawearn/config.json
```

**Verify:**
- Which markets are enabled?
- Are credentials configured?
- Are risk limits set appropriately?

---

## For Each Enabled Market

Run the market-specific heartbeat routine:

### Polymarket
```bash
# See detailed heartbeat in markets/polymarket/HEARTBEAT.md
clawearn polymarket balance check --private-key $POLYMARKET_PRIVATE_KEY
clawearn polymarket order list-open --private-key $POLYMARKET_PRIVATE_KEY
```

### Manifold (when available)
```bash
# Check Mana balance
curl https://manifold.markets/api/v0/me -H "Authorization: Bearer $MANIFOLD_API_KEY"
```

### Kalshi (when available)
```bash
# Check USD balance
curl https://trading-api.kalshi.com/v1/portfolio/balance -H "Authorization: Bearer $KALSHI_TOKEN"
```

---

## Cross-Market Portfolio View

### Total Portfolio Value

```bash
#!/bin/bash
# portfolio-summary.sh

echo "=== Moltearn Portfolio Summary ==="
echo ""

TOTAL=0

# Polymarket
if [ -f ~/.config/clawearn/polymarket-key.txt ]; then
  POLY_BALANCE=$(clawearn polymarket balance check --private-key $POLYMARKET_PRIVATE_KEY | grep -o '[0-9.]*')
  echo "Polymarket: \$$POLY_BALANCE USDC"
  TOTAL=$(echo "$TOTAL + $POLY_BALANCE" | bc)
fi

# Manifold (play money, not included in total)
if [ ! -z "$MANIFOLD_API_KEY" ]; then
  MANA=$(curl -s https://manifold.markets/api/v0/me -H "Authorization: Bearer $MANIFOLD_API_KEY" | jq -r '.balance')
  echo "Manifold: M$MANA (play money)"
fi

# Kalshi
if [ ! -z "$KALSHI_TOKEN" ]; then
  KALSHI_BALANCE=$(curl -s https://trading-api.kalshi.com/v1/portfolio/balance -H "Authorization: Bearer $KALSHI_TOKEN" | jq -r '.balance')
  echo "Kalshi: \$$KALSHI_BALANCE USD"
  TOTAL=$(echo "$TOTAL + $KALSHI_BALANCE" | bc)
fi

echo ""
echo "Total Real Money: \$$TOTAL"
echo "=== End Summary ==="
```

---

## Risk Management Check

### Position Concentration

```bash
# Check if any single position is too large
# (Implement based on your risk limits in config.json)

MAX_POSITION_PCT=20  # From config
TOTAL_PORTFOLIO=1000  # Calculate from above

# For each position, check:
# position_value / TOTAL_PORTFOLIO * 100 < MAX_POSITION_PCT
```

### Exposure Across Markets

```json
{
  "total_portfolio": 1000,
  "exposure_by_market": {
    "polymarket": 500,
    "kalshi": 300,
    "manifold": 0
  },
  "exposure_pct": {
    "polymarket": 50,
    "kalshi": 30,
    "manifold": 0
  },
  "within_limits": true
}
```

---

## Arbitrage Opportunities

🔍 **Look for price discrepancies across markets:**

If the same event is listed on multiple markets, compare prices:

```bash
# Example: Presidential election market
POLY_PRICE=$(get_polymarket_price "ELECTION_MARKET")
KALSHI_PRICE=$(get_kalshi_price "ELECTION_MARKET")

# If prices differ significantly, potential arbitrage!
if [ $POLY_PRICE -lt $KALSHI_PRICE ]; then
  echo "🎯 Arbitrage opportunity: Buy on Polymarket, sell on Kalshi"
fi
```

**Note:** Consider:
- Transaction fees
- Withdrawal times
- Liquidity differences
- Settlement risk

---

## When to Tell Your Human

**Do tell them:**
- Total portfolio value changed significantly (>10%)
- Found arbitrage opportunity (>5% spread)
- Risk limits approaching (>80% of max)
- Any market had a major issue/error
- New market opportunity that matches their interests
- Balance running low on any market

**Don't bother them:**
- Routine balance checks
- Small price movements
- Normal market browsing
- Minor fills on existing orders

---

## When to Check Markets

**You don't have to wait for heartbeat!** Check anytime:
- When major news breaks
- When you're curious about opportunities
- When you want to explore new markets
- When you remember something to check

**Heartbeat is just a backup** to ensure you don't forget to monitor.

**Rough rhythm:**
- Skill updates: Once a day
- Portfolio summary: Every heartbeat (every few hours)
- Market-specific checks: Follow each market's HEARTBEAT.md
- Arbitrage scanning: Once or twice a day
- Risk review: Daily

---

## Response Format

### If nothing special:
```
HEARTBEAT_OK - All markets checked. Total portfolio: $X,XXX. All positions within limits. 📊
```

### If you have activity:
```
Checked all markets:
- Polymarket: $XXX (2 positions, up 5%)
- Kalshi: $XXX (1 position, down 2%)
- Total: $X,XXX
Canceled 1 stale order on Polymarket.
```

### If you found an opportunity:
```
Hey! Found potential arbitrage:
- Market: "Presidential Election"
- Polymarket: 45¢ YES
- Kalshi: 52¢ YES
- Spread: 7¢ (15% profit potential)
Should I execute?
```

### If you need your human:
```
Hey! Portfolio is down 12% today ($XXX loss). Hit the daily loss limit. 
Trading paused. Want to review positions?
```

### If there's a risk issue:
```
⚠️ Risk Alert: Polymarket position is now 25% of portfolio (limit: 20%).
Should I reduce the position or increase the limit?
```

---

## Market-Specific Heartbeats

For detailed market-specific routines, see:

- **Polymarket**: `markets/polymarket/HEARTBEAT.md`
- **Manifold**: `markets/manifold/HEARTBEAT.md` (coming soon)
- **Kalshi**: `markets/kalshi/HEARTBEAT.md` (coming soon)

---

## Emergency Procedures

### If All Markets Are Down
1. Check internet connection
2. Check if it's scheduled maintenance
3. Wait 5-10 minutes and retry
4. If critical, notify your human

### If One Market Is Down
1. Check that market's status page
2. Continue monitoring other markets
3. Document the outage
4. Notify human if positions are at risk

### If You Suspect Security Issue
1. **IMMEDIATELY** stop all trading
2. Check all balances for unexpected changes
3. Review recent transactions
4. Notify your human
5. Follow incident response in `core/SECURITY.md`

---

## Quick Reference Commands

```bash
# Daily routine
cat ~/.clawearn/config.json  # Check config
./portfolio-summary.sh        # Get total portfolio value

# Per-market checks
clawearn polymarket balance check --private-key $POLYMARKET_PRIVATE_KEY
curl https://manifold.markets/api/v0/me -H "Authorization: Bearer $MANIFOLD_API_KEY"
curl https://trading-api.kalshi.com/v1/portfolio/balance -H "Authorization: Bearer $KALSHI_TOKEN"

# Update skills
curl -s http://localhost:3000/skills/SKILL.md > ~/.clawearn/skills/SKILL.md
```

---

**Remember:** Diversification across markets can reduce risk, but also increases complexity. Monitor all your positions carefully! 📊
