# Scoring Rubric

## Dimension 1: Technical Infrastructure (8 points → 10)

| Component | Points | Criteria |
|-----------|--------|----------|
| llms.txt | 0-2 | 0=Missing, 1=Exists but minimal, 2=Comprehensive |
| robots.txt | 0-2 | 0=Blocks AI, 1=No explicit block, 2=Explicit allow |
| Schema.org | 0-3 | 0=None, 1=1 type, 2=2-3 types, 3=4+ types valid |
| HTTPS/Perf | 0-1 | 0=Issues, 1=All pass |

### Conversion to 10-point scale
```
tech_score = (llms + robots + schema + https) / 8 * 10
```

---

## Dimension 2: Content Structure (10 points)

| Component | Points | Criteria |
|-----------|--------|----------|
| Direct answer | 0-3 | 0=Buried/missing, 1=Present, 2=Early, 3=Immediate |
| FAQ presence | 0-3 | 0=None, 1=Mentioned, 2=1-2 sections, 3=3+ with schema |
| Headers | 0-2 | 0=Poor, 1=Present but issues, 2=Excellent hierarchy |
| Data/citations | 0-2 | 0=None, 1=Sparse, 2=Multiple recent citations |

---

## Dimension 3: Entity Signals (9 points → 10)

| Component | Points | Criteria |
|-----------|--------|----------|
| Org schema | 0-3 | 0=None, 1=Incomplete, 2=Required fields, 3=Complete |
| sameAs links | 0-2 | 0=None, 1=1-2, 2=3+ |
| Brand consistency | 0-2 | 0=Major issues, 1=Minor issues, 2=Fully consistent |
| About page | 0-2 | 0=None, 1=Basic, 2=Comprehensive |

### Conversion to 10-point scale
```
entity_score = (org + sameas + consistency + about) / 9 * 10
```

---

## Dimension 4: Citation Content (9 points → 10)

| Component | Points | Criteria |
|-----------|--------|----------|
| Original research | 0-3 | 0=None, 1=Minor data, 2=One major piece, 3=Multiple |
| Comparisons | 0-2 | 0=None, 1=One, 2=Multiple |
| Definitions | 0-2 | 0=None, 1=Some, 2=Comprehensive |
| Content hubs | 0-2 | 0=Siloed, 1=Some clustering, 2=Strong hubs |

### Conversion to 10-point scale
```
citation_score = (research + comparisons + definitions + hubs) / 9 * 10
```

---

## Overall Score Calculation

```
overall = (technical + content + entity + citation) / 4
```

### Grade Assignment

| Overall | Grade | Status |
|---------|-------|--------|
| 9.0-10.0 | A+ | Excellent |
| 8.0-8.9 | A | Strong |
| 7.0-7.9 | B | Good |
| 6.0-6.9 | C | Fair |
| 5.0-5.9 | D | Poor |
| <5.0 | F | Critical |

---

## Priority Matrix

Use this to prioritize fixes:

| Impact | Effort | Priority | Action |
|--------|--------|----------|--------|
| High | Low | 🔴 Critical | Do first |
| High | High | 🟡 Important | Plan for next sprint |
| Low | Low | 🟢 Nice to have | Queue for later |
| Low | High | ⚪ Skip | Don't do |

### High Impact GEO Fixes

- Add llms.txt
- Fix robots.txt blocking
- Implement Organization schema
- Add FAQ schema to top pages
- Create comparison pages

### Low Effort GEO Fixes

- Update robots.txt
- Add sameAs links
- Fix @context to https
- Add H2 headers
- Include brand in first 100 words