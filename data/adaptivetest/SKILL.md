---
name: adaptive-testing
description: Design and implement adaptive testing systems using Item Response Theory (IRT). Use when working with computerized adaptive tests (CAT), psychometric assessment, ability estimation, question calibration, test design, or IRT models (1PL/2PL/3PL). Covers test algorithms, stopping rules, item selection strategies, and practical implementation patterns for K-12, certification, placement, and diagnostic assessments.
---

# Adaptive Testing with IRT

Design computerized adaptive tests that measure ability efficiently and accurately using Item Response Theory.

## Core Concept

Adaptive tests adjust difficulty in real-time based on student responses. A correct answer → harder question. Incorrect → easier question. The result: accurate ability estimates in ~50% fewer questions than fixed-length tests.

**Key advantage:** Traditional tests waste time on too-easy or too-hard questions. Adaptive tests spend time where measurement matters most — near the student's ability level.

## Quick Decision Tree

| You need to... | See |
|----------------|-----|
| Understand IRT models and parameters | [IRT Fundamentals](#irt-fundamentals) |
| Design a new adaptive test | [Test Design Workflow](#test-design-workflow) |
| Choose item selection algorithm | [Item Selection](#item-selection-strategies) |
| Decide when to stop the test | [Stopping Rules](#stopping-rules) |
| Calibrate new questions | `references/calibration.md` |
| Implement CAT algorithm | `references/implementation.md` |

---

## IRT Fundamentals

### The 3-Parameter Logistic (3PL) Model

Most adaptive tests use the 3PL model. Each question has three parameters:

- **a** (discrimination) — How well the question differentiates ability levels. Higher = steeper curve. Typical range: 0.5 to 2.5
- **b** (difficulty) — The ability level where P(correct) = 0.5. Range: -3 to +3 (standardized scale)
- **c** (guessing) — Probability of guessing correctly. Usually 0.2 to 0.25 for multiple choice

**Probability of correct response:**
```
P(correct | ability, a, b, c) = c + (1 - c) / (1 + e^(-a(ability - b)))
```

**Simpler models:**
- **2PL:** Set c = 0 (no guessing parameter)
- **1PL (Rasch):** Set c = 0 and a = 1 for all items (only difficulty varies)

Use 3PL for high-stakes tests. Use 2PL/1PL when sample size is small (<500 responses per item).

### Information and Standard Error

**Information** measures how precisely an item estimates ability at a given level. Peak information occurs when ability ≈ difficulty (b parameter).

**Standard Error (SE)** is the inverse of information:
```
SE = 1 / sqrt(Information)
```

**Goal of CAT:** Maximize information (minimize SE) at the student's true ability level.

---

## Test Design Workflow

### 1. Define Test Specifications

- **Purpose:** Placement, diagnostic, certification, progress monitoring?
- **Content domain:** Single skill or multidimensional?
- **Target population:** What ability range (-3 to +3)?
- **Constraints:** Time limit, minimum/maximum length, content balance

### 2. Build Item Bank

**Minimum bank size:** 10× the average test length. For a 20-item CAT, you need ≥200 calibrated items.

**Distribution targets:**
- Difficulty (b): Spread across expected ability range
- Discrimination (a): Target 1.0 to 2.0 (high discrimination)
- Exposure: No item used >20% of the time

**Content balancing:** If testing math, ensure geometry/algebra/etc. are proportionally represented.

### 3. Choose Algorithms

Pick one from each category:

**Item selection:** (see below)
- Maximum Information
- Randomesque (MFI + exposure control)
- Content balancing

**Ability estimation:**
- Maximum Likelihood Estimation (MLE)
- Expected A Posteriori (EAP) — better for extreme scores
- Weighted Likelihood (WLE)

**Stopping rule:** (see below)
- Fixed length
- Standard error threshold
- Information threshold

### 4. Simulate Performance

Before going live, simulate 1000+ test sessions with known abilities. Check:
- Average test length
- SE at different ability levels
- Item exposure rates
- Content balance adherence

Adjust if needed.

---

## Item Selection Strategies

### Maximum Fisher Information (MFI)

**Rule:** Select the item with highest information at current ability estimate.

**Pros:** Optimal precision, shortest tests
**Cons:** Overuses "best" items, poor security

**Use when:** Pilot testing, low-stakes practice

### Randomesque (MFI + Exposure Control)

**Rule:** Select from top N items by information (e.g., top 5), choose randomly from that set.

**Pros:** Balances precision and security
**Cons:** Slightly longer tests than pure MFI

**Use when:** Operational tests, default choice

### a-Stratified

**Rule:** Start with high-discrimination items (high a), use mid-discrimination later.

**Pros:** Fast initial ability estimate
**Cons:** Complex to implement

**Use when:** Very large item banks, research settings

### Content Balancing

**Rule:** Track content area usage, prioritize underrepresented areas when selecting next item.

**Implementation:** Weight information by content constraint satisfaction.

**Use when:** Blueprint requirements, multidimensional tests

---

## Stopping Rules

### Fixed Length

Stop after N items (e.g., 20 questions).

**Pros:** Predictable time, simple
**Cons:** May over/under-test some students

**Use when:** Time limits matter, simple implementation needed

### Standard Error Threshold

Stop when SE < target (e.g., SE < 0.3).

**Pros:** Consistent precision across ability levels
**Cons:** Variable test length (harder to schedule)

**Typical targets:**
- Low-stakes: SE < 0.4
- Medium-stakes: SE < 0.3
- High-stakes: SE < 0.25

**Use when:** Precision matters more than time

### Combined Rule

Stop when (SE < target) OR (length ≥ max) OR (length ≥ min AND ability estimate stable).

**Use when:** Production systems (safest approach)

---

## Practical Considerations

### Starting Ability Estimate

**Options:**
1. Population mean (θ = 0)
2. Prior information (e.g., grade level, previous test)
3. First question is medium difficulty, estimate from there

Never start at extremes (-3 or +3).

### Handling Extreme Response Patterns

**All correct or all incorrect:** MLE fails. Use EAP or Bayesian prior to regularize.

**Rapid changes:** If ability estimate jumps >1.0, consider response anomaly (cheating, guessing).

### Exposure Control

Track how often each item is used. Flag items used >20% of the time. Consider:
- Randomesque selection (above)
- Sympson-Hetter method (advanced)
- Periodic item bank refresh

### Multidimensional IRT (MIRT)

If testing multiple skills (e.g., algebra + geometry), use separate ability estimates per dimension. Select items to balance information across dimensions.

**Warning:** MIRT requires larger item banks and more complex calibration.

---

## Common Mistakes

❌ **Too few items in bank** → High exposure, security risk
✅ Aim for 10× average test length

❌ **Poorly distributed difficulties** → Accurate only in narrow ability range  
✅ Spread items across -2 to +2 difficulty

❌ **Ignoring content balance** → May skip important topics  
✅ Build content constraints into item selection

❌ **Using MLE for all incorrect** → Returns -∞  
✅ Use EAP or cap estimates at -3/+3

❌ **No exposure control** → Same items every test  
✅ Use randomesque or Sympson-Hetter

---

## When to Load References

| Need | File |
|------|------|
| Calibrate new items (collect data, estimate parameters) | `references/calibration.md` |
| Implement CAT algorithm (code patterns, libraries) | `references/implementation.md` |

---

## Real-World Example: K-12 Math Placement

**Setup:**
- Item bank: 300 questions, b from -2 (basic) to +2 (advanced)
- Target: SE < 0.35 or max 25 questions
- Content: 40% algebra, 30% geometry, 30% statistics
- Algorithm: Randomesque (top 5), EAP estimation

**Flow:**
1. Start at θ = 0 (grade-level average)
2. Select item: b ≈ 0, content area needed
3. Student answers → update ability estimate (EAP)
4. Select next: maximize information at new θ, respect content balance, randomesque from top 5
5. Stop when SE < 0.35 or 25 questions reached
6. Report: ability estimate + placement recommendation

**Result:** Average 18 questions, 95% of students placed within ±0.5 grade levels of true ability.

---

## Further Reading

- Lord, F. M. (1980). *Applications of Item Response Theory to Practical Testing Problems*
- Wainer, H. (2000). *Computerized Adaptive Testing: A Primer* (2nd ed.)
- van der Linden, W. J., & Glas, C. A. W. (2010). *Elements of Adaptive Testing*

IRT packages:
- Python: `mirt`, `girth`, `catsim`
- R: `mirt`, `TAM`, `catR`
- Production: Custom implementation or AdaptiveTest.io
