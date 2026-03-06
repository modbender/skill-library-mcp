# 7-Dimension Evaluation

Use this as a quick checklist before delivering important work. Takes 30 seconds.

## The Dimensions

| # | Dimension | Core Question | Red Flags |
|---|-----------|--------------|-----------|
| 1 | **Correctness** | Does it solve the stated problem? | Solving wrong problem, misread requirements |
| 2 | **Completeness** | Edge cases covered? | Missing null checks, unhappy paths ignored |
| 3 | **Clarity** | Immediately understandable? | Dense code, no comments on complex logic |
| 4 | **Robustness** | What could break this? | No error handling, brittle assumptions |
| 5 | **Efficiency** | Unnecessary complexity? | Over-engineering, premature optimization |
| 6 | **Alignment** | What user actually wants? | Letter vs spirit of request |
| 7 | **Pride** | Would I sign my name? | Gut check on quality |

## Quick Scoring

For each dimension: 1-10 score (10 = excellent)

- **All ≥7** → Clear to deliver
- **Any <7** → Address before delivering
- **Any <5** → Major revision needed

## Common Failure Modes

### Correctness
- Solved the problem I assumed, not the one stated
- Optimized for wrong metric

### Completeness  
- "Happy path only" implementation
- Missing input validation

### Clarity
- Future-me won't understand this
- Magic numbers without explanation

### Robustness
- Works on my machine™
- No timeout, no retry, no fallback

### Efficiency
- 200 lines when 20 would do
- Premature abstraction

### Alignment
- Technically correct, practically useless
- User asked for X, I delivered adjacent Y

### Pride
- "It works" ≠ "It's good"
- Would be embarrassed if someone reviewed this
