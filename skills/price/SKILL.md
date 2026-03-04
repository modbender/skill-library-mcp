---
name: Price
slug: price
version: 1.0.0
description: Track prices, detect deals and manipulation, time purchases, and make informed buying decisions as a consumer or business buyer.
metadata: {"clawdbot":{"emoji":"💰","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User asks: "is this a good price?", "should I buy now or wait?", "track this price", "price history", "is this sale real?", "hidden fees", "compare prices", "price alert", "shrinkflation", "fair market value".

NOT for: setting prices as a seller (use `pricing`), general buying process (use `buy`), negotiation tactics.

## Quick Reference

| Area | File |
|------|------|
| Retail & electronics | `retail.md` |
| Travel & hospitality | `travel.md` |
| B2B & enterprise | `b2b.md` |
| Collectibles & investments | `collectibles.md` |
| Manipulation detection | `manipulation.md` |
| Price tracking setup | `tracking.md` |

## Workspace Structure

All data lives in ~/price/:

```
~/price/
├── config.md           # Preferred retailers, alert thresholds
├── watchlist.md        # Items being tracked with targets
├── history/            # Price history by item
├── alerts.md           # Active price alerts
└── purchases.md        # Past decisions for learning
```

## Core Operations

**Evaluate price:** Current price + item → Check historical range → Calculate vs 90-day low → Factor total cost → Verdict with confidence level.

**Set alert:** Item + target price → Add to watchlist → Monitor across retailers → Notify when hit.

**Track item:** Product URL/name → Poll price periodically → Log to history → Detect changes.

**Time purchase:** Category + timeframe → Check seasonal patterns → Recommend buy/wait → Explain reasoning.

## Price Assessment Framework

For EVERY price evaluation:

1. **Historical context** — Current vs 90-day low, all-time low, typical range
2. **Total cost** — Add shipping, tax, fees, warranty, hidden costs
3. **Timing factors** — Seasonal patterns, upcoming sales, event-driven spikes
4. **Manipulation check** — Inflated "was" price, dynamic pricing, fake urgency

## Output Format

```
## Price Assessment: [Item]

**Current:** $X | **90-day low:** $Y | **All-time low:** $Z
**Total cost:** $W (includes: shipping, tax, fees)
**Verdict:** [Good deal | Fair | Wait | Overpriced]

**Why:** [Data-backed reasoning]
**Action:** [Buy now | Set alert for $X | Wait until Y]
**Confidence:** [High | Medium | Low] — [data quality note]
```

## Critical Rules (ALWAYS Apply)

- **Show data sources** — Never claim price history without citing where it came from
- **Include total cost** — Listed price is not final price, always add fees
- **State confidence level** — Be honest about data quality and limitations
- **Explain "why now"** — If recommending buy, explain what makes timing good
- **Flag manipulation** — Always check for inflated comparisons, dynamic pricing

## On First Use

1. Ask what categories user buys frequently
2. Set up preferred retailers list
3. Configure alert notification preferences
4. Explain price history data sources available
5. Add first items to watchlist
