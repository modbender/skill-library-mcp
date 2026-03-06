# Engineering Operations

## DORA Metrics

Track these four metrics for engineering health:

| Metric | Elite | High | Medium | Low |
|--------|-------|------|--------|-----|
| Deployment frequency | Multiple/day | Weekly | Monthly | < Monthly |
| Lead time for changes | < 1 hour | < 1 week | < 1 month | > 1 month |
| Change failure rate | < 5% | < 10% | < 15% | > 15% |
| Time to restore | < 1 hour | < 1 day | < 1 week | > 1 week |

**Goal:** Move up the scale incrementally.

## On-Call

### Principles
- Sustainable rotations (no burnout)
- Clear escalation paths
- Runbooks for common issues
- Compensation for off-hours work
- Blameless culture

### Structure

| Team Size | Rotation |
|-----------|----------|
| 1-3 | Informal, shared responsibility |
| 4-8 | Weekly rotation |
| 8+ | Multiple rotations by service |

### Incident Response

1. **Detect** — Alerts fire
2. **Respond** — On-call acknowledges
3. **Mitigate** — Stop the bleeding
4. **Resolve** — Fix the root cause
5. **Review** — Blameless postmortem

## Postmortems

### Template

```markdown
# Incident: [Title]
Date: [Date]
Duration: [Time]
Impact: [What users experienced]

## Timeline
- HH:MM — Event happened
- HH:MM — Alert fired
- HH:MM — Action taken

## Root Cause
[What actually caused this]

## Contributing Factors
[What made it worse or delayed response]

## Action Items
- [ ] [Specific fix with owner and due date]

## Lessons Learned
[What did we learn?]
```

### Rules
- Written within 48 hours
- Blameless (focus on systems, not people)
- Action items tracked to completion
- Shared widely

## Development Workflow

### Git Workflow
- Trunk-based for small teams
- Feature branches for larger teams
- Short-lived branches (< 1 week)
- CI required before merge

### Code Review

| Reviewer Focus | Author Responsibility |
|----------------|----------------------|
| Correctness | Small, focused PRs |
| Readability | Clear descriptions |
| Tests | Self-reviewed first |
| Architecture fit | Responsive to feedback |

**Review time target:** < 24 hours

## Release Process

| Stage | Purpose |
|-------|---------|
| CI | Tests pass, builds work |
| Staging | Integration testing |
| Canary | Small production traffic |
| Production | Full rollout |
| Monitor | Watch metrics post-deploy |

### Feature Flags

Use flags to:
- Decouple deploy from release
- Gradual rollout
- Quick rollback
- A/B testing

## Security Basics

- Dependencies scanned automatically
- Secrets never in code
- Least privilege access
- Regular access reviews
- Security training for engineers
- Incident response plan exists
