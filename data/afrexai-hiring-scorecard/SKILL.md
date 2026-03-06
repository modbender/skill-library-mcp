---
name: Hiring Scorecard Skill
description: Score and compare job candidates objectively using weighted
  criteria. Eliminates gut-feel hiring decisions.
---

# Hiring Scorecard Skill

Score and compare job candidates objectively using weighted criteria. Eliminates gut-feel hiring decisions.

## Usage

Tell your agent: "Score this candidate for [role]" or "Compare these 3 candidates for the backend engineer role."

## How It Works

1. **Define the role** — provide job title and key requirements
2. **Set criteria** — the agent uses 6 default dimensions (or you customize):
   - Technical skills (weight: 25%)
   - Relevant experience (weight: 20%)
   - Culture fit (weight: 15%)
   - Communication (weight: 15%)
   - Problem solving (weight: 15%)
   - Growth potential (weight: 10%)
3. **Score candidates** — 1-5 scale per criterion after interview/review
4. **Get weighted totals** — ranked comparison with hire/no-hire recommendation

## Commands

- `score candidate [name] for [role]` — start a new scorecard
- `add criterion [name] weight [%]` — customize scoring dimensions
- `compare candidates` — side-by-side ranked comparison
- `hiring summary` — executive summary with recommendation

## Scorecard Template

```markdown
# Candidate Scorecard: [Name]
**Role:** [Title]
**Date:** [Date]
**Interviewer:** [Name]

| Criterion | Weight | Score (1-5) | Weighted |
|-----------|--------|-------------|----------|
| Technical Skills | 25% | _ | _ |
| Relevant Experience | 20% | _ | _ |
| Culture Fit | 15% | _ | _ |
| Communication | 15% | _ | _ |
| Problem Solving | 15% | _ | _ |
| Growth Potential | 10% | _ | _ |
| **TOTAL** | **100%** | | **_/5.0** |

### Notes
- Strengths:
- Concerns:
- Recommendation: HIRE / NO HIRE / MAYBE

### Scoring Guide
5 = Exceptional — top 5% of candidates seen
4 = Strong — clearly above average
3 = Meets bar — would do the job well
2 = Below bar — notable gaps
1 = Not a fit — significant concerns
```

## Tips

- Score immediately after each interview while impressions are fresh
- Have multiple interviewers score independently, then compare
- Adjust weights per role (e.g., bump Technical to 40% for senior eng)
- Track scores over time to calibrate your hiring bar

## More Business Tools

Get industry-specific AI agent context packs at [AfrexAI](https://afrexai-cto.github.io/context-packs/) — pre-built configurations for recruitment, sales, operations, and more. Drop-in and go.
