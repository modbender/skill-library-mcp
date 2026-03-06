# Paywall A/B Testing

## Core Principles

### 1. Always Be Testing
Every paywall change should be A/B tested. Even "obvious" improvements fail 50% of the time.

### 2. Velocity Matters
More tests = more learnings = more revenue. Aim for 2-4 tests per month on paywalls.

### 3. Statistical Rigor
Bad test design leads to bad decisions. Get the fundamentals right.

---

## Key Metrics

### Primary Metrics
| Metric | Definition | Why it matters |
|--------|------------|----------------|
| Conversion rate | % of paywall views → trial/purchase | Direct impact |
| ARPU | Revenue ÷ all users | Captures price × conversion |
| Trial-to-paid | % of trials → paid | Trial quality signal |

### Secondary Metrics
| Metric | Definition | Watch for |
|--------|------------|-----------|
| Time to convert | Days from install → purchase | Urgency impact |
| Cancellation rate | % who cancel in period | Price sensitivity |
| LTV | Lifetime revenue per user | Long-term impact |

### Metric Hierarchy
1. **Short-term:** Conversion rate, ARPU
2. **Medium-term:** Trial-to-paid, 7-day cancellation
3. **Long-term:** LTV, 13-month revenue projection

**Warning:** A change that boosts conversion but increases cancellations can hurt long-term revenue.

---

## Sample Size Calculator

### Minimum Sample Per Variant

| Baseline Rate | Detectable Lift | Sample Needed |
|---------------|-----------------|---------------|
| 2% | 20% | ~10,000 |
| 5% | 20% | ~4,000 |
| 10% | 20% | ~2,000 |
| 20% | 20% | ~1,000 |

**Rule of thumb:** Need 100+ conversions per variant for reliable results.

### Duration
- Run test for full week minimum (day-of-week effects)
- Don't peek and stop early
- Set duration before starting

---

## Test Design

### Control vs Variant
- **Control:** Current paywall (A)
- **Variant:** New paywall (B)
- Split traffic 50/50 for fastest results
- Use 90/10 or 80/20 if variant is risky

### Randomization
- Randomize by user ID, not session
- Same user should always see same variant
- Check for selection bias (device type, geo, etc.)

### What NOT to Do
- ❌ Stop test when you see a winner (peeking)
- ❌ Run multiple tests on same screen simultaneously
- ❌ Change variant mid-test
- ❌ Ignore statistical significance

---

## Test Prioritization

### Impact × Effort Matrix

| Test Type | Impact | Effort | Priority |
|-----------|--------|--------|----------|
| Price points | High | Low | 1st |
| Plan display | High | Medium | 2nd |
| Layout redesign | High | High | 3rd |
| Headline copy | Medium | Low | 4th |
| Button color | Low | Low | Last |

### Prioritization Questions
1. How much of paywall traffic does this affect?
2. How big could the impact be?
3. How confident are we in the hypothesis?
4. How hard is implementation?

---

## Common Test Ideas

### Pricing Tests
- [ ] Different price points (±20%)
- [ ] Monthly vs annual default
- [ ] Discount amount (20% vs 30% vs 50%)
- [ ] Trial length (7 vs 14 days)

### Layout Tests
- [ ] Number of plans shown (2 vs 3)
- [ ] Plan card layout (horizontal vs vertical)
- [ ] Feature list vs carousel
- [ ] Dark vs light background

### Copy Tests
- [ ] Headline (outcome vs feature focus)
- [ ] Benefit framing
- [ ] CTA text variations
- [ ] Social proof type (reviews vs logos vs numbers)

### Placement Tests
- [ ] Onboarding timing (slide 3 vs slide 5)
- [ ] Contextual trigger point
- [ ] Campaign frequency

---

## Analyzing Results

### Statistical Significance
- Target 95% confidence (p < 0.05)
- Don't trust results below 90% confidence
- Use proper calculators (not gut feel)

### Segment Analysis
After overall winner is determined:
- New vs returning users
- iOS vs Android
- High-value vs low-value users
- Geographic segments

**Warning:** Segment analysis is exploratory. Don't cherry-pick winning segments.

### Documenting Results

For every test, record:
```
Test: [Name]
Hypothesis: [What we expected]
Variants: [A vs B description]
Duration: [Dates]
Sample: [N per variant]
Results: [Conversion rates, confidence]
Winner: [A/B/Inconclusive]
Learning: [What we learned]
Next: [Follow-up tests]
```

---

## Tools

### Mobile A/B Testing
- **RevenueCat** — Paywall experiments built-in
- **Superwall** — Remote paywalls + A/B
- **Firebase A/B Testing** — General purpose
- **Optimizely** — Enterprise

### Web A/B Testing
- **PostHog** — Open source, feature flags
- **LaunchDarkly** — Feature flags + experiments
- **VWO** — Visual editor + testing
- **Optimizely** — Enterprise

### Analytics
- **Amplitude** — User behavior, funnels
- **Mixpanel** — Event analytics
- **RevenueCat** — Subscription analytics

---

## Testing Cadence

### Recommended Schedule
- **Price testing:** Every 6-12 months
- **Layout testing:** Continuous (always have one running)
- **Copy testing:** When layout is stable
- **Placement testing:** Quarterly

### After Launch
1. Week 1-2: Collect baseline data
2. Week 3+: Start first test (pricing recommended)
3. Ongoing: 2-4 tests per month

### Seasonal Considerations
- Holiday periods may skew results
- Back-to-school, New Year, summer affect different apps
- Document seasonality for future reference

---

## Common Mistakes

### Test Design Mistakes
- Stopping test early because variant "looks good"
- Running too many variants (A/B/C/D/E)
- Not accounting for novelty effect
- Ignoring long-term metrics

### Analysis Mistakes
- Celebrating small lifts (2% lift with low confidence)
- Segment cherry-picking
- Ignoring negative secondary metrics
- Not documenting learnings

### Implementation Mistakes
- Variant shows to wrong users (randomization bug)
- Variant differs in unintended ways
- Mobile vs web inconsistency
- Not QA-ing variants before launch
