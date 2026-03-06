# Timed Simulations

Mock exams that match real test conditions.

---

## Setting Up a Simulation

User specifies:
- **Question count** — Match real exam (e.g., 65 questions)
- **Time limit** — Match real exam (e.g., 90 minutes)
- **Question types** — Distribution (e.g., 80% MC, 20% scenario)
- **Passing score** — Target percentage (e.g., 72%)

```
"Start AWS SAA simulation: 65 questions, 130 minutes"
```

---

## During Simulation

### Timer Display
```
⏱️ Time: 1:45:32 remaining
📊 Progress: 23/65 questions
```

### Question Display
```
Question 23 of 65 [Flagged: 3]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Question text...]

A) Option A
B) Option B
C) Option C
D) Option D

[Flag] [Previous] [Next] [Submit All]
```

### Controls
- **Flag** — Mark for review
- **Previous/Next** — Navigate
- **Submit All** — End exam early

---

## End of Simulation

### Results Summary
```
📊 Simulation Complete: AWS SAA

Score: 52/65 (80%) ✅ PASS
Time used: 1:58:42 / 2:10:00
Passing: 72%

By Domain:
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Design Resilient:     18/22 (82%) ✅
Design Performant:    14/18 (78%) ✅
Design Secure:        12/15 (80%) ✅
Design Cost-Optimized: 8/10 (80%) ✅

Flagged questions: 3 (2 correct, 1 wrong)

[Review Wrong] [Review All] [Retake]
```

---

## Review Mode

After simulation, review each question:

```
Question 15 ❌ INCORRECT

Your answer: B
Correct answer: C

[Full question and options displayed]

Explanation:
[Why C is correct and B is wrong]

Related topics: VPC, Security Groups

[Previous] [Next] [Back to Summary]
```

---

## Simulation Types

### Full Mock
- Complete exam replica
- Real time pressure
- No hints or feedback until end

### Practice Mode
- Same questions
- Immediate feedback after each
- Explanations shown
- No time pressure (optional)

### Quick Quiz
- 10-20 questions
- Focused on specific topic
- Timed or untimed

### Review Weak Areas
- Questions from topics with low scores
- Adaptive difficulty

---

## Matching Real Exams

| Exam | Questions | Time | Format |
|------|-----------|------|--------|
| AWS SAA | 65 | 130 min | MC, Multiple select |
| AWS SAP | 75 | 180 min | MC, Multiple select |
| PMP | 180 | 230 min | MC |
| CCNA | 100-120 | 120 min | MC, Drag-drop |

When user says exam name, match format automatically.

---

## Performance Over Time

Track simulation scores:
```json
{
  "simulations": [
    {"date": "2024-02-10", "score": 68, "time": 125},
    {"date": "2024-02-12", "score": 74, "time": 118},
    {"date": "2024-02-13", "score": 80, "time": 112}
  ]
}
```

Show trend:
```
📈 Simulation History

Feb 10: 68% (125 min) — needs improvement
Feb 12: 74% (118 min) — getting there
Feb 13: 80% (112 min) — ready! ✅

Trend: ↑12% improvement, ↓13 min faster
```
