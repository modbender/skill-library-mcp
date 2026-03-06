# Caching Patterns

Caching strategies, invalidation, eviction policies, HTTP caching, distributed caching, and anti-patterns. Use when designing cache layers, choosing eviction policies, debugging stale data, or optimizing read-heavy workloads.

## What's Inside

- Cache Strategies — cache-aside, read-through, write-through, write-behind, refresh-ahead
- Cache Invalidation — TTL-based, event-based, version-based, tag-based with TTL guidelines
- HTTP Caching — Cache-Control directives, common recipes, conditional requests (ETag, Last-Modified)
- Application Caching — in-memory LRU, Redis, Memcached, SQLite comparison
- Redis vs Memcached feature comparison
- Distributed Caching — partitioning, replication, failover
- Cache Eviction Policies — LRU, LFU, FIFO, TTL
- Caching Layers — browser, CDN, application, database
- Cache Stampede Prevention — mutex, probabilistic early expiration, request coalescing
- Cache Warming strategies
- Monitoring — hit rate, eviction rate, latency, memory usage

## When to Use

- Designing cache layers for an application
- Choosing between cache strategies and eviction policies
- Configuring HTTP caching headers
- Debugging stale data or cache inconsistencies
- Optimizing read-heavy workloads
- Setting up Redis or distributed caching

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/api/caching
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/api/caching .cursor/skills/caching
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/api/caching ~/.cursor/skills/caching
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/api/caching .claude/skills/caching
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/api/caching ~/.claude/skills/caching
```

## Related Skills

- `api-design` — API design including HTTP caching considerations
- `rate-limiting` — Rate limiting often works alongside caching
- `error-handling` — Never cache error responses

---

Part of the [API](..) skill category.
