# Service Layer Architecture

Controller-service-query layered API architecture with data enrichment and parallel fetching. Use when building REST APIs or GraphQL resolvers with clean separation of concerns.

## What's Inside

- Three-Layer Architecture — controllers (HTTP handling), services (business logic), queries (database access)
- Layer 1: Controllers — HTTP-only concerns, request parsing, validation, status codes
- Layer 2: Services — business logic, data enrichment, parallel data fetching with `Promise.all`
- Layer 3: Queries — database access, raw data retrieval with `.lean()`
- Parallel Data Fetching — sequential vs parallel comparison
- Layer Responsibilities table — clear ownership of each concern

## When to Use

- Building REST APIs with complex data aggregation
- GraphQL resolvers needing data from multiple sources
- Any API where responses combine data from multiple queries
- Systems needing testable, maintainable code

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/backend/service-layer-architecture
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/backend/service-layer-architecture .cursor/skills/service-layer-architecture
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/backend/service-layer-architecture ~/.cursor/skills/service-layer-architecture
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/backend/service-layer-architecture .claude/skills/service-layer-architecture
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/backend/service-layer-architecture ~/.claude/skills/service-layer-architecture
```

## Related Skills

- `postgres-job-queue` — Background job processing
- `architecture-patterns` — Clean Architecture, Hexagonal, and DDD patterns

---

Part of the [Backend](..) skill category.
