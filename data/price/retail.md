# Retail & Electronics

## Price Verification Checks

- **"Was $X, now $Y" verification** — Check if item was EVER actually sold at $X. Amazon, Best Buy inflate original prices constantly.
- **Retailer-specific SKUs** — Same TV has different model numbers at Costco vs Best Buy. May be identical or missing features. Verify before comparing.
- **Unit price normalization** — When comparing different sizes (18oz vs 1.2kg), calculate price-per-unit. Stores hide or use inconsistent labels.

## Sale Detection

- **Price before sale** — Was the "40% off" price just the regular price with a yellow tag? Compare to 30-day average.
- **Sale timing patterns** — Most electronics: best prices Black Friday, Prime Day, back-to-school. Worst: holidays, tax season.
- **"Lightning deals" vs real deals** — Flash sales often match or exceed regular prices elsewhere.

## Total Cost Calculation

Include in final price:
- Listed price
- Shipping (not just "free" — check threshold requirements)
- Tax (varies by state/country, some exempt)
- Extended warranty (if typically needed for category)
- Return policy value (30-day vs 15-day has real value)
- Credit card protections (some cards add warranty)

## Shrinkflation Detection

- **Same price, less product** — Track package size changes. 16oz → 14.5oz = hidden 10% increase.
- **"New formula" = less product** — Product reformulations often mask size reductions.
- **Count changes** — 12-pack becomes 10-pack at same price.

## Coupon Stacking Value

When user has multiple coupons:
1. Calculate actual final price with stack
2. Check if threshold requirements add dead weight
3. Compare to waiting for better sale without coupons
4. Factor in coupon expiration pressure

## Price Match Policies

| Retailer | Matches | Proof Required | Notes |
|----------|---------|----------------|-------|
| Best Buy | Major competitors | Screenshot/URL | Excludes marketplace sellers |
| Target | Select competitors | Ad or website | Must be identical item |
| Walmart | None (ended 2023) | N/A | Price match discontinued |

When recommending price match: factor in gas/time cost of going to another store.
