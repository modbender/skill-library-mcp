---
name: Temu
slug: temu
version: 1.0.0
description: Shop smarter on Temu with price tracking, review analysis, scam detection, and shipping optimization.
metadata: {"clawdbot":{"emoji":"🛍️","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User wants to buy from Temu without getting scammed. Agent helps evaluate products, detect fakes, compare prices, track orders, and maximize value.

## Quick Reference

| Topic | File |
|-------|------|
| Review analysis | `reviews.md` |
| Pricing strategies | `pricing.md` |
| Scam detection | `scams.md` |

## Core Rules

### 1. Price Reality Check
"90% off" is usually fake. Before recommending any deal:
- Compare to AliExpress, Amazon, eBay for same product
- Check if "original price" is inflated
- Calculate total: base + shipping + potential customs duties
- Historical lows matter more than current "discounts"

### 2. Review Analysis
Most Temu reviews are worthless. Filter by:
| Signal | Weight |
|--------|--------|
| Photo reviews with product in hand | HIGH |
| Reviews mentioning specific measurements | HIGH |
| 1-star reviews citing defects | HIGH |
| Generic 5-star "great product!" | IGNORE |
| Reviews within 24h of listing | RED FLAG |

Minimum threshold: 500+ orders AND 4.5+ stars with real buyer photos.

### 3. Seller Scoring
Check before buying:
- **Store age** — new stores (<6 months) = higher risk
- **Total sales** — more sales = more data points
- **Response rate** — <90% = avoid for expensive items
- **Photo consistency** — stock photos only = dropshipper, beware

### 4. Duplicate Detection
Same product appears from 10+ sellers. Compare:
- Unit price (not just total)
- Shipping time from ACTUAL warehouse location
- Review quality, not quantity
- Return policy differences

### 5. Scam Red Flags
Auto-flag as likely scam:
| Pattern | Action |
|---------|--------|
| Brand item 80%+ below retail | Counterfeit — do not buy |
| Main photo differs from product photos | Bait-and-switch |
| No buyer photos in reviews | Unverified quality |
| Seller only has this one product | Dropship test account |
| Ships from country different than stated | Customs risk |

### 6. Size & Material Verification
NEVER trust listed specifications:
- Cross-reference with actual review measurements
- Search reviews for "actual size", "real material"
- "Leather" under $20 = PU/pleather
- Electronics without CE/FCC = potential customs seizure

### 7. Shipping Reality
Temu ETAs are optimistic fiction:
| Temu Says | Reality |
|-----------|---------|
| 7-12 days | 15-25 days typical |
| "Express" | 10-15 days |
| "Standard" | 20-45 days |

Factor 2-3 weeks minimum for anything not from local warehouse.

### 8. Coupon Optimization
Temu's coupon system is intentionally confusing:
- Stack: welcome coupon + category coupon + free shipping threshold
- Coupons expire — track them
- Free shipping threshold often makes small orders unprofitable
- "Lightning deals" rotate every few hours

### 9. Return Reality
Before buying, know:
- Return shipping often costs more than item value
- "Free returns" has exceptions (electronics, hygiene)
- Dispute window is 90 days from purchase
- Open disputes BEFORE protection expires
- Photo everything when it arrives

### 10. Cross-Platform Decision
| Buy on Temu When | Avoid Temu When |
|------------------|-----------------|
| Disposable/trendy items | Need item in <1 week |
| Price difference >50% vs Amazon | Safety-critical (electronics, car parts) |
| Low-risk categories (decor, accessories) | Brand authenticity matters |
| Willing to wait 2-4 weeks | Need reliable customer service |

## Common Traps

- **Trusting "original price"** → it's fictional; compare to actual market prices
- **Ignoring shipping time** → 2-3 weeks minimum; plan ahead
- **Buying brands** → 99% are counterfeits; don't expect Nike for $5
- **Skipping photo reviews** → text reviews are mostly fake; photos reveal reality
- **Missing dispute deadline** → 90 days passes fast; document issues immediately
- **Small orders without free shipping** → shipping can exceed item cost; batch orders
