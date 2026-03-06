# API Development

Meta-skill that orchestrates the full API development lifecycle — from design through documentation — by coordinating specialized skills, agents, and commands into a seamless build workflow.

## What's Inside

- Orchestration Flow — 7-step API development lifecycle (Design → OpenAPI Spec → Scaffold → Implement → Test → Document → Deploy)
- API Design Decision Table — REST vs GraphQL vs gRPC comparison
- API Checklist — authentication, rate limiting, pagination, filtering, error handling, versioning, CORS, documentation, security, monitoring
- Skill Routing Table — maps needs to specialized skills

## When to Use

- Building a new API from scratch
- Adding endpoints to an existing API
- Redesigning or refactoring an API
- Planning API versioning and migration
- Running a complete API development cycle (design → build → test → document → deploy)

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/api/api-development
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/api/api-development .cursor/skills/api-development
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/api/api-development ~/.cursor/skills/api-development
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/api/api-development .claude/skills/api-development
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/api/api-development ~/.claude/skills/api-development
```

## Related Skills

- `api-design` — Resource modeling, HTTP semantics, pagination, error formats
- `api-versioning` — Version lifecycle, deprecation, migration patterns
- `auth-patterns` — JWT, OAuth2, sessions, RBAC, MFA
- `error-handling` — Error types, retry patterns, circuit breakers, HTTP errors
- `rate-limiting` — Algorithms, HTTP headers, tiered limits, distributed limiting
- `caching` — Cache strategies, HTTP caching, invalidation, Redis patterns
- `database-migrations` — Schema evolution, zero-downtime patterns, rollback strategies

---

Part of the [API](..) skill category.
