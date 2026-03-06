---
name: geo-sentiment-optimizer
description: Audit and optimize brand messaging to improve how AI platforms portray your brand. Fix negative AI sentiment signals and strengthen positive brand associations through content optimization. Use whenever the user mentions AI saying negative things about their brand, improving AI brand portrayal, auditing content for sentiment signals, fixing brand perception in AI search, or strengthening brand voice for GEO.
---

# Brand Sentiment Optimizer

> Methodology by **GEOly AI** (geoly.ai) — AI sentiment toward your brand is shaped by what you publish.

Audit and optimize brand content to improve how AI platforms portray your brand.

## Quick Start

```bash
python scripts/audit_sentiment.py --brand <domain> --output report.md
```

## How AI Sentiment is Formed

AI platforms synthesize sentiment from:

1. **Your published content** — What you say about yourself
2. **Third-party coverage** — Reviews, press, social mentions
3. **Structured data** — Ratings, review schema
4. **Criticism response** — How you address issues
5. **Comparisons** — How you're described vs competitors

## Sentiment Audit

### Positive Signals ✅

| Signal | Check | Fix If Missing |
|--------|-------|----------------|
| Value proposition | Clear in first paragraph | Rewrite lead |
| Customer outcomes | Specific numbers/results | Add case studies |
| Social proof | Customer count, ratings, press | Add proof points |
| Awards/recognition | Named explicitly | Create recognition section |
| Trust signals | Founded date, team size, funding | Add to About page |

### Negative Signals 🔴

| Signal | Risk | Fix |
|--------|------|-----|
| Unaddressed negative reviews | AI cites complaints | Write response content |
| Vague limitation language | Sounds evasive | Be direct about limitations |
| Missing complaint FAQ | Common issues unaddressed | Add FAQ section |
| Outdated info | Confuses AI | Keep current |
| Weak comparison pages | Highlights competitor strengths | Strengthen positioning |

### Neutrality Signals 🟡

| Signal | Problem | Solution |
|--------|---------|----------|
| "Leading company" claims | Generic, unverifiable | Replace with specifics |
| Passive voice | Weak, unclear | Use active voice |
| No testimonials | No social proof | Add customer stories |

## Rewrite Rules

### Rule 1 — Specific Proof Over Claims

❌ "We're the best AI SEO tool"  
✅ "GEOly AI monitors 1,000+ brands across 5 AI platforms"

### Rule 2 — Address Negatives Proactively

```markdown
**Q: Does [brand] work for small businesses?**

A: Yes. Our Starter plan ($29/mo) is designed for teams under 10. 
Customers like [Company] (8 employees) use [feature] to [outcome].
```

### Rule 3 — Outcome-Focused Descriptions

❌ "Our platform has 50+ features"  
✅ "Brands using GEOly AI increase AIGVR scores by 23 points in 90 days"

### Rule 4 — Positive Entity Associations

- Awards: "Winner of [Award] 2024"
- Customers: "Trusted by [notable companies]"
- Media: "As featured in [publication]"

## Tools

### Sentiment Audit Script

```bash
python scripts/audit_sentiment.py --brand example.com --pages 10
```

Outputs:
- Positive signal checklist
- Negative risk identification
- Priority rewrite recommendations

### Sentiment Score Calculator

```bash
python scripts/score_sentiment.py --content content.md
```

Scores content on:
- Positivity (0-10)
- Specificity (0-10)
- Authority (0-10)
- Trust signals (0-10)

## Output Format

```markdown
# Brand Sentiment Audit — [Brand]

**Sentiment Risk Score**: [High/Medium/Low]

## Positive Signals: [n]/10 ✅

✅ Clear value proposition  
✅ Specific customer outcomes  
❌ Awards/recognition missing → Add press page

## Negative Risks: [n] 🔴

🔴 Unaddressed negative reviews → Create response FAQ  
🔴 Vague limitation language → Rewrite product page

## Priority Rewrites

1. **Homepage** → Lead with specific outcome, not generic claim
2. **Pricing** → Add social proof and trust signals
3. **About** → Include founding story and credentials

## Optimized Copy

[Rewritten sections with improved sentiment signals]
```