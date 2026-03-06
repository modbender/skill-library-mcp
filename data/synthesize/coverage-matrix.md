# Coverage Matrix

## Building the Matrix

Map sources (rows) against themes/topics (columns):

```
| Source      | Theme A | Theme B | Theme C | Theme D |
|-------------|---------|---------|---------|---------|
| Source 1    | ██      | ██      | ░░      | ░░      |
| Source 2    | ░░      | ██      | ██      | ░░      |
| Source 3    | ██      | ░░      | ██      | ██      |
| Coverage    | 2/3     | 2/3     | 2/3     | 1/3     |
```

██ = covered, ░░ = not covered

## Analysis

### Strong Coverage (3+ sources)
- High confidence in synthesis
- Cross-validate claims
- Note consensus vs disagreement

### Moderate Coverage (2 sources)
- Acceptable confidence
- Flag if sources disagree
- Note limitations

### Weak Coverage (1 source)
- Flag explicitly: "Based solely on [source]"
- Seek additional sources if critical
- Don't over-generalize single-source claims

### Gap (0 sources)
- Acknowledge explicitly
- Either: seek sources, or note as limitation
- Never invent to fill gaps

## Pre-Synthesis Checklist

- [ ] Every source appears in at least one theme
- [ ] No critical theme has 0 coverage
- [ ] Single-source themes are flagged
- [ ] Coverage aligns with synthesis scope

## When to Expand Research

- Critical theme has <2 sources
- High-stakes decision depends on weak coverage
- User specifically needs depth on gap area
