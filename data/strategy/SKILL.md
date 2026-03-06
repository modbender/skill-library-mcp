---
name: Strategy
slug: strategy
version: 1.0.0
description: Design robust strategies for any domain with proven frameworks, cognitive bias protection, and constraint-aware recommendations.
metadata: {"clawdbot":{"emoji":"♟️","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Architecture

Strategy profiles live in `~/strategy/` with context-specific refinement.

```
~/strategy/
├── memory.md          # HOT: constraints, preferences, past decisions
├── domains/           # Domain-specific patterns (business, product, career)
└── playbooks/         # Reusable strategy templates
```

See `memory-template.md` for initial setup.

## Quick Reference

| Topic | File |
|-------|------|
| Strategic frameworks | `frameworks.md` |
| Cognitive biases to avoid | `biases.md` |
| Design process | `process.md` |
| Thinking techniques | `techniques.md` |

## Core Rules

### 1. Diagnosis Before Prescription
Never propose strategy without understanding the REAL problem. Ask:
- What are you trying to achieve? (specific, measurable)
- What constraints exist? (time, money, people, politics)
- What have you tried? What failed?
- Who are the stakeholders and what do they want?

### 2. Constraints First
BEFORE any recommendation, map hard constraints:
- Budget (actual numbers, not "limited")
- Timeline (deadlines, milestones)
- Resources (team size, capabilities)
- Political/cultural restrictions

Reject strategies that ignore stated constraints.

### 3. Trade-offs Are Mandatory
Every strategy must explicitly state:
- What you're SACRIFICING (not doing Y to do X)
- What could go wrong (risks, not just benefits)
- What success looks like (measurable criteria)

"Do both" is not a strategy. "Optimize everything" is not a strategy.

### 4. Model Competitor Response
For competitive decisions: "If you do X, competitor will likely do A, B, or C. Your counter-move for each..."

Never assume competitors stay static.

### 5. Multiple Scenarios
Provide at least 3 scenarios:
- **Best case**: Everything works (10% weight)
- **Base case**: Realistic execution (60% weight)  
- **Worst case**: Key assumptions fail (30% weight)

Include triggers: "If X happens, switch to plan B"

### 6. Bias Protection
Before finalizing, run bias check from `biases.md`:
- Am I confirming existing beliefs?
- Am I anchored to first data?
- Am I avoiding loss or chasing sunk costs?

### 7. Actionable Next Steps
End every strategy session with:
- 3 concrete actions for this week
- Clear owner for each action
- Success metrics to check in 2-4 weeks

### 8. Challenge the Framing
If the question seems wrong, say so:
"You're asking how to grow faster, but your data suggests retention is the real problem. Should we reframe?"

### 9. Kill Criteria
Every strategy includes conditions to ABANDON it:
"If metric X drops below Y for Z weeks, stop and reassess."

### 10. Progressive Framework Selection
Match framework to problem type — see `frameworks.md`:
- Competition analysis → Porter's Five Forces
- Growth options → Ansoff Matrix
- Prioritization → ICE/RICE
- Full strategy design → Playing to Win

## Memory Storage

User context persists in `~/strategy/memory.md`. Create on first use.
