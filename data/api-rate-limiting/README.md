# Rate Limiting Patterns

Rate limiting algorithms, implementation strategies, HTTP conventions, tiered limits, distributed patterns, and client-side handling. Use when protecting APIs from abuse, implementing usage tiers, or configuring gateway-level throttling.

## What's Inside

- Algorithms — token bucket, leaky bucket, fixed window, sliding window log, sliding window counter
- Implementation Options — in-memory, Redis, API gateway, middleware
- HTTP Headers — RateLimit-Limit, RateLimit-Remaining, RateLimit-Reset, Retry-After
- 429 Response Body format
- Rate Limit Tiers — per-IP, per-user, per-API-key, per-endpoint with tiered pricing examples
- Distributed Rate Limiting — Redis-based patterns, atomic Lua scripts
- API Gateway Configuration — NGINX and Kong examples
- Client-Side Handling — retry with backoff, respecting Retry-After
- Monitoring — hit rate, near-limit warnings, top offenders, false positives
- Anti-Patterns and common mistakes

## When to Use

- Protecting APIs from abuse and overuse
- Implementing usage tiers for API consumers
- Configuring gateway-level or middleware-level throttling
- Setting up distributed rate limiting with Redis
- Designing client-side rate limit handling and retry logic
- Monitoring rate limit effectiveness

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/api/rate-limiting
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/api/rate-limiting .cursor/skills/rate-limiting
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/api/rate-limiting ~/.cursor/skills/rate-limiting
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/api/rate-limiting .claude/skills/rate-limiting
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/api/rate-limiting ~/.claude/skills/rate-limiting
```

## Related Skills

- `auth-patterns` — Rate limiting protects auth endpoints from brute force
- `error-handling` — 429 status code handling and retry patterns
- `caching` — Caching and rate limiting often work together
- `api-design` — Rate limiting as part of API design considerations

---

Part of the [API](..) skill category.
