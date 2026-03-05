# System Design Fundamentals

## Overview
Monolith vs Microservices, service boundaries, API contracts, dan scalability patterns untuk production systems.

## Decision Framework

```
┌─────────────────────────────────────────────────────────────┐
│                  SYSTEM DESIGN DECISION TREE                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │  Team Size?                  │
              └─────────────────────────────┘
                    │               │
               < 10 people        > 20 people
                    │               │
                    ▼               ▼
              ┌─────────┐    ┌─────────────────┐
              │ Monolith│    │ Microservices   │
              │ Start   │    │ Consider        │
              └─────────┘    │ carefully       │
                             └─────────────────┘
```

## Monolith vs Microservices

### Monolith - When to Use ✅
- Team size < 10 engineers
- Early startup/MVP phase (< 6 months)
- Tightly coupled features
- Simple domain
- Need fast iteration
- Limited DevOps maturity

### Microservices - When to Use ✅
- Team size > 20 engineers
- Multiple independent products
- Different scaling requirements per service
- Polyglot needs (different tech stacks)
- Need independent deployments
- Complex domain with clear boundaries

### Warning Signs (Time to Migrate)
| Sign | Indicator |
|------|-----------|
| Build time | > 10 minutes |
| Deploy coupling | Teams blocking each other |
| Scaling | Different parts need different resources |
| Tech stack | One size doesn't fit all |

## Service Boundaries

### Bounded Context Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                    E-COMMERCE DOMAIN                        │
├─────────────────┬─────────────────┬─────────────────────────┤
│    Catalog      │      Order     │      User               │
│    Context      │      Context   │      Context            │
├─────────────────┼─────────────────┼─────────────────────────┤
│  - Products     │  - Cart        │  - Profile              │
│  - Categories   │  - Checkout    │  - Auth                 │
│  - Inventory    │  - Payments    │  - Preferences          │
│                 │  - Shipping    │                         │
└─────────────────┴─────────────────┴─────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
   ┌──────────┐        ┌──────────┐        ┌──────────┐
   │ Catalog  │        │  Order   │        │   User   │
   │ Service  │        │ Service  │        │  Service │
   └──────────┘        └──────────┘        └──────────┘
```

### Communication Patterns

| Pattern | Use Case | Pros | Cons |
|---------|----------|------|------|
| REST | CRUD, synchronous | Simple, familiar | Coupling |
| gRPC | High perf, internal | Fast, type-safe | Learning curve |
| Message Queue | Async, decoupled | Resilient, scalable | Complexity |
| Event Bus | Cross-service events | Loose coupling | Hard to trace |

## Scalability Patterns

### Horizontal vs Vertical Scaling

```
Vertical Scaling                    Horizontal Scaling
┌───────────────────┐             ┌─────┐ ┌─────┐ ┌─────┐
│     Server        │             │ SV1 │ │ SV2 │ │ SV3 │
│   ┌─────┐         │      →      └─────┘ └─────┘ └─────┘
│   │ CPU │ +        │                 Load Balancer
│   │ RAM │          │
│   └─────┘          │
│                   │             Pros: Infinite scale, resilient
│   Expensive       │             Cons: Distributed complexity
│   Limited         │
└───────────────────┘
```

### Database Scaling

```
                    ┌──────────────┐
                    │  Application │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         ┌────────┐  ┌──────────┐  ┌─────────┐
         │ Read   │  │  Write   │  │  Cache  │
         │ Replica│  │  Master  │  │ (Redis) │
         └────────┘  └──────────┘  └─────────┘
              │            │
              ▼            ▼
         ┌─────────────────────────┐
         │      Sharding          │
         │  (when single DB fails)│
         └─────────────────────────┘
```

## Checklist

### Phase 1: Discovery
- [ ] Identify business domains
- [ ] Map data ownership per domain
- [ ] Define service boundaries
- [ ] List inter-service dependencies

### Phase 2: Architecture
- [ ] Choose communication style (sync/async)
- [ ] Define API contracts
- [ ] Plan for failure scenarios
- [ ] Set SLAs per service

### Phase 3: Implementation
- [ ] Set up service discovery
- [ ] Configure load balancing
- [ ] Implement circuit breakers
- [ ] Add monitoring per service

### Phase 4: Operations
- [ ] Document runbooks
- [ ] Set up alerting
- [ ] Plan capacity
- [ ] Define rollback procedures

## Tradeoffs Summary

| Aspect | Monolith | Microservices |
|--------|----------|---------------|
| **Deployment** | Simple | Complex |
| **Scaling** | Limited | Infinite |
| **Debugging** | Easy | Hard |
| **Team Autonomy** | Low | High |
| **Data Consistency** | Easy (ACID) | Eventual |
| **Infrastructure** | Minimal | Extensive |
| **Time to MVP** | Fast | Slow |

## Common Mistakes

| Mistake | Solution |
|---------|----------|
| Premature microservices | Start monolith, extract when needed |
| No clear boundaries | Use Domain-Driven Design |
| Distributed monolith | Actually decouple or stay monolithic |
| Forgetting operations | Plan monitoring from day 1 |

## Resources

- [ ] Read: Building Microservices by Sam Newman
- [ ] Watch: System Design Primer on YouTube
- [ ] Practice: LeetCode System Design questions
