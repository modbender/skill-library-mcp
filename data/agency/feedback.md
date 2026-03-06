# Feedback and Learning System

## Purpose

The agency improves over time by capturing:
- What works with clients
- What causes problems
- Patterns to replicate or avoid
- Estimate accuracy over time

## Knowledge Base Structure

`~/agency/knowledge/`:

```
knowledge/
├── sops/                 # Standard Operating Procedures
│   ├── onboarding.md
│   ├── proposal.md
│   └── delivery.md
├── cases/                # Completed project summaries
│   └── [project-name].md
├── learnings.md          # Accumulated insights
└── estimates-log.md      # Estimate vs actual tracking
```

## After Each Project

Capture in `~/agency/knowledge/cases/[project].md`:

```markdown
# [Project Name]

## Client: [name]
## Type: [project type]
## Duration: [start] to [end]
## Value: [revenue]

## What we did
[Brief description]

## What worked
- [Thing that went well]
- [Another success]

## What didn't work
- [Issue and why]
- [Another problem]

## Key learnings
- [Insight to apply to future projects]

## Would we do it again?
[Yes/No and why — honest assessment]
```

## Estimate Tracking

In `~/agency/knowledge/estimates-log.md`:

```markdown
| Project | Type | Estimated Hours | Actual Hours | Variance | Notes |
|---------|------|-----------------|--------------|----------|-------|
| [name]  | [type] | 40h | 52h | +30% | Client slow to respond |
```

Review quarterly:
- Which project types consistently over/under estimate?
- What causes overruns? (scope creep, client delays, complexity)
- Adjust estimation formulas based on patterns

## Template Updates

When something works well:
- Extract the pattern
- Add to relevant template
- Note why it works

When something fails:
- Document what happened
- Add warning to relevant SOP
- Update checklist to prevent recurrence

## Client Feedback Capture

After project delivery:
- Request feedback (formal or informal)
- Record in client file
- Extract actionable improvements

Feedback to track:
- Would they work with us again?
- What did they value most?
- What could we improve?

## Quarterly Review

Every quarter, review:
1. **Projects completed:** wins, losses, lessons
2. **Estimate accuracy:** adjust formulas
3. **Client retention:** who renewed, who didn't, why
4. **Process improvements:** what to update in SOPs
5. **Team performance:** who's growing, who needs support

Update:
- Rate card if costs changed
- Templates if better versions exist
- SOPs if processes improved
