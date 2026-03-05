# WebSocket Hub Patterns

Production patterns for horizontally-scalable WebSocket connections with Redis-backed coordination. Includes lazy subscriptions, connection registry, and graceful shutdown.

## What's Inside

- Hub structure with local state and Redis coordination
- Hub main loop for connection register/unregister/broadcast
- Lazy Redis subscriptions (subscribe only when first local client joins)
- Redis message forwarding to local WebSocket connections
- Connection write pump with ping/pong and batch draining
- Connection registry for horizontal scaling across instances
- Graceful shutdown with proper cleanup

## When to Use

- Real-time bidirectional communication
- Chat applications, collaborative editing
- Live dashboards with client interactions
- Need horizontal scaling across multiple gateway instances

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/realtime/websocket-hub-patterns
```

### OpenClaw / Moltbot / Clawbot

```bash
npx clawhub@latest install websocket-hub-patterns
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/realtime/websocket-hub-patterns .cursor/skills/websocket-hub-patterns
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/realtime/websocket-hub-patterns ~/.cursor/skills/websocket-hub-patterns
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/realtime/websocket-hub-patterns .claude/skills/websocket-hub-patterns
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/realtime/websocket-hub-patterns ~/.claude/skills/websocket-hub-patterns
```

## Related Skills

- [dual-stream-architecture](../dual-stream-architecture/) — Event publishing with Kafka + Redis
- [resilient-connections](../resilient-connections/) — Connection resilience and retry logic

---

Part of the [Realtime](..) skill category.
