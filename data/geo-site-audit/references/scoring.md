# GEO Audit Scoring Methodology

## Scoring System

### Point Values
- **✅ Pass** = 1 point
- **❌ Fail** = 0 points
- **⚠️ Partial** = 0.5 points

### Grade Scale

| Points | Grade | Interpretation | Action Needed |
|--------|-------|----------------|---------------|
| 26-29 | A+ | Excellent GEO readiness | Maintain current state |
| 22-25 | A | Strong with minor issues | Small optimizations |
| 18-21 | B | Good, some gaps | Address medium priority items |
| 14-17 | C | Fair, needs work | Tackle high priority gaps |
| 10-13 | D | Poor, major issues | Comprehensive overhaul |
| 0-9 | F | Critical problems | Immediate remediation required |

## Dimension Weighting

### Default: Equal Weighting
All 29 checks worth 1 point each (total 29 points).

### Alternative: Priority Weighting
If you want to emphasize certain areas:

```json
{
  "accessibility": 1.2,
  "structured_data": 1.2,
  "content": 1.0,
  "technical": 0.8
}
```

This reflects that AI accessibility and structured data have outsized impact on GEO.

## Check Categories

### Critical (Must Fix)
These directly block AI crawlers:
- robots.txt blocking AI bots
- No llms.txt when expected
- noindex on key pages
- Site behind login/paywall

### High Impact (Fix Soon)
Major improvement opportunities:
- Missing Organization schema
- Missing WebSite schema
- No JSON-LD at all
- No clear answer sentences

### Medium Impact (Nice to Have)
Incremental improvements:
- BreadcrumbList schema
- HowTo schema
- Twitter Card tags
- Hreflang implementation

### Low Impact (Polish)
Minor optimizations:
- Exact llms.txt formatting
- Schema validation warnings
- 404 page styling

## Calculating Dimension Scores

```
Dimension Score = (Sum of check points / Number of checks) × 100
```

Example: AI Accessibility with 8/10 points = 80%

## Reporting

### Summary Format
```
GEO Readiness Score: 24/29 (A)

By Dimension:
├── AI Accessibility:     8/10  (80%)
├── Structured Data:      9/11  (82%)
├── Content Citability:   5/7   (71%)
└── Technical Setup:      6/7   (86%)
```

### Trending
Track scores over time to measure improvement:

| Date | Score | Change | Notes |
|------|-------|--------|-------|
| 2024-01 | 18/29 | - | Baseline |
| 2024-02 | 22/29 | +4 | Added schemas |
| 2024-03 | 25/29 | +3 | Fixed robots.txt |

## Benchmarks

Based on industry analysis:

| Metric | Average | Top 10% |
|--------|---------|---------|
| Overall Score | 16/29 | 26/29 |
| Has llms.txt | 12% | 100% |
| Valid Schema | 45% | 95% |
| AI-Crawlable | 78% | 100% |

Use these to contextualize your results.