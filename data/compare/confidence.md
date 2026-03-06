# Confidence Levels

Use when reporting scores in comparisons.

| Level | Definition | When to use |
|-------|------------|-------------|
| **High** | 3+ quality sources, consistent findings, recent data | Strong basis for scoring |
| **Medium** | 1-2 sources or minor inconsistencies | Reasonable but not definitive |
| **Low** | Single source, outdated, or conflicting data | Caveat the score |
| **Caveat** | Significant imbalance between items | State explicitly in output |

## Applying Confidence

In comparison output, show confidence per criterion:

```
| Criterion | Item A | Item B | Confidence |
|-----------|--------|--------|------------|
| Price     | 8      | 6      | High       |
| Quality   | 7      | 8      | Medium     |
| Support   | 5      | 7      | Low ⚠️     |
```

When confidence is Low or Caveat:
- Explicitly note in the ⚠️ CAVEATS section
- Suggest what additional research would increase confidence
- Offer to investigate further before user decides
