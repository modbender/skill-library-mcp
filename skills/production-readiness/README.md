# Production Readiness

Meta-skill that orchestrates logging, monitoring, error handling, performance, security, deployment, and testing skills to ensure a service is fully production-ready before launch.

## What's Inside

- Orchestration flow (logging & observability → error handling → performance → security → deployment → testing → documentation)
- Skill routing table for each concern
- Production readiness checklist (health & lifecycle, resilience, configuration & secrets, data safety, operational readiness)
- Maturity levels (L1 MVP → L2 Stable → L3 Resilient → L4 Optimized)
- Incident response (on-call rotation, escalation matrix, postmortem template)

## When to Use

- Before first deploy — new service going to production
- Before major release — significant feature or architectural change shipping
- Quarterly production review — scheduled audit of existing services
- After incident — post-incident hardening to prevent recurrence
- Dependency upgrade — major framework, runtime, or infrastructure change
- Team handoff — transferring ownership of a service to another team

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/meta/production-readiness
```

### OpenClaw / Moltbot / Clawbot

```bash
npx clawhub@latest install production-readiness
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/meta/production-readiness .cursor/skills/production-readiness
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/meta/production-readiness ~/.cursor/skills/production-readiness
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/meta/production-readiness .claude/skills/production-readiness
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/meta/production-readiness ~/.claude/skills/production-readiness
```

## Related Skills

- `logging-observability` — Structured logging, metrics, tracing
- `error-handling-patterns` — Error boundaries, retry policies
- `security-review` — Comprehensive security audit
- `docker-expert` — Container hardening
- `testing-workflow` — Test coverage and strategy
- `rate-limiting-patterns` — Rate limiting configuration

---

Part of the [Meta](..) skill category.
