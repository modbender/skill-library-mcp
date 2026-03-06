# Dual-Stream Architecture

Dual-stream event publishing combining Kafka for durability with Redis Pub/Sub for real-time delivery. Publish events to both systems simultaneously for guaranteed delivery and instant updates.

## What's Inside

- Core dual-publisher pattern (Kafka + Redis Pub/Sub)
- Architecture diagram showing ingester, publisher, and consumer flow
- Channel naming conventions for event routing
- Batch publishing for high-throughput scenarios
- Decision tree for choosing single vs dual stream
- Edge case handling (Redis down, client mid-stream, backpressure)

## When to Use

- Event-driven systems needing both durability AND real-time
- WebSocket/SSE backends that push live updates
- Dashboards showing events as they happen
- Kafka consumers have lag but users expect instant updates

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/realtime/dual-stream-architecture
```

### OpenClaw / Moltbot / Clawbot

```bash
npx clawhub@latest install dual-stream-architecture
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/realtime/dual-stream-architecture .cursor/skills/dual-stream-architecture
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/realtime/dual-stream-architecture ~/.cursor/skills/dual-stream-architecture
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/realtime/dual-stream-architecture .claude/skills/dual-stream-architecture
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/realtime/dual-stream-architecture ~/.claude/skills/dual-stream-architecture
```

## Related Skills

- [websocket-hub-patterns](../websocket-hub-patterns/) — WebSocket gateway patterns
- [resilient-connections](../resilient-connections/) — Connection resilience and retry logic
- [backend/service-layer-architecture](../../backend/service-layer-architecture/) — Service integration

---

Part of the [Realtime](..) skill category.
