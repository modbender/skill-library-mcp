# Fare Estimation & Savings — Taxi

## How Pricing Works

### Standard Formula
```
Fare = Base + (Per-minute × Time) + (Per-km × Distance) + Booking fee + Surge multiplier
```

### Pricing Tiers by Region

| Region | Base | Per-km | Per-min | Minimum | Surge typical |
|--------|------|--------|---------|---------|---------------|
| US major | $2-3 | $1-2 | $0.25-0.40 | $6-10 | 1.2-3x |
| US secondary | $1-2 | $0.80-1.50 | $0.15-0.30 | $5-7 | 1.1-2x |
| Western Europe | €2-4 | €1-2 | €0.20-0.40 | €6-10 | 1.2-2x |
| Eastern Europe | €1-2 | €0.40-0.80 | €0.10-0.20 | €3-5 | 1.1-1.5x |
| Southeast Asia | $0.50-1 | $0.30-0.60 | $0.05-0.15 | $2-4 | 1.2-2x |
| India | ₹30-50 | ₹8-15 | ₹1-2 | ₹50-100 | 1.2-2.5x |
| Latin America | $0.50-2 | $0.40-1 | $0.10-0.20 | $2-5 | 1.2-2x |
| Middle East | $1-3 | $0.50-1.50 | $0.10-0.30 | $3-7 | 1.2-2x |

## Surge Pricing Deep Dive

### When Surge Happens
| Trigger | Expected Surge | Duration |
|---------|---------------|----------|
| Rush hour | 1.3-1.8x | 1-2 hours |
| Rain/weather | 1.5-2x | Weather dependent |
| Concert end | 2-4x | 30-60 min |
| Sports event | 2-3x | 45-90 min |
| Bar closing | 2-3x | 1-2 AM window |
| New Year's Eve | 3-10x | Midnight - 3 AM |
| Major holiday | 1.5-2x | Varies |

### Surge Avoidance Strategies
1. **Wait it out** - Surge often drops 50% within 10-15 min
2. **Walk away** - Move 0.5-1 mile from event venue
3. **Schedule ahead** - Locked prices (some apps)
4. **Check all apps** - Surge varies by platform
5. **Try pool/shared** - Sometimes not surged
6. **Public transit** - Subway doesn't surge
7. **Set price alert** - Agent monitors, notifies when drops

### Surge Monitoring Workflow
1. User needs ride during likely surge time
2. Agent checks current multiplier across apps
3. If >2x: Alert user, suggest wait or alternative
4. Set 5-min check interval
5. Notify when any app drops below threshold
6. User confirms, agent assists booking

## Maximizing Savings

### Promo Code Sources
| Source | Type | Notes |
|--------|------|-------|
| RetailMeNot | Codes | General promo aggregator |
| Honey extension | Auto-apply | Browser extension |
| App emails | User-specific | Check spam folder |
| Credit card portals | % back | Chase, Amex, etc. |
| Student discount | Ongoing | .edu email required |
| Corporate accounts | Negotiated | Business profile |
| Referral codes | New users | One-time bonus |
| Airport partnerships | Flat rates | Some airports |

### Price Comparison Checklist
Before any non-urgent ride:
- [ ] Check Uber estimate
- [ ] Check Lyft/Bolt estimate
- [ ] Check local app if applicable
- [ ] Search "[app] promo code [month] [year]"
- [ ] Check if scheduled ride cheaper
- [ ] Consider pool/shared option
- [ ] Compare to public transit + last mile

### Scheduled vs On-Demand
| Scenario | Better Option |
|----------|---------------|
| Airport at 5 AM | Scheduled (no surge guarantee) |
| Meeting in 2 hours | Scheduled (peace of mind) |
| Leaving bar now | On-demand (can't predict) |
| Regular commute | Scheduled (often 10-20% off) |
| Flexible timing | Wait and watch surge |

## Airport Specifics

### Common Airport Fee Structures
| Airport | Uber/Lyft | Taxi | Notes |
|---------|-----------|------|-------|
| JFK | Base + $5-8 fee | Flat $70 to Manhattan | Taxi better for Manhattan |
| LAX | Base + $4 fee | Metered | Use LAXit pickup lot |
| LHR | Base + £3-5 fee | Metered/fixed | Compare Heathrow Express |
| SFO | Base + $3-5 fee | Metered | Consider BART + rideshare |

### Airport Tips
- Know terminal-specific pickup zones
- Pre-book for guaranteed availability
- Check if hotel shuttle is free
- Compare shuttle services (SuperShuttle, etc.)
- Use flight tracking to adjust pickup time
- Have backup plan if app doesn't work (taxi queue)

## Tipping Guide

| Region | Expectation | Standard |
|--------|-------------|----------|
| US | Expected | 15-20% or $2-5 min |
| UK | Appreciated | 10% or round up |
| Europe | Optional | Round up €1-2 |
| Australia | Not expected | Round up if great service |
| Asia | Not expected | Not customary |
| Latin America | Appreciated | 10% or round up |
| Middle East | Appreciated | Round up or 10% |

### When to Tip More
- Help with heavy luggage
- Long wait at pickup
- Excellent conversation/service
- Bad weather
- Late night/early morning

## Business Travel

### Receipt Management
- All apps: Email receipt auto-send
- Uber: Uber for Business dashboard
- Lyft: Business profile expense reports
- Export: Monthly CSV/PDF available

### Corporate Account Benefits
- Centralized billing
- Pre-set expense categories
- Policy compliance (fare caps)
- Admin oversight
- Consolidated invoices

### VAT/Tax Considerations
- UK/EU: VAT on app fees, not driver portion
- Request formal invoice for large amounts
- Keep receipts for reimbursement
- Note: Tax treatment varies by jurisdiction

## Price Tracking Over Time

Agent can track:
- User's common routes → historical prices
- Best time to book regular commute
- Seasonal patterns (summer tourist surge)
- Event calendar → predict surge days
- Route alternatives → price comparison

Store in `~/taxi/trips.md` for analysis.
