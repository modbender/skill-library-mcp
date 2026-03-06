# Price Tracking & Deal Detection

## Price History Analysis

**What to check:**
- 90-day price range (typical fluctuation)
- 1-year low/high (absolute range)
- Pre-Prime Day prices (baseline for "deals")
- Black Friday/Cyber Monday patterns

**Tools/approaches:**
- CamelCamelCamel for historical data
- Keepa charts embedded in product pages
- Build own tracking for key products

## Fake Discount Detection

**Pattern: Inflate then discount**
- Price raised 2-4 weeks before sale
- "50% off" from inflated price
- Real discount: 10-15% from typical

**How to catch:**
- Compare to 90-day average, not "was" price
- Check if product is actually popular at claimed "original" price
- Look for review velocity — did sales match "original" price claims?

## Optimal Buy Timing

**Predictable sales:**
- Prime Day (July) — electronics, Amazon devices
- Black Friday/Cyber Monday — everything
- Back to school (August) — laptops, supplies
- Spring deals — home/garden

**Category patterns:**
- TVs: Best prices Nov-Dec, new models Jan (old models clearance)
- Laptops: Back to school, Black Friday
- Amazon devices: Prime Day (best), Black Friday
- Clothing: Season-end clearance (60-70% off)

## Price Alert System

Set alerts with context:

```
Product: [ASIN]
Target: $X (Y% below current)
Alert type: 
  - Any drop
  - Target price
  - All-time low
Expiry: [date or "ongoing"]
```

## Subscribe & Save Math

Calculate if worth it:

```
Regular price: $X
S&S discount: Y% (typically 5-15%)
S&S price: $X * (1 - Y/100)
Additional coupons: Often stack

Compare to:
- Deal price frequency
- Price per unit optimization
- Delivery flexibility needed
```

S&S wins for true consumables. Skip for items with frequent sales that beat S&S.

## Multi-Region Arbitrage

When applicable:
- Compare Amazon US/UK/DE prices
- Factor shipping and import duties
- Check warranty validity across regions
- Note: Many products region-locked
