# Evaluation Dimensions — Pipeline Retro Scoring Rubric

8 axes for scoring pipeline process quality. Overall score = weighted average.

## Weights

| Dimension | Weight | What it measures |
|-----------|--------|-----------------|
| Efficiency | 25% | Productive vs wasted iterations |
| Stability | 20% | Pipeline restarts and circuit breaker hits |
| Fidelity | 20% | Acceptance criteria and task completion |
| Quality | 15% | Test pass rate and build status |
| Commits | 5% | Conventional commit format adherence |
| Docs | 5% | Plan/spec freshness and completeness |
| Signals | 5% | Clean pipeline signal handling |
| Speed | 5% | Total pipeline duration |

## Scoring Scale

### Efficiency (25%)

| Score | Waste % | Description |
|-------|---------|-------------|
| 10 | 0% | Every iteration produced useful work |
| 9 | 1-5% | Near-perfect, minor retries |
| 8 | 6-10% | Slight waste, acceptable |
| 7 | 11-20% | Some waste, within tolerance |
| 6 | 21-30% | Noticeable waste |
| 5 | 31-40% | Significant waste |
| 4 | 41-50% | Half of iterations wasted |
| 3 | 51-65% | Majority wasted |
| 2 | 66-80% | Severe waste |
| 1 | >80% | Pipeline mostly spinning wheels |

### Stability (20%)

| Score | Restarts | Max-iter hits | Description |
|-------|----------|---------------|-------------|
| 10 | 0 | 0 | Single clean run |
| 8 | 1 | 0 | One restart, no ceiling hits |
| 7 | 1 | 1 | One restart with ceiling hit |
| 5 | 2 | 1 | Multiple restarts |
| 3 | 2-3 | 2+ | Repeated ceiling hits |
| 1 | >3 | 2+ | Unstable, constant restarts |

### Fidelity (20%)

| Score | Criteria Met | Tasks Done | Description |
|-------|-------------|------------|-------------|
| 10 | 100% | 100% | All acceptance criteria and tasks complete |
| 9 | 100% | >90% | All criteria met, minor tasks remaining |
| 8 | >90% | >90% | Near-complete |
| 7 | >90% | 70-90% | Criteria mostly met |
| 5 | 70-90% | 50-70% | Significant gaps |
| 3 | 50-70% | <50% | Major gaps |
| 1 | <50% | <30% | Most criteria unmet |

### Quality (15%)

| Score | Test Pass Rate | Build | Description |
|-------|---------------|-------|-------------|
| 10 | 100% | PASS | All tests pass, build clean |
| 8 | >95% | PASS | Minor test failures |
| 6 | 80-95% | PASS | Some test failures |
| 4 | 60-80% | PASS | Notable failures |
| 2 | <60% | PASS | Many failures |
| 1 | any | FAIL | Build broken |
| N/A | - | - | No tests configured (score as 5) |

### Commits (5%)

| Score | Conventional % | Description |
|-------|---------------|-------------|
| 10 | 100% | All commits follow conventional format |
| 7 | >90% | Most commits conventional |
| 4 | 70-90% | Some non-conventional |
| 1 | <70% | Mostly non-conventional |

### Docs (5%)

| Score | Condition | Description |
|-------|-----------|-------------|
| 10 | All plans complete, specs with SHAs | Fully documented |
| 7 | Plans complete, no SHAs | Plans done but no commit tracking |
| 4 | Some plans incomplete | Partial documentation |
| 1 | Plans missing or all incomplete | No documentation trail |

### Signals (5%)

| Score | Condition | Description |
|-------|-----------|-------------|
| 10 | Clean signals, no doubled tags, no missing signals | Perfect signal handling |
| 7 | Minor doubled tags (no impact) | Cosmetic issues only |
| 4 | Missing signals (caused extra iterations) | Signal gaps caused waste |
| 1 | Wrong signals or systematic signal failures | Signal system broken |

### Speed (5%)

| Score | Duration | Description |
|-------|----------|-------------|
| 10 | <30 min | Fast pipeline |
| 8 | 30-60 min | Reasonable |
| 6 | 1-2 hours | Acceptable for complex projects |
| 4 | 2-4 hours | Slow |
| 2 | 4-8 hours | Very slow |
| 1 | >8 hours | Excessively slow |

## Computing Overall Score

```
overall = (
  efficiency * 0.25 +
  stability  * 0.20 +
  fidelity   * 0.20 +
  quality    * 0.15 +
  commits    * 0.05 +
  docs       * 0.05 +
  signals    * 0.05 +
  speed      * 0.05
)
```

Round to 1 decimal place. Display as `{score}/10`.
