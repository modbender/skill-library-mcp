# PostgreSQL Job Queue

Production-ready job queue using PostgreSQL with priority scheduling, batch claiming, and progress tracking.

## What's Inside

- Schema Design — jobs table with priority, status, progress tracking, retry handling, and partial indexes
- Batch Claiming with SKIP LOCKED — SQL function for concurrent, safe job claiming
- Go Implementation — JobQueue struct with Claim, Complete, and Fail operations
- Stale Job Recovery — automatic reclamation of abandoned jobs
- Decision Tree — when to use PostgreSQL vs Redis for job queues

## When to Use

- Need a job queue but want to avoid Redis/RabbitMQ dependencies
- Jobs need priority-based scheduling
- Long-running jobs need progress visibility
- Jobs should survive service restarts

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/backend/postgres-job-queue
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/backend/postgres-job-queue .cursor/skills/postgres-job-queue
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/backend/postgres-job-queue ~/.cursor/skills/postgres-job-queue
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/backend/postgres-job-queue .claude/skills/postgres-job-queue
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/backend/postgres-job-queue ~/.claude/skills/postgres-job-queue
```

## Related Skills

- `service-layer-architecture` — Service patterns for job handlers
- `supabase-postgres` — PostgreSQL optimization and best practices

---

Part of the [Backend](..) skill category.
