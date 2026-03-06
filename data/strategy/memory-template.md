# Strategy Memory Setup

Create `~/strategy/` on first strategy session.

## Initial Structure

```bash
mkdir -p ~/strategy/{domains,playbooks}
touch ~/strategy/memory.md
```

## memory.md Template

```markdown
# Strategy Memory

## Context
<!-- Your role, industry, company stage -->
Role: 
Industry:
Company stage:
Team size:
Runway/budget:

## Constraints
<!-- Things that can't change -->
- 
- 

## Strategic Preferences
<!-- How you like to work -->
Risk tolerance: [conservative/moderate/aggressive]
Planning horizon: [weeks/months/years]
Decision style: [data-driven/intuition/consensus]

## Active Strategies
<!-- Current strategic initiatives -->
| Initiative | Start | Target | Status |
|------------|-------|--------|--------|
|            |       |        |        |

## Past Decisions
<!-- Major decisions and outcomes for learning -->
| Date | Decision | Outcome | Learning |
|------|----------|---------|----------|
|      |          |         |          |

## Frameworks That Work
<!-- Which frameworks resonate with you -->
- 

## Anti-Patterns
<!-- Things that don't work for your context -->
- 
```

## Domain-Specific Files

For recurring strategy areas, create `domains/{area}.md`:

```markdown
# {Area} Strategy Context

## Stakeholders
<!-- Who matters for decisions in this area -->

## Success Metrics
<!-- How we measure wins -->

## Historical Context
<!-- What's been tried, what worked/failed -->

## Current Challenges
<!-- Open strategic questions -->
```

## Playbooks

For repeatable strategy patterns, create `playbooks/{name}.md`:

```markdown
# {Name} Playbook

## When to Use
<!-- Trigger conditions -->

## Process
1. 
2. 
3. 

## Checklist
- [ ] 
- [ ] 

## Common Pitfalls
- 
```
