# Memory Setup — Business Strategy

## Initial Setup

Create directory structure on first use:

```bash
mkdir -p ~/business/ideas ~/business/archive
touch ~/business/decisions.md ~/business/metrics.md
```

## decisions.md Template

Copy to `~/business/decisions.md`:

```markdown
# Business Decisions Log

Track significant decisions to learn from outcomes.

## Active Decisions

### [DATE] Decision Title
**Context:** Why this decision came up
**Options:**
- A: Description
- B: Description  
- C: Description

**Decision:** [Which option]
**Reasoning:** Why this over alternatives
**Review Date:** [When to check outcome]
**Outcome:** [Fill after review date]

---

## Completed Decisions

Move here after outcome is known. Add lessons learned.

---

## Patterns Observed

After 10+ decisions, note patterns:
- What types of decisions go well?
- What assumptions tend to be wrong?
- What frameworks work best for you?

---
*Last updated: YYYY-MM-DD*
```

## metrics.md Template

Copy to `~/business/metrics.md`:

```markdown
# Business Metrics

## Current State

**Date:** YYYY-MM-DD

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| MRR | $X | $Y | 🟡 |
| Active Users | N | M | 🟢 |
| Churn (monthly) | X% | <5% | 🔴 |
| CAC | $X | <$Y | |
| LTV | $X | >$Z | |

## Monthly Snapshots

### YYYY-MM
- MRR: $X
- Users: N
- Notable: [key events]

---
*Update weekly minimum*
```

## ideas/ Folder

For each idea being validated, create `~/business/ideas/{idea-name}.md`:

```markdown
# Idea: {Name}

## One-Line Description
[What is it in one sentence]

## Validation Progress

### 1. Problem Definition
- [ ] Can articulate without mentioning solution
- Problem statement: ___

### 2. Evidence
- [ ] Talked to 5+ potential customers
- Evidence collected:
  - Person 1: [what they said]
  - Person 2: [what they said]
  - ...

### 3. Alternatives
- [ ] Researched current solutions
- Competitors: ___
- How people solve it today: ___

### 4. Differentiation
- [ ] Clear reason to switch
- Why us: ___

### 5. Willingness to Pay
- [ ] Asked for money
- Results:
  - Pre-orders: ___
  - LOIs: ___
  - Rejections and why: ___

## Verdict
- [ ] GO: All stages passed
- [ ] NO-GO: Failed at stage ___
- [ ] PIVOT: Modify to ___

## Next Action
[One concrete next step]

---
*Created: YYYY-MM-DD*
*Last updated: YYYY-MM-DD*
```

## Archive

Move old decisions and completed ideas to `~/business/archive/` with date prefix:

```
archive/
├── 2024-01-idea-saas-tool.md
├── 2024-02-decision-pricing.md
└── ...
```

Periodically review archive to spot patterns.
