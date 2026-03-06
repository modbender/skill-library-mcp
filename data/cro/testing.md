# A/B Testing Methodology

## Before Starting a Test

### Sample Size Calculation
```
n = (2 × (Zα + Zβ)² × p × (1-p)) / MDE²

Where:
- Zα = 1.96 (95% confidence)
- Zβ = 0.84 (80% power)
- p = baseline conversion rate
- MDE = minimum detectable effect
```

**Quick reference:**
| Baseline CVR | 5% MDE | 10% MDE | 20% MDE |
|--------------|--------|---------|---------|
| 2% | 30,000/variant | 8,000 | 2,000 |
| 5% | 12,000/variant | 3,000 | 800 |
| 10% | 6,000/variant | 1,500 | 400 |

### Test Duration
- Minimum 7 days (capture day-of-week effects)
- Maximum 4 weeks (avoid history effects)
- Never stop early on positive results

## Statistical Significance

### When to Call a Winner
- p-value < 0.05 (95% confidence)
- Reached pre-calculated sample size
- Test ran for minimum duration
- Result is consistent across segments

### Common Mistakes
- **Peeking** — Checking results daily inflates false positives
- **Multiple variants** — 4+ variants need Bonferroni correction
- **Ignoring segments** — Winner overall may lose in key segments
- **Novelty effect** — New always gets more attention initially

## Variant Generation Frameworks

### Headlines (test one at a time)
1. **Direct benefit:** "Get [outcome] in [timeframe]"
2. **Social proof:** "[Number] [people] already [action]"
3. **Curiosity gap:** "The [adjective] way to [outcome]"
4. **Pain-agitate:** "Stop [pain]. Start [benefit]"
5. **Specificity:** "[Specific number]% [improvement] in [metric]"

### CTAs
- Action verbs: Get, Start, Join, Claim, Unlock
- Add urgency: Now, Today, Free
- Reduce friction: No credit card, Cancel anytime
- Value-first: "Get my free X" vs "Sign up"

## Test Prioritization (ICE Framework)

Score each test idea 1-10:
- **Impact:** How much will conversion improve?
- **Confidence:** How sure are we this works?
- **Ease:** How easy to implement?

ICE Score = (Impact + Confidence + Ease) / 3

Prioritize highest scores first.

## Sequential Testing vs Fixed Horizon

### Fixed Horizon (Traditional)
- Pre-set sample size
- Wait until complete
- Higher validity

### Sequential Testing
- Can stop early if effect is large
- Requires adjusted significance thresholds
- Use tools like Optimizely's Stats Engine

## Post-Test Actions

1. **Document results** — Hypothesis, variants, metrics, learning
2. **Implement winner** — Ship immediately, don't delay
3. **Monitor post-ship** — Confirm live results match test
4. **Update playbook** — Add learning to patterns
5. **Plan follow-up** — Next iteration based on findings
