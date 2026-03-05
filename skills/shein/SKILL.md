---
name: Shein Shopping
slug: shein
version: 1.0.0
homepage: https://clawic.com/skills/shein
description: Shop Shein with price tracking, size guidance, quality assessment, and smart deal finding.
metadata: {"clawdbot":{"emoji":"🛍️","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User wants to shop on Shein. Agent helps with product research, sizing, quality checks, price tracking, and finding the best deals.

## Quick Reference

| Topic | File |
|-------|------|
| Size conversion | `sizing.md` |
| Quality signals | `quality.md` |

## Core Rules

### 1. Always Check Reviews First
Before recommending any product:
- Minimum 100 reviews for reliability
- Check photo reviews (real product appearance)
- Read 1-star reviews for common issues
- Look for sizing feedback in comments

### 2. Size Conversion Priority
| Region | Action |
|--------|--------|
| US/EU user | Convert to Shein sizes using sizing.md |
| Asia user | Usually direct match, verify with measurements |
| Any user | Always recommend checking size chart measurements |

### 3. Price Intelligence
- Track prices over 2-4 weeks before major purchases
- Flash sales: verify original price (often inflated)
- Coupons stack: app-exclusive + email signup + influencer codes
- Free shipping threshold: optimize cart to hit it

### 4. Quality Assessment Protocol
Use signals from quality.md:
- Fabric composition (avoid 100% polyester for summer)
- Photo count (more seller photos = more confidence)
- Return rate mentions in reviews
- Compare similar items from different sellers

### 5. Shipping Reality
| Destination | Standard | Express |
|-------------|----------|---------|
| US/EU | 7-15 days | 3-7 days |
| Other | 15-30 days | 7-15 days |

Set realistic expectations. Express worth it for time-sensitive items only.

### 6. Return Policy Awareness
- 35-day return window from delivery
- Some items non-returnable (swimwear, underwear, accessories)
- Return shipping cost varies by region
- Document condition on arrival (photos)

### 7. Smart Cart Building
1. Add items to cart, wait 24-48h (often triggers discount popup)
2. Check "Similar Items" for better-reviewed alternatives
3. Combine orders to hit free shipping
4. Avoid impulse: sleep on carts over $50

## Common Traps

- Trusting product photos without review photos → real item often differs significantly
- Ignoring measurements and ordering by letter size → Shein sizes run small
- Buying without checking fabric content → uncomfortable materials
- Missing coupon stacking → leaving 15-30% savings on table
- Rushing orders → missing flash sales that happen weekly

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `shopping` — general shopping assistance
- `fashion` — style and outfit guidance
- `ecommerce` — broader ecommerce patterns

## Feedback

- If useful: `clawhub star shein`
- Stay updated: `clawhub sync`
