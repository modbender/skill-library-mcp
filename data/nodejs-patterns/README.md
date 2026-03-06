# Node.js Backend Patterns

Production-ready Node.js backend patterns — Express/Fastify setup, layered architecture, middleware, error handling, validation, database integration, authentication, and caching.

## What's Inside

- Project Structure — layered architecture (controllers, services, repositories, models, middleware, routes)
- Express Setup — helmet, CORS, compression, JSON parsing
- Fastify Setup — type-safe routes with built-in schema validation
- Error Handling — custom error classes (AppError, ValidationError, NotFoundError), global error handler, async handler wrapper
- Validation Middleware (Zod) — schema-based request validation
- Authentication (JWT) — auth middleware, token verification, role-based authorization
- Auth Service — login with bcrypt, access/refresh token generation
- Database Patterns — PostgreSQL connection pool, transaction pattern
- Rate Limiting — Redis-backed with express-rate-limit
- Caching with Redis — get, set, delete, pattern invalidation
- API Response Helpers — success and paginated response formatting

## When to Use

- Building REST APIs with Express or Fastify
- Setting up middleware pipelines and error handling
- Implementing authentication and authorization
- Integrating databases with connection pooling and transactions
- Adding validation, caching, and rate limiting

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/backend/nodejs-patterns
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/backend/nodejs-patterns .cursor/skills/nodejs-patterns
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/backend/nodejs-patterns ~/.cursor/skills/nodejs-patterns
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/backend/nodejs-patterns .claude/skills/nodejs-patterns
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/backend/nodejs-patterns ~/.claude/skills/nodejs-patterns
```

---

Part of the [Backend](..) skill category.
