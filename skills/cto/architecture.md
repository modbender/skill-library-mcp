# Architecture Decisions

## Architecture Decision Records (ADRs)

Document every significant technical decision:

```markdown
# ADR-001: [Title]

## Status
Proposed | Accepted | Deprecated | Superseded

## Context
What problem are we solving? What constraints exist?

## Decision
What did we decide?

## Consequences
What are the trade-offs? What becomes easier/harder?
```

Keep ADRs in version control with code.

## Decision Framework

### Reversibility Matrix

| Reversible | Irreversible |
|------------|--------------|
| Library choice | Database choice |
| API design (internal) | API design (public) |
| Feature flag rollout | Data model changes |
| Cloud region | Primary language |

**Rule:** Reversible = move fast. Irreversible = invest in analysis.

### Build vs Buy

| Build When | Buy When |
|------------|----------|
| Core differentiator | Commodity capability |
| Unique requirements | Standard problem |
| Long-term strategic | Time-to-market critical |
| Team has expertise | Would need to hire |

## System Design Principles

1. **Start simple** — Add complexity only when simple breaks
2. **Horizontal > vertical** — Scale out before scaling up
3. **Async by default** — Decouple where possible
4. **Fail gracefully** — Timeouts, retries, circuit breakers
5. **Observable** — If you can't see it, you can't fix it

## Technology Selection Criteria

| Factor | Weight | Questions |
|--------|--------|-----------|
| Team expertise | High | Can we hire for this? Do we know it? |
| Community/support | High | Is it actively maintained? |
| Fit for problem | High | Does it solve our actual problem? |
| Long-term viability | Medium | Will it exist in 5 years? |
| Performance | Medium | Does it meet our requirements? |
| Ecosystem | Low | Are there good libraries? |

## Common Architecture Patterns

### Monolith → Services Migration

1. Identify bounded contexts
2. Extract read models first (less risk)
3. Strangler fig pattern (gradual replacement)
4. Shared database → API calls → separate data
5. Don't migrate everything — some stays monolith

### Scaling Playbook

| Symptom | First Try | Then |
|---------|-----------|------|
| DB slow | Query optimization, indexes | Read replicas, caching |
| API latency | CDN, caching | Async processing |
| Memory pressure | Optimize code | Horizontal scale |
| High traffic | Load balancer | Rate limiting, queues |
