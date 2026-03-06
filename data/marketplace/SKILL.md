---
name: Marketplace
slug: marketplace
version: 1.0.1
description: Navigate online marketplaces as buyer, seller, or builder with platform comparison, listing optimization, and scam detection.
metadata: {"clawdbot":{"emoji":"🛒","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Architecture

Role-based guidance for marketplace participation. Load relevant file based on user's role.

```
marketplace/
├── buyer.md      # Price comparison, scam detection, negotiation
├── seller.md     # Listing creation, pricing, platform rules
├── builder.md    # Marketplace creation, economics, liquidity
├── arbitrage.md  # Price gaps, ROI calculations, ToS risks
└── compliance.md # Tax obligations, legal pitfalls, bans
```

## Quick Reference

| Role | File | When to Load |
|------|------|--------------|
| Buying items | `buyer.md` | Comparing prices, spotting scams, negotiating |
| Selling items | `seller.md` | Creating listings, pricing, handling buyers |
| Building marketplace | `builder.md` | Designing platform, economics, payments |
| Arbitrage/Reselling | `arbitrage.md` | Finding price gaps, calculating true ROI |
| Legal/Tax questions | `compliance.md` | Tax nexus, ToS violations, suspensions |

## Core Rules

### 1. Platform-Specific, Never Generic
- Each platform has unique fees, rules, and dynamics
- eBay auction ≠ Amazon Buy Box ≠ FB Marketplace negotiation
- ALWAYS specify which platform advice applies to

### 2. Total Cost, Not Sticker Price
- Include: platform fees, shipping, taxes, return costs
- Amazon referral fee varies 8-45% by category
- eBay 13%+ Poshmark 20%+ Mercari varies

### 3. Scam Pattern Recognition
- Stock photos on local marketplaces = red flag
- "Ship to my address, I'll pay extra" = triangulation fraud
- Payment outside platform = no protection
- New account + high-value item + urgency = likely scam

### 4. Pricing Research = SOLD, Not Listed
- Listed prices mean nothing—items don't sell at listed price
- Always research completed/sold listings
- Factor in condition: "Good" vs "Very Good" = 30% price difference

### 5. Suspension Risks Are Real
- Amazon ODR >1% = account death
- Review manipulation = permanent ban
- IP complaints from brands = immediate suspension
- Multiple accounts = instant termination

### 6. Fee Complexity
Never estimate fees—calculate exactly:
- Amazon: referral + FBA + storage + return processing + advertising
- eBay: final value (category-specific) + promoted listings + payment
- Factor returns into margin (15-30% in some categories)

### 7. Real-Time Data Required
- Never quote prices from memory/training data
- Inventory and pricing change hourly
- Competitor stock levels affect optimal pricing
- Always verify current marketplace state before advising
