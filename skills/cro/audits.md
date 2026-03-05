# Conversion Audits

## Funnel Audit

### Step 1: Map the Funnel
```
Traffic → Landing → Product/Pricing → Cart/Signup → Checkout → Confirmation
```

### Step 2: Get Conversion Rates Per Step
- Pull from GA4, Mixpanel, or custom events
- Calculate both step-to-step AND overall conversion
- Segment by device, traffic source, user type

### Step 3: Identify Biggest Drop-offs
- Which step has the largest absolute drop?
- Which step is below industry benchmark?
- Where are mobile users dropping vs desktop?

### Step 4: Quantify Impact
```
Revenue Impact = (Target CVR - Current CVR) × Traffic × AOV
```

Example: If checkout converts 60% → 70% improvement:
- 10,000 monthly checkouts
- $50 AOV
- Impact = 0.10 × 10,000 × $50 = $50,000/month

### Step 5: Prioritize Fixes
1. High traffic + low conversion = highest priority
2. Easy wins first (copy, button color)
3. Structural changes (flow, steps) = more effort

## Form Audit

### Field-Level Analysis
Track for each field:
- Time to complete
- Error rate
- Abandonment rate
- Refill rate

### Red Flags
- Phone fields (biggest friction)
- "Confirm email" (unnecessary in 2024)
- Required fields that could be optional
- Fields with high error rates
- Dropdowns with 20+ options

### Best Practices
- Ask only what you need NOW
- Progressive profiling > long forms
- Smart defaults (detect country, currency)
- Inline validation (not on submit)
- Mobile-optimized inputs (tel, email types)

## Speed Audit

### Core Web Vitals Targets
| Metric | Good | Needs Work | Poor |
|--------|------|------------|------|
| LCP | <2.5s | 2.5-4s | >4s |
| FID | <100ms | 100-300ms | >300ms |
| CLS | <0.1 | 0.1-0.25 | >0.25 |

### Conversion Impact (Industry Data)
- 1s delay = 7% conversion drop
- 2s delay = 40% user bounce
- 3s+ = 53% mobile abandonment

### Quick Wins
1. Compress images (WebP, AVIF)
2. Lazy load below-fold content
3. Remove unused JS/CSS
4. Use CDN for static assets
5. Preconnect to critical origins

## Mobile Audit

### Check These Specifically
- CTA visible without scrolling?
- Buttons min 44px tap target?
- Form fields easy to fill on mobile?
- No horizontal scrolling?
- Text readable without zooming?

### Common Mobile Conversion Killers
- Sticky headers eating screen space
- Pop-ups that cover CTA
- Forms that zoom on focus
- Slow-loading hero images
- Click-to-call not implemented

## Checkout Audit

### Friction Checklist
- [ ] Guest checkout available?
- [ ] Progress indicator shown?
- [ ] Security badges visible?
- [ ] Clear shipping/tax before payment?
- [ ] Multiple payment options?
- [ ] Error messages are helpful?
- [ ] Back button works correctly?

### Cart Abandonment Recovery
- Send email within 1 hour (not 24h)
- Include cart contents + images
- Consider incentive (free shipping > % off)
- 3-email sequence: reminder, urgency, last chance

## Competitor Audit

### What to Capture
1. Above-fold layout and CTA placement
2. Value prop messaging
3. Trust signals (logos, testimonials)
4. Form length and fields
5. Pricing presentation
6. Urgency/scarcity tactics
7. Mobile experience

### Scoring Template
| Element | Competitor A | Competitor B | Us |
|---------|--------------|--------------|-----|
| Clear CTA | 8 | 6 | 7 |
| Social proof | 9 | 7 | 5 |
| Form friction | 6 | 8 | 4 |
| Speed | 7 | 5 | 8 |
