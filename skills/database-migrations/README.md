# Database Migration Patterns

Safe, zero-downtime database migration strategies — schema evolution, rollback planning, data migration, tooling, and anti-pattern avoidance for production systems. Use when planning schema changes, writing migrations, or reviewing migration safety.

## What's Inside

- Schema Evolution Strategies — additive-only, expand-contract, parallel change, lazy migration
- Zero-Downtime Patterns — add column, rename column, drop column, change type, add index, split table, change constraint, add enum value
- Migration Tools — Prisma, Knex, Drizzle, Alembic, Django, Flyway, golang-migrate, Atlas
- Rollback Strategies — reversible, forward-only, hybrid approaches
- Data Preservation — soft-delete, snapshot tables, point-in-time recovery, logical backups
- Blue-Green Database pattern
- Data Migration Patterns — backfill strategies, batch processing, dual-write period
- Testing Migrations — production-like data, migration CI pipeline
- Migration Checklist — pre-migration, during, and post-migration steps

## When to Use

- Planning schema changes for production databases
- Writing safe, zero-downtime migrations
- Choosing a migration tool for your stack
- Reviewing migration safety before deployment
- Handling data migrations and backfills on large tables
- Setting up migration CI pipelines

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/api/database-migrations
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/api/database-migrations .cursor/skills/database-migrations
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/api/database-migrations ~/.cursor/skills/database-migrations
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/api/database-migrations .claude/skills/database-migrations
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/api/database-migrations ~/.claude/skills/database-migrations
```

## Related Skills

- `api-versioning` — API versioning often accompanies schema migrations
- `api-development` — Database migrations as part of the API development lifecycle

---

Part of the [API](..) skill category.
