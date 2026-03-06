# Architecture Decisions — Enterprise

## ADR Template

Every major decision gets an ADR:

```markdown
# ADR-{number}: {Title}

## Status
Proposed | Accepted | Deprecated | Superseded by ADR-X

## Context
What is the issue that we're seeing that is motivating this decision?

## Decision
What is the change that we're proposing and/or doing?

## Consequences
What becomes easier or more difficult because of this change?
```

## Trade-off Matrix

| Factor | Monolith | Microservices | Serverless |
|--------|----------|---------------|------------|
| Initial velocity | ✅ Fast | ⚠️ Slow | ✅ Fast |
| Team independence | ❌ Low | ✅ High | ✅ High |
| Operational cost | ✅ Low | ⚠️ High | ⚠️ Variable |
| Debugging | ✅ Easy | ❌ Hard | ❌ Hard |
| Scaling | ⚠️ All-or-nothing | ✅ Granular | ✅ Auto |

## Decision Frameworks

### Buy vs Build
```
Build when:
- Core differentiator
- Exact fit required
- Long-term ownership viable

Buy when:
- Commodity functionality
- Time-to-market critical
- Expertise gap exists
```

### Synchronous vs Async
```
Sync when:
- User waiting for response
- Transaction semantics needed
- Simple request/response

Async when:
- Long-running operations
- Decoupling required
- Spike handling needed
- At-least-once acceptable
```

## Common Patterns

### API Gateway
Single entry point for all external traffic.
- Authentication centralized
- Rate limiting
- Request transformation
- Analytics collection

### Event Sourcing
Store state as sequence of events.
- Full audit trail built-in
- Temporal queries possible
- Complexity cost: high

### CQRS
Separate read and write models.
- Scale reads independently
- Optimize for query patterns
- Eventual consistency required

## Anti-Patterns

- Distributed monolith → worst of both worlds
- Database per service without data ownership → integration hell
- Synchronous chains across services → cascading failures
- Shared libraries coupling services → deployment lock-step
