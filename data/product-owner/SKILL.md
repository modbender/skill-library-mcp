---
name: Product Owner
slug: product-owner
version: 1.0.1
changelog: Improved setup flow with natural conversation guidelines
homepage: https://clawic.com/skills/product-owner
description: Manage backlogs, write user stories, define acceptance criteria, and maximize product value.
metadata: {"clawdbot":{"emoji":"📋","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` for onboarding guidelines.

## When to Use

User needs backlog management, user story writing, sprint prioritization, or stakeholder alignment. Agent handles Scrum artifacts, acceptance criteria, value maximization, and delivery coordination.

## Architecture

Memory lives in `~/product-owner/`. See `memory-template.md` for structure.

```
~/product-owner/
├── memory.md          # Product context, stakeholders, priorities
├── backlog/           # Per-product backlogs
│   └── {product}.md   # Stories, priorities, acceptance criteria
└── sprints/           # Sprint history and retrospectives
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |
| Story patterns | `stories.md` |
| Prioritization | `prioritization.md` |

## Core Rules

### 1. Value Over Features
- Every story must connect to business value
- Ask "what outcome does this enable?" before writing
- Prioritize by value/effort ratio, not stakeholder volume

### 2. INVEST in Stories
User stories must be:
| Criterion | Question |
|-----------|----------|
| Independent | Can be delivered alone? |
| Negotiable | Details can evolve? |
| Valuable | Delivers user/business value? |
| Estimable | Team can estimate effort? |
| Small | Fits in one sprint? |
| Testable | Clear pass/fail criteria? |

### 3. Acceptance Criteria Format
Write criteria as Given/When/Then:
```
Given [context]
When [action]
Then [expected outcome]
```

Multiple criteria per story. Each must be independently verifiable.

### 4. Backlog Grooming Cadence
- Top 20% of backlog: fully refined, ready for sprint
- Next 30%: roughly estimated, needs refinement
- Bottom 50%: parking lot, review quarterly

### 5. Stakeholder Management
- One voice to development team
- Translate stakeholder requests into stories
- Say no to scope creep, offer alternatives
- Document decisions and rationale in memory

### 6. Sprint Boundaries
- Committed scope is sacred
- New requests go to backlog, not current sprint
- Only PO can adjust sprint scope (with team agreement)

### 7. Definition of Done
Maintain explicit DoD. Every story must meet DoD before acceptance. Update DoD when team matures.

## Common Traps

- Writing solutions instead of problems in stories
- Accepting vague requirements without clarification
- Overloading sprints with "just one more thing"
- Prioritizing by who shouts loudest
- Skipping acceptance criteria because "it's obvious"
- Treating estimates as commitments

## Prioritization Frameworks

| Framework | Best For |
|-----------|----------|
| WSJF (Weighted Shortest Job First) | SAFe environments, cost of delay matters |
| MoSCoW | Quick categorization, stakeholder alignment |
| RICE | Data-driven teams, scoring objectivity |
| Kano Model | Feature differentiation, user delight |
| Value/Effort Matrix | Simple visualization, quick decisions |

See `prioritization.md` for detailed guidance.

## Story Templates

### Standard User Story
```
As a [user type]
I want [capability]
So that [benefit]

Acceptance Criteria:
- Given... When... Then...
- Given... When... Then...
```

### Technical Story
```
As a [team role]
I need [technical capability]
So that [technical benefit enabling user value]
```

### Bug Fix
```
Current: [what happens]
Expected: [what should happen]
Impact: [users affected, severity]
```

## Metrics to Track

| Metric | Why |
|--------|-----|
| Velocity | Predictability |
| Cycle Time | Flow efficiency |
| Escaped Defects | Quality |
| Sprint Goal Achievement | Commitment reliability |
| Stakeholder Satisfaction | Value delivery |

## Related Skills
Install with `clawhub install <slug>` if user confirms:

- `product-manager` — Product strategy and roadmap
- `cpo` — Chief Product Officer leadership
- `delegate` — Task delegation patterns
- `business` — Business strategy fundamentals

## Feedback

- If useful: `clawhub star product-owner`
- Stay updated: `clawhub sync`
