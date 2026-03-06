# Real-Time React Hooks

Production patterns for real-time data in React applications using SSE, WebSocket, and SWR integration. Covers connection management, reconnection logic, and optimistic updates.

## What's Inside

- SSE hook (`useSSE`) for server-sent events
- WebSocket hook with automatic reconnection and exponential backoff
- SWR integration for real-time cache updates with optimistic mutations
- Subscription hook for multi-channel WebSocket communication
- Connection status indicator component

## When to Use

- React apps needing live data updates
- Dashboards with real-time metrics
- Chat interfaces, notifications
- Any UI that should update without refresh

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/realtime/realtime-react-hooks
```

### OpenClaw / Moltbot / Clawbot

```bash
npx clawhub@latest install realtime-react-hooks
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/realtime/realtime-react-hooks .cursor/skills/realtime-react-hooks
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/realtime/realtime-react-hooks ~/.cursor/skills/realtime-react-hooks
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/realtime/realtime-react-hooks .claude/skills/realtime-react-hooks
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/realtime/realtime-react-hooks ~/.claude/skills/realtime-react-hooks
```

## Related Skills

- [resilient-connections](../resilient-connections/) — Retry logic and fault tolerance
- [websocket-hub-patterns](../websocket-hub-patterns/) — Server-side WebSocket patterns
- [design-systems/animated-financial-display](../../design-systems/animated-financial-display/) — Number animations

---

Part of the [Realtime](..) skill category.
