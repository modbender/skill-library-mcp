# Microservices Patterns

Patterns for building distributed systems: service decomposition, inter-service communication, data management, and resilience. Helps you avoid the "distributed monolith" anti-pattern.

## What's Inside

- Decision Framework — when to use microservices vs monolith
- Service Decomposition — by business capability, Strangler Fig migration pattern
- Communication Patterns — synchronous (REST/gRPC) with retries, asynchronous (events/Kafka)
- Data Patterns — database per service, Saga pattern for distributed transactions
- Resilience Patterns — circuit breaker, retry with exponential backoff, bulkhead isolation
- API Gateway Pattern — single entry point, request aggregation, circuit breaking
- Health Checks — liveness and readiness probes

## When to Use

- Decomposing a monolith into microservices
- Designing service boundaries and contracts
- Implementing inter-service communication
- Managing distributed transactions
- Building resilient distributed systems

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/backend/microservices-patterns
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/backend/microservices-patterns .cursor/skills/microservices-patterns
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/backend/microservices-patterns ~/.cursor/skills/microservices-patterns
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/backend/microservices-patterns .claude/skills/microservices-patterns
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/backend/microservices-patterns ~/.claude/skills/microservices-patterns
```

## Related Skills

- `architecture-patterns` — Clean Architecture, Hexagonal, and DDD foundations
- `event-store` — Event sourcing for microservices data management
- `architecture-decision-records` — Document decomposition and design decisions

---

Part of the [Backend](..) skill category.
