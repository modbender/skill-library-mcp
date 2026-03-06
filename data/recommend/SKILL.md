---
name: "Recommend"
description: "Context-aware recommendations. Learns preferences, researches options, anticipates expectations."
---

## Core Loop

```
Context → Preferences → Research → Match → Recommend
```

Every recommendation requires: knowing the user + knowing the options.

Check `sources.md` for where to find user context. Check `categories.md` for domain-specific factors.

---

## Step 1: Context Gathering

Before recommending, search user context. See `sources.md` for full source list.

**Minimum output:** 3-5 relevant user signals before proceeding. If insufficient, ask targeted questions.

---

## Step 2: Preference Extraction

From gathered context, extract:

| Dimension | Question |
|-----------|----------|
| **Values** | What matters most? (Quality, price, speed, novelty, safety) |
| **Constraints** | Hard limits? (Budget, time, dietary, ethical) |
| **History** | What worked? What disappointed? |
| **Mood** | Adventurous or safe? Exploring or comfort? |

**Output:** 3-5 bullet preference profile for this request.

---

## Step 3: Research Options

Now—and only now—research candidates:

- **Breadth first**: Don't anchor on first good option
- **Source quality**: Prioritize reviews, ratings, expert opinions
- **Recency**: Check if information is current
- **Availability**: Confirm options are actually accessible

**Output:** Shortlist of 3-7 viable candidates with key attributes.

---

## Step 4: Match & Rank

Score each candidate against the preference profile:

```
Candidate → Values alignment + Constraint fit + History match + Mood fit
```

**Disqualify** anything that violates hard constraints.

**Rank** by total alignment, not just one dimension.

---

## Step 5: Recommend

Present 1-3 recommendations:

```
🎯 RECOMMENDATION: [Option]
📌 WHY: Matches [preference], avoids [constraint]
⚖️ TRADEOFF: Less [X] than [Alternative]
🔍 CONFIDENCE: [Level] — based on [data quality]
```

---

## Adaptive Learning

After each recommendation:

- **Track outcome**: Accepted? Modified? Rejected?
- **Update preferences**: Acceptance = reinforcement, rejection = adjustment
- **Note exceptions**: "Normally X, but for Y context preferred Z"

Store learnings in memory for future recommendations.

---

## Traps

- **Projecting** — Your taste ≠ their taste
- **Recency bias** — Last choice isn't always preference
- **Ignoring context** — Tuesday lunch ≠ anniversary dinner
- **Over-filtering** — Too many constraints = nothing fits
- **Stale data** — Preferences evolve, verify periodically

---

*Recommendations are predictions. More context = better predictions.*
