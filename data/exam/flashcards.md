# Flashcards

Spaced repetition for memorization.

---

## Generating Cards

From source material, extract:
- **Term → Definition**
- **Concept → Explanation**
- **Question → Answer**
- **Acronym → Expansion**
- **Process → Steps**

### Card Format
```json
{
  "front": "What is the CAP theorem?",
  "back": "In distributed systems, you can only guarantee 2 of 3: Consistency, Availability, Partition tolerance",
  "topic": "distributed-systems",
  "tags": ["theory", "tradeoffs"]
}
```

---

## Card Types

### Basic (Front/Back)
```
Front: Term or question
Back: Definition or answer
```

### Cloze (Fill in blank)
```
"The {{c1::CAP theorem}} states that distributed systems 
can only guarantee {{c2::two of three}} properties."
```

### Reversed
```
Front: Definition
Back: What term does this describe?
```

### Image Occlusion
```
Front: Diagram with part hidden
Back: Full diagram with labels
```

---

## Spaced Repetition

### Algorithm (SM-2 simplified)
After each review, user rates:
- **Again (1)** — Reset interval to 1 day
- **Hard (2)** — Interval × 1.2
- **Good (3)** — Interval × 2.5
- **Easy (4)** — Interval × 3.0

### Intervals
| Rating | Next Review |
|--------|-------------|
| New card | 1 day |
| Again | 1 day |
| Hard | Previous × 1.2 |
| Good | Previous × 2.5 |
| Easy | Previous × 3.0 |

### Daily Queue
1. Due cards first (overdue prioritized)
2. New cards (limit per day)
3. Review cards (oldest first)

---

## Session Flow

```
📚 Flashcards: AWS Services (23 due)

━━━━━━━━━━━━━━━━━━━━━━━━━━━
What service provides managed 
Kubernetes?
━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Show Answer]
```

After reveal:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Answer: Amazon EKS 
(Elastic Kubernetes Service)
━━━━━━━━━━━━━━━━━━━━━━━━━━━

How well did you know this?

[Again] [Hard] [Good] [Easy]
```

---

## Storage

```json
{
  "cards": [...],
  "reviews": [
    {"card_id": "c001", "date": "2024-02-13", "rating": 3, "interval": 4}
  ],
  "stats": {
    "total": 150,
    "mature": 89,
    "learning": 45,
    "new": 16
  }
}
```

---

## Best Practices

**Creating cards:**
- One fact per card
- Keep fronts short
- Avoid yes/no questions
- Include context when needed
- Add images for visual concepts

**Reviewing:**
- Daily sessions (even 5 minutes)
- Be honest with ratings
- Don't over-add new cards
- Review weak topics more

**Maintenance:**
- Delete cards you've mastered
- Update outdated information
- Merge similar cards
- Tag for easy filtering
