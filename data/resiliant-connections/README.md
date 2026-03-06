# Resilient Connections

Patterns for building resilient API clients and real-time connections with retry logic, circuit breakers, and graceful degradation. Build systems that handle failures gracefully.

## What's Inside

- Exponential backoff with jitter for retry logic
- Circuit breaker pattern (Closed → Open → Half-Open states)
- Resilient fetch wrapper with timeout and automatic retries
- Reconnecting WebSocket class with configurable max retries
- Graceful degradation with primary/fallback/cache strategy

## When to Use

- Building API clients that need to handle transient failures
- Real-time connections that should reconnect automatically
- Systems that need graceful degradation
- Any production system calling external services

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/realtime/resilient-connections
```

### OpenClaw / Moltbot / Clawbot

```bash
npx clawhub@latest install resilient-connections
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/realtime/resilient-connections .cursor/skills/resilient-connections
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/realtime/resilient-connections ~/.cursor/skills/resilient-connections
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/realtime/resilient-connections .claude/skills/resilient-connections
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/realtime/resilient-connections ~/.claude/skills/resilient-connections
```

## Related Skills

- [realtime-react-hooks](../realtime-react-hooks/) — React hook usage for real-time data
- [websocket-hub-patterns](../websocket-hub-patterns/) — Server-side WebSocket patterns

---

Part of the [Realtime](..) skill category.
