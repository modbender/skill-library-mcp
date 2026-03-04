---
name: "Compare"
description: "Rigorous comparisons with confidence parity, weighted criteria, and research depth tracking."
---

## Core Principle

Comparisons fail when confidence is uneven. Only as reliable as the weakest-researched dimension.

## Protocol

```
Criteria → Research Parity → Confidence Check → Score → Present
```

### 1. Criteria

- Load domain defaults (`domains.md`)
- Overlay user preferences from memory
- If unknown: "What matters most here?"
- Output: Ranked criteria with weights (sum = 100%)

### 2. Research Parity (Critical)

**Research each item to equivalent depth before scoring.**

Track: `| Criterion | Item A sources | Item B sources |`

5 reviews for A but 1 for B? Research more for B first. Never score unbalanced data.

### 3. Confidence Check

Verify before presenting:
- Each item researched equally
- Each criterion researched equally
- Source quality comparable
- Data recency comparable

Fail any? Research more OR caveat explicitly.

### 4. Score

`Final = Σ(criterion_score × weight)` — Show the math.

### 5. Present

```
🆚 [A] vs [B]
📊 CRITERIA: [ranked by weight]
📈 SCORES: [table + confidence per row]
🎯 RESULT: [Winner] by [margin]
⚠️ CAVEATS: [imbalances]
💡 IF [X] MATTERS MORE: [alt winner]
```

## After

Note which criteria user focused on. Update `preferences.md` by category.

## Decline When

Research parity impossible, priorities unclear, or time insufficient. Partial > misleading.

References: `domains.md`, `confidence.md`, `traps.md`, `preferences.md`
