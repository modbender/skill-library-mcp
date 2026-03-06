# Memory Setup — Meditate

## Initial Setup

Create directory on first use:
```bash
mkdir -p ~/meditate/archive
```

## profile.md Template

Copy to `~/meditate/profile.md`:

```markdown
# User Profile

## Detected Type
<!-- entrepreneur | developer | creative | personal | system | unknown -->
Type: unknown
Confidence: low
Last updated: never

## Rhythm Preferences
Frequency: conservative
Last meditation: never
Feedback rate: 0%

## Focus Areas
<!-- Topics user has confirmed interest in -->

## Excluded Topics
<!-- Topics user said "don't think about" -->

---
*Updated automatically based on feedback*
```

## topics.md Template

Copy to `~/meditate/topics.md`:

```markdown
# Active Meditation Topics

## High Priority
<!-- Topics with positive feedback -->

## Normal Priority
<!-- Default topics based on profile -->

## Low Priority
<!-- Topics with no feedback yet -->

## Excluded
<!-- User explicitly said no -->

---
*Priorities shift based on user feedback*
```

## insights.md Template

Copy to `~/meditate/insights.md`:

```markdown
# Pending Insights

<!-- Maximum 3 pending at any time -->
<!-- Format:
## [YYYY-MM-DD] Topic
**Observation:** ...
**Question:** ...
**Context:** ...
Generated: HH:MM
-->

---
*Present oldest first*
```

## feedback.md Template

Copy to `~/meditate/feedback.md`:

```markdown
# Feedback Log

<!-- Format:
## YYYY-MM-DD
- Topic: [topic]
- Insight: [summary]
- Response: [positive|neutral|negative|silence]
- Action: [continue|demote|exclude|prioritize]
-->

## Stats
Total: 0
Positive: 0
Neutral: 0
Negative: 0
Silence: 0

---
*Stats update automatically*
```
