# Growth — CRO, Upsells, Retention, Benchmarks

## Checkout Abandonment Recovery

### Email Sequence
| Email | Timing | Content | Discount |
|-------|--------|---------|----------|
| 1 | 1 hour | "You left items behind" + cart contents | None |
| 2 | 24 hours | "Still interested?" + social proof | None |
| 3 | 72 hours | "Last chance" + urgency | 10% or free shipping |

**Expected recovery rate:** 5-15% of abandoned carts

### Exit-Intent Popup
**Use when:** Cart >€30, not returning visitor
**Copy:** "Wait! Get 10% off your first order" (email capture)
**Don't:** Show every time, show to returning visitors, show on mobile (annoying)

## Upsells & Cross-sells

### Placement Priority
1. **Cart page** — "Frequently bought together" (highest conversion)
2. **Post-purchase page** — One-click add (no re-enter payment)
3. **Checkout page** — Small add-ons only (don't distract from completing)
4. **Product page** — Related products (lower intent)

### What to Offer
| Strategy | Example | Expected lift |
|----------|---------|---------------|
| Complementary | Phone + case | +15-25% AOV |
| Upgrade | 64GB → 128GB | +10-20% AOV |
| Bundle discount | Buy 2, get 10% off | +20-30% AOV |
| Protection plan | Warranty | +5-10% revenue |

### Post-Purchase Upsell
Show on thank-you page:
- Related product at 15% discount
- One-click add to existing order
- Time-limited (10 min countdown)

**Conversion:** 2-5% of buyers add item

## Average Order Value (AOV)

### Tactics with Expected Impact
| Tactic | Implementation | Expected Impact |
|--------|----------------|-----------------|
| Free shipping threshold | AOV × 1.25 | +10-15% AOV |
| Bundle discounts | "Complete the look" | +15-25% AOV |
| Volume discounts | Buy 3+, save 15% | +20-30% AOV |
| Gift with purchase | Free item at €X | +8-12% AOV |
| Tiered pricing | Show "most popular" middle option | +10-20% AOV |

### Free Shipping Calculator
```
If current AOV = €40
Set threshold = €50 (AOV × 1.25)
Show progress bar: "Add €12 more for free shipping!"
```

## Customer Lifetime Value (LTV)

### Basic Calculation
```
LTV = AOV × Purchase Frequency × Customer Lifespan
```

**Example:**
- AOV: €50
- Purchases per year: 3
- Average customer stays: 2 years
- LTV = €50 × 3 × 2 = €300

### CAC Ratio
**Healthy:** LTV:CAC = 3:1 or better
- LTV €300, CAC should be ≤€100
- If CAC >€100, you're losing money acquiring customers

### Retention Tactics by Stage

| Stage | Timing | Tactic |
|-------|--------|--------|
| Post-purchase | Day 7 | "How's your purchase?" email |
| Post-purchase | Day 14 | Request review + discount for next |
| Nurture | Day 30 | Related products email |
| Nurture | Day 60 | "We miss you" + 15% off |
| Win-back | Day 90 | "Come back" + 20% off |
| Win-back | Day 180 | Last attempt + best offer |

### When is Customer "Lost"?
```
If no purchase in (3 × average purchase cycle):
  → Customer considered churned
  → Move to win-back sequence
```

## Product Page Conversion

### Must-Haves
- [ ] High-quality images (multiple angles, zoom)
- [ ] Price clearly visible (no "request quote")
- [ ] Stock status (creates urgency if low)
- [ ] Shipping estimate for visitor's location
- [ ] Reviews (minimum 5 for credibility)
- [ ] Clear CTA button (contrasting color)

### Trust Elements
| Element | Placement | Impact |
|---------|-----------|--------|
| Reviews with photos | Below main image | +15-25% conversion |
| "X people viewing" | Near CTA | +5-10% conversion |
| Money-back guarantee | Near CTA | +10-15% conversion |
| Secure payment badges | Near CTA | +3-5% conversion |
| Delivery date estimate | Near CTA | +5-10% conversion |

### Urgency/Scarcity
**Ethical use:**
- Real stock count ("Only 3 left")
- Real deadline ("Sale ends Sunday")
- Real demand ("12 sold today")

**Avoid:**
- Fake countdown timers that reset
- "Last one!" when you have 100
- Pressure tactics that erode trust

## A/B Testing

### What to Test (Priority Order)
1. **Headlines** — Biggest impact, fastest to test
2. **CTA button** — Color, text, size
3. **Price display** — With/without anchoring, payment plans
4. **Social proof** — Position, format, quantity
5. **Layout** — Only after above optimized

### Sample Size Calculator
```
Minimum visitors per variation:
n = (16 × p × (1-p)) / MDE²

p = baseline conversion rate
MDE = minimum detectable effect (e.g., 0.05 for 5% lift)
```

**Example:**
- Baseline conversion: 3% (p = 0.03)
- Want to detect 10% relative lift (MDE = 0.003)
- n = (16 × 0.03 × 0.97) / 0.003² ≈ 52,000 per variation

**Rule of thumb:** At least 100 conversions per variation before concluding.

### Duration
- Minimum: 1 full week (capture day-of-week effects)
- Maximum: 4 weeks (avoid sample pollution)
- Stop early only if >99% statistical significance

## Mobile Optimization

### Critical Elements
| Element | Requirement |
|---------|-------------|
| LCP (Largest Contentful Paint) | <2.5 seconds |
| Add to cart | Sticky/floating button |
| Checkout | Single page or minimal steps |
| Payment | Apple Pay / Google Pay enabled |
| Images | Lazy load, compressed, WebP |

### Mobile Checkout Checklist
- [ ] Auto-fill enabled (addresses, cards)
- [ ] Number keyboard for phone/card fields
- [ ] Progress indicator (step 1 of 3)
- [ ] Guest checkout option
- [ ] Express payment buttons above fold

### Mobile vs Desktop Benchmarks
| Metric | Desktop | Mobile |
|--------|---------|--------|
| Conversion rate | 3-4% | 1.5-2% |
| Bounce rate | 40-50% | 50-60% |
| AOV | Higher | 10-20% lower |
| Cart abandonment | 70% | 85% |

**Implication:** Mobile drives traffic, desktop closes sales. Optimize mobile for email capture and retargeting.
