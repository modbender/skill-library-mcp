---
name: eBay
slug: ebay
version: 1.0.1
changelog: Minor refinements for consistency
description: Buy, sell, and flip on eBay with listing optimization, pricing research, shipping calculations, and scam detection.
metadata: {"clawdbot":{"emoji":"🛒","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User wants to buy, sell, or flip items on eBay. Agent helps with listing creation, pricing strategy, shipping, and avoiding common pitfalls.

## Quick Reference

| Topic | File |
|-------|------|
| Listing strategies | `listing.md` |
| Pricing research | `pricing.md` |
| Shipping guide | `shipping.md` |

## Core Rules

### 1. Research Sold Listings First
Before pricing: search eBay sold listings (filter: Sold Items).
- Use exact model numbers, not generic terms
- Note condition, included accessories, shipping method
- Price range matters more than single data points

### 2. Title Optimization (80 chars max)
```
[Brand] [Model] [Specs] [Condition] [Key Features] [Accessories]
```
- Front-load searchable terms
- No filler words (WOW, LOOK, L@@K)
- Include model numbers, not just names
- Color and size if applicable

### 3. Fee Calculation
eBay fees structure:
| Category | Final Value Fee |
|----------|-----------------|
| Most categories | 13.25% |
| Clothing | 12% |
| Guitars | 6% |
| Heavy Equipment | 3% |

Plus: $0.30 per order. PayPal/managed payments: ~2.9% + $0.30.
**Quick estimate:** Take 15-17% off sale price for net profit.

### 4. Auction vs Buy It Now
| Use Auction When | Use BIN When |
|------------------|--------------|
| Rare/collectible items | Common items with clear market price |
| Uncertain market value | Need guaranteed price |
| Time-sensitive (holiday) | High-value items (>$500) |
| Building feedback | Consistent inventory |

### 5. Shipping Strategy
- **Free shipping** converts better but price it in
- **Calculated shipping** for heavy/bulky items
- Always add handling time buffer (1 day minimum)
- Pack BEFORE listing to know exact dimensions

### 6. Scam Detection (Seller Side)
Red flags from buyers:
- Requests to ship to different address than PayPal
- "Can you end listing early for $X?"
- Overpayment + request to wire difference
- Pressure for tracking before payment clears
- New account with shipping to freight forwarder

### 7. Scam Detection (Buyer Side)
Red flags from sellers:
- Price too good to be true (50%+ below market)
- Stock photos only
- Ships from different country than stated
- No returns, vague description, low feedback
- Requests payment outside eBay

### 8. Return Policy Impact
| Policy | Effect |
|--------|--------|
| 30-day free returns | Higher search ranking, more sales |
| No returns | Lower visibility, buyers more cautious |
| Restocking fee | Legal but reduces conversions |

Recommendation: 30-day returns for most items (rarely actually used).

## Common Traps

- **Underestimating shipping** → eat costs on heavy items; weigh and measure BEFORE listing
- **Ignoring item specifics** → listings without specs get buried in search
- **Accepting PayPal without verification** → chargebacks on high-value items; require signature for >$750
- **Pricing from asking, not sold** → unsold listings don't reflect market; filter by SOLD
- **Shipping before payment clears** → "Item Not Received" claims; wait for funds
