# Kalshi Trading Guide

## How Kalshi Works

Kalshi is a CFTC-regulated prediction market where users trade on real-world events. Markets are binary YES/NO contracts.

### Pricing Mechanics

- Each contract pays out $1.00 (100¢) if correct, $0 if wrong
- Prices are in cents (1-99)
- Buying YES at 65¢ means you think there's >65% chance the event happens
- Buying NO at 35¢ means you think there's <65% chance (inverse of YES price)
- YES price + NO price ≈ 100¢ (spreads cause small variations)

### Profit Calculation

**YES contract bought at 65¢:**

- Cost: 65¢ per contract
- If YES wins: receive $1.00 → profit = 35¢ per contract
- If NO wins: lose 65¢ per contract

**NO contract bought at 35¢:**

- Cost: 35¢ per contract
- If NO wins: receive $1.00 → profit = 65¢ per contract
- If YES wins: lose 35¢ per contract

## Market Categories

Kalshi covers:

- **Politics** - Elections, policy outcomes, appointments
- **Economics** - Fed rates, inflation, GDP, unemployment
- **Crypto** - Bitcoin, Ethereum prices at specific dates
- **Weather** - Temperature, precipitation, seasonal forecasts
- **Sports** - Game outcomes, championships
- **Technology** - Product launches, company metrics

## Order Types

### Limit Orders

- Specify exact price you're willing to pay
- May not fill immediately if no counterparty at that price
- Good for getting specific entry points

### Market Orders

- Execute immediately at best available price
- Guarantees fill but not price
- Use for liquid markets only

## Trading Strategy Tips

1. **Check liquidity** - Use `orderbook` command to see depth
   - Thin orderbooks = wide spreads, harder to enter/exit
   - Deep orderbooks = tight spreads, easier trading

2. **Understand the clock** - Markets have close times
   - Check `close_time` field
   - Some markets can close early based on resolution

3. **Position sizing** - Calculate risk before trading
   - Max loss = price paid per contract × count
   - Example: 10 YES contracts at 65¢ = $6.50 at risk

4. **Watch volume** - High volume = more informed pricing
   - `volume_24h` shows recent activity
   - Low volume markets may have stale prices

5. **Read the rules** - Check `rules_primary` field
   - Resolution criteria matter
   - Some markets have specific thresholds or conditions

## Common Patterns

### Fade the Extreme

When a market is priced at 95¢ YES or 5¢ NO, small probability shifts create large % moves. Higher risk, higher reward.

### News Trading

Breaking news can move markets before prices adjust. Use web search to correlate events with market movements.

### Mean Reversion

Some markets overreact to noise. If fundamentals haven't changed, consider fading the move.

### Correlation Plays

Related markets often move together (e.g., different Fed rate meetings). Use one to inform the other.

## Risk Management

1. **Diversify** - Don't put everything in one market
2. **Size appropriately** - Risk only what you can afford to lose
3. **Set stops mentally** - Know your exit price before entering
4. **Track P&L** - Use `portfolio` command regularly
5. **Understand resolution** - Make sure you know when/how market resolves

## Fees

Kalshi charges:

- No fees on resting orders (maker)
- Fees on filled orders (taker)
- Check order confirmation for exact fees

## Best Practices

- **Always confirm before trading** - Double-check ticker, side, count, price
- **Verify you're selling what you own** - Check portfolio before selling
- **Use descriptive search terms** - "fed rate march" works better than "rates"
- **Monitor resting orders** - Cancel and replace if price moves away
- **Read market titles carefully** - Similar tickers can have different strike prices or dates
