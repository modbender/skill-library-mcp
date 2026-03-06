# Architecture Decisions

## ADR Template (Architecture Decision Record)

```markdown
# ADR-XXX: [Title]

## Status
[Proposed | Accepted | Deprecated | Superseded by ADR-YYY]

## Context
What is the issue that we're seeing that is motivating this decision?

## Decision
What is the change that we're proposing and/or doing?

## Consequences
What becomes easier or more difficult to do because of this change?

## Alternatives Considered
What other options were evaluated?
```

## Integration Patterns

| Pattern | When to Use |
|---------|-------------|
| **API-first** | Real-time needs, tight coupling acceptable |
| **Event-driven** | Loose coupling, eventual consistency OK |
| **Batch/ETL** | Large volumes, latency tolerant |
| **File transfer** | Legacy systems, simple needs |

## Technical Debt Categories

| Type | Example | Impact |
|------|---------|--------|
| **Code** | No tests, copy-paste | Slow feature delivery |
| **Architecture** | Monolith needing split | Scale ceiling |
| **Infrastructure** | Manual deployments | Reliability risk |
| **Documentation** | Tribal knowledge | Bus factor |
| **Dependency** | Outdated libraries | Security risk |

## Debt Tracking Template

| ID | Description | Type | Impact | Effort | Priority |
|----|-------------|------|--------|--------|----------|
| | | | H/M/L | S/M/L/XL | |

## Technology Standards

### Approved Stack
- **Languages:** [List approved languages]
- **Frameworks:** [List approved frameworks]
- **Databases:** [List approved databases]
- **Cloud:** [Approved providers]
- **Monitoring:** [Approved tools]

### Exception Process
1. Submit exception request with justification
2. Architecture review (impact, support, exit plan)
3. CIO/CTO approval for production use
4. Document in tech radar as Trial/Assess

## System Criticality Tiers

| Tier | Definition | RTO | RPO |
|------|------------|-----|-----|
| **Tier 1** | Business stops | <1hr | <15min |
| **Tier 2** | Major impact | <4hr | <1hr |
| **Tier 3** | Workarounds exist | <24hr | <4hr |
| **Tier 4** | Minor inconvenience | <72hr | <24hr |
