# CPO Operational Excellence

## Strategic Documentation

### Product Vision Document Template

```
## Vision
[One sentence: what the world looks like when we win]

## Strategic Context
- Market size and trajectory
- Competitive landscape
- Our differentiation

## Bets (3-year horizon)
1. [Bet name]: [What we believe, why, how we'll know]
2. [Bet name]: ...

## Anti-goals
- What we're explicitly NOT doing

## Success Metrics
- [Metric]: [Current] → [Target by when]
```

### Roadmap Prioritization Frameworks

**RICE Scoring:**
- Reach: How many users affected per quarter?
- Impact: How much will it move the metric? (3=massive, 2=high, 1=medium, 0.5=low, 0.25=minimal)
- Confidence: How sure are we? (100%/80%/50%)
- Effort: Person-weeks to ship

Score = (Reach × Impact × Confidence) / Effort

**When RICE Fails:**
- Strategic initiatives that don't fit quarterly thinking
- Platform/infrastructure investments
- Market entry decisions

Use: Strategic fit + reversibility + regret minimization for these.

## OKR/KPI Management

### Quarterly OKR Review Template

| Objective | Key Result | Target | Actual | Status | Learning |
|-----------|------------|--------|--------|--------|----------|
| [O1] | [KR1] | | | 🟢🟡🔴 | |
| | [KR2] | | | | |

### Metric Review Cadence

| Metric Type | Review Frequency | Audience |
|-------------|------------------|----------|
| North star metric | Weekly | Product leadership |
| Feature metrics | Sprint review | Product teams |
| Business metrics | Monthly | Executive team |
| Strategic metrics | Quarterly | Board |

## Stakeholder Communication

### Weekly Stakeholder Update Template

```
## Progress
- [Major milestone achieved]
- [Key metric movement]

## Blockers
- [Blocker + owner + ETA]

## Decisions Needed
- [Decision needed from whom by when]

## Coming Up
- [Next week's focus]
```

### Board Deck: Product Section

Slides to prepare:
1. **Product Metrics Dashboard** — Key metrics with trend lines
2. **Roadmap Progress** — What shipped vs planned
3. **Strategic Initiatives** — Deep dive on 1-2 major bets
4. **Competitive Landscape** — Notable moves, our response
5. **Product Org Update** — Team health, key hires/departures

## Competitive Intelligence

### Continuous Monitoring

Track weekly:
- Competitor product releases (changelog, app store updates)
- Competitor job postings (signals priorities)
- G2/Capterra review themes
- Social media mentions and sentiment
- Pricing changes

### Competitive Response Framework

| Competitor Move | Response Options |
|-----------------|------------------|
| New feature we lack | Evaluate: Copy, differentiate, or ignore? |
| Price cut | Analyze: Can we compete on value instead? |
| New market entry | Assess: Defend or let them have it? |
| Key hire from us | Debrief: What did they learn? |

## Product Org Design

### Team Structure Options by Stage

**Series A (3-5 PMs):**
- All PMs report to CPO
- Minimal specialization
- Everyone ships

**Series B (6-15 PMs):**
- Introduce PM managers
- Squad model (PM + Eng lead + Designer)
- Platform vs product teams emerge

**Series C+ (15+ PMs):**
- Director layer
- Domain-based pods
- Dedicated platform, growth, core teams
- PM ops function

### RACI for Common Decisions

| Decision | PM | PM Manager | CPO | CEO |
|----------|-----|------------|-----|-----|
| Feature prioritization | R | A | C | I |
| Roadmap (quarterly) | C | R | A | I |
| Strategy (annual) | I | C | R | A |
| Pricing changes | I | C | R | A |
| Major pivots | I | C | C | R/A |
