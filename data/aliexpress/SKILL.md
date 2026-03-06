---
name: Aliexpress
slug: aliexpress
version: 1.0.0
description: Navigate Aliexpress as buyer, seller, or dropshipper with vendor evaluation, price comparison, and scam detection.
metadata: {"clawdbot":{"emoji":"🛒","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User needs help with Aliexpress purchases, selling, or sourcing. Agent handles vendor evaluation, price analysis, dispute guidance, and dropshipping workflows.

## Quick Reference

| Topic | File |
|-------|------|
| Vendor signals | `vendors.md` |
| Dropshipping | `dropshipping.md` |

## Core Rules

### 1. Vendor Evaluation Beyond Stars
Stars alone are misleading. Check these signals in order:

| Signal | Red Flag | Green Flag |
|--------|----------|------------|
| Store age | <1 year | >3 years |
| Followers | <1000 | >10,000 |
| Response rate | <80% | >95% |
| Positive feedback | <95% | >98% |
| Photo reviews | Stock photos only | Real customer photos |

If user asks "is this seller trustworthy?" — require ALL five signals.

### 2. Real Cost Calculation
Aliexpress price ≠ landed cost. Always compute:
```
Landed Cost = Item Price + Shipping + Import Tax (if >$150) + Payment Fee (2-3%)
```
- Shipping varies 3-40 days depending on method
- "Free shipping" often means 40-60 day wait
- ePacket/AliExpress Standard = 15-25 days typical

### 3. Same Product Different Vendors
Before recommending a purchase, search same product across vendors:
- Price can vary 50-200% for identical items
- Check if dropshipping from same factory (similar photos)
- Lower price + low reviews = test batch risk

### 4. Dispute Timing
Aliexpress dispute window rules:
- Open dispute before buyer protection expires
- Wait 10+ days past delivery estimate before "not received"
- Document everything with screenshots
- Partial refund often better than full dispute loss

### 5. Dropshipping Specifics
See `dropshipping.md` for margin calculation and supplier vetting.

Key rule: Never source from vendors with <98% positive and <2 years history.

### 6. Scam Detection Patterns
Common scams to warn about:
- Price too good (>50% below others) = bait and switch
- "Ships from local warehouse" but no proof = fake
- Brand names at 90% discount = counterfeit
- Empty box scam = always request tracking with photos

## Common Traps

- Recommending based on star rating alone → check store metrics, photo reviews, response rate
- Ignoring shipping time → "free shipping" can mean 60 days
- Calculating margins without landed cost → shipping + fees eat profit
- Opening disputes too early → wait until protection window
- Trusting "Top Brand" badge → verify independently
