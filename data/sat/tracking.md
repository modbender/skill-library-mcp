# Progress Tracking System

## Score Tracking

Maintain in `~/sat/profile.md`:
```
## Score History
| Date | RW | Math | Total | Notes |
|------|----|----- |-------|-------|
| 2024-01-15 | 650 | 700 | 1350 | Diagnostic |
| 2024-02-01 | 680 | 720 | 1400 | Practice test 1 |
```

Update after every full practice test.

## Section-Level Tracking

For each section, track in `~/sat/sections/`:

**Reading & Writing (`rw.md`):**
```
## Domain Accuracy
- Craft and Structure: 78% (14/18 last test)
- Information and Ideas: 85% (11/13)
- Standard English: 65% (10/15) ← PRIORITY
- Expression of Ideas: 70% (7/10)

## Weak Topics
- Comma usage in complex sentences
- Transition word selection
- Vocabulary in context (advanced)
```

**Math (`math.md`):**
```
## Domain Accuracy
- Algebra: 88% (14/16)
- Advanced Math: 72% (11/15) ← PRIORITY
- Problem-Solving: 80% (8/10)
- Geometry/Trig: 67% (4/6) ← PRIORITY

## Weak Topics
- Quadratic word problems
- Circle equations
- Systems with no/infinite solutions
```

## Mistake Log

Track every wrong answer in `~/sat/mistakes/`:
```
## 2024-02-01 Practice Test
| Q# | Section | Topic | Error Type | Review Date |
|----|---------|-------|------------|-------------|
| 17 | RW | Transitions | Misread context | 2024-02-08 |
| 32 | Math | Quadratics | Calculation | 2024-02-05 |
| 41 | Math | Geometry | Concept gap | 2024-02-08 |
```

Error types:
- **Concept gap** — Didn't know how to solve
- **Calculation** — Knew method, made arithmetic error
- **Misread** — Read question wrong
- **Time pressure** — Rushed due to time
- **Careless** — Knew it, made silly mistake

## Time Analysis

Track time per question to identify slow areas:
```
## Timing Patterns
- RW average: 1.1 min/question (target: 1.2)
- Math average: 1.8 min/question (target: 1.6) ← TOO SLOW

Slowest topics:
- Geometry word problems: 2.5 min avg
- Reading inference: 1.8 min avg
```

## Score Prediction Model

Based on practice data, predict test day score:
```
Diagnostic: 1350
Practice avg (last 3): 1420
Improvement rate: +23 pts/week
Days until test: 21

Predicted score: 1450-1490
Confidence: Medium (need more practice tests)
```

Factors that affect prediction:
- Practice test conditions (timed? distraction-free?)
- Number of tests taken
- Score variance across tests
- Recency of practice
