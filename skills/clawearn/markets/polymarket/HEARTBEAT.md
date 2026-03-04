# Polymarket Trading Heartbeat 📊

*This runs periodically, but you can also check markets anytime you want!*

Time to check in on your Polymarket trading activity!

---

## First: Check for skill updates

```bash
curl -s http://localhost:3000/skills/markets/polymarket/SKILL.md | grep '^version:'
```

Compare with your saved version. If there's a new version, re-fetch the skill files:
```bash
curl -s http://localhost:3000/skills/markets/polymarket/SKILL.md > ~/.clawearn/skills/markets/polymarket/SKILL.md
curl -s http://localhost:3000/skills/markets/polymarket/HEARTBEAT.md > ~/.clawearn/skills/markets/polymarket/HEARTBEAT.md
curl -s http://localhost:3000/skills/markets/polymarket/README.md > ~/.clawearn/skills/markets/polymarket/README.md
```

**Check for updates:** Once a day is plenty. New features and markets get added!

---

## Check your account status

```bash
clawearn polymarket balance check --private-key $POLYMARKET_PRIVATE_KEY
```

This tells you:
- **Available balance**: How much USDC you have to trade
- **Locked balance**: Funds tied up in open orders
- **Total balance**: Your complete account value

**If balance is low:**
- Request pocket money (testnet): `clawearn polymarket balance pocket-money --amount 100`
- Or notify your human to deposit funds

---

## Check your open orders

```bash
clawearn polymarket order list-open --private-key $POLYMARKET_PRIVATE_KEY
```

**Look for:**
- **Stale orders** → Orders that haven't filled in 24+ hours (consider canceling)
- **Mispriced orders** → Orders far from current market price
- **Expired markets** → Markets that have closed (cancel immediately)

**Cancel stale orders:**
```bash
clawearn polymarket order cancel --order-id ORDER_ID --private-key $POLYMARKET_PRIVATE_KEY
```

---

## Check your positions

```bash
# Check positions across all markets
clawearn polymarket positions list --private-key $POLYMARKET_PRIVATE_KEY
```

**For each position, consider:**
- Has the market moved significantly?
- Is it close to resolution?
- Should you take profit or cut losses?
- Do you want to add to the position?

---

## Scan for new markets

```bash
# Get recently created markets
clawearn polymarket market list --tag trending --limit 10
```

**Or search for specific topics:**
```bash
clawearn polymarket market search --query "crypto"
clawearn polymarket market search --query "politics"
clawearn polymarket market search --query "sports"
```

**Look for:**
- Markets related to your human's interests
- Mispriced markets (arbitrage opportunities)
- High-volume markets (better liquidity)
- Markets with clear resolution criteria

---

## Monitor market prices

For markets you're interested in or have positions in:

```bash
# Check current price
clawearn polymarket price get --token-id TOKEN_ID --side buy

# View order book depth
clawearn polymarket price book --token-id TOKEN_ID
```

**Price movement triggers:**
- **Significant change** (>10% in 24h) → Investigate why
- **Approaching resolution** → Consider closing position
- **Arbitrage opportunity** → Price differs from fair value

---

## Consider placing new trades

Ask yourself:
- Did new information emerge that affects a market?
- Are there mispriced markets based on your analysis?
- Has your human expressed interest in a topic?
- Do you have available capital to deploy?

**If yes, place a trade!**

```bash
# Example: Buy "Yes" shares at 0.45
clawearn polymarket order buy \
  --token-id TOKEN_ID \
  --price 0.45 \
  --size 20 \
  --private-key $POLYMARKET_PRIVATE_KEY \
  --signature-type 0
```

**Trading ideas:**
- Markets with clear catalysts coming up
- Contrarian positions on overreacted markets
- Hedging existing positions
- Markets where you have information edge

---

## Risk management checklist

| Check | Action |
|-------|--------|
| Total exposure > 50% of balance | Reduce position sizes |
| Single position > 20% of balance | Consider diversifying |
| Multiple correlated positions | Reduce correlation risk |
| Open orders > 30% of balance | Cancel some orders |
| No activity in 7+ days | Review strategy |

---

## When to tell your human

**Do tell them:**
- A position has moved significantly (>20% gain/loss)
- A market is about to resolve
- You found a potentially mispriced market
- Account balance is running low
- An error occurred (failed order, API issue)
- You need approval for a large trade (>10% of balance)

**Don't bother them:**
- Routine price checks
- Small fills on existing orders
- Normal market browsing
- Minor balance fluctuations

---

## When to check Polymarket

**You don't have to wait for heartbeat!** Check anytime:
- When major news breaks that affects your markets
- When you're curious about market movements
- When you want to explore new trading opportunities
- When you remember a market you wanted to check

**Heartbeat is just a backup** to make sure you don't forget to monitor. Think of it like a gentle reminder, not a rule.

**Rough rhythm:**
- Skill updates: Once a day
- Balance check: Every heartbeat (every few hours)
- Open orders: Every heartbeat
- Positions: Every heartbeat
- New markets: Once or twice a day
- Price monitoring: Whenever you're curious or have positions
- Trading: When you have conviction

---

## Response format

If nothing special:
```
HEARTBEAT_OK - Checked Polymarket, all positions stable. Balance: $X.XX USDC 📊
```

If you did something:
```
Checked Polymarket - Canceled 1 stale order, current balance $X.XX. Watching 3 markets for entry opportunities.
```

If you have positions:
```
Checked Polymarket - 2 active positions: [Market A] up 15%, [Market B] down 5%. Total balance $X.XX.
```

If you need your human:
```
Hey! Your position in "[Market Name]" is up 25% ($XX profit). Should I take profit or let it ride?
```

If there's an opportunity:
```
Hey! I found a potentially mispriced market: "[Market Name]" trading at X% but I think fair value is Y%. Want me to place an order?
```

If there's an issue:
```
Hey! Balance is low ($X.XX remaining) and I have 2 markets I'm watching. Should I deposit more funds?
```

---

## Emergency procedures

**If API is down:**
1. Check https://status.polymarket.com
2. Wait 5-10 minutes and retry
3. If critical, notify your human

**If order fails repeatedly:**
1. Check balance is sufficient
2. Verify token ID is correct
3. Check if market is still active
4. Try reducing order size
5. If still failing, notify your human

**If you suspect account compromise:**
1. **IMMEDIATELY** notify your human
2. Stop all trading activity
3. Do not share private key with anyone

---

## Best practices

✅ **Do:**
- Check positions daily
- Cancel stale orders
- Monitor balance regularly
- Keep notes on why you entered trades
- Learn from both wins and losses

❌ **Don't:**
- Trade without available balance
- Chase losses with bigger bets
- Ignore risk management rules
- Trade markets you don't understand
- Share your private key

---

## Quick reference commands

```bash
# Daily routine
clawearn polymarket balance check --private-key $KEY
clawearn polymarket order list-open --private-key $KEY
clawearn polymarket positions list --private-key $KEY

# Market discovery
clawearn polymarket market list --tag trending --limit 10
clawearn polymarket market search --query "your topic"

# Trading
clawearn polymarket price get --token-id TOKEN --side buy
clawearn polymarket order buy --token-id TOKEN --price 0.50 --size 10 --private-key $KEY
```

---

**Remember:** Trading involves risk. Always follow your human's risk management guidelines and never trade more than you can afford to lose. 📊
