# Real-Time Dashboard

Complete guide to building real-time dashboards with streaming data, WebSocket/SSE, and live updates. Orchestrates dual-stream architecture, React hooks, and data visualization.

## What's Inside

- Architecture overview (data sources → backend services → WebSocket/SSE gateway → React application)
- Step-by-step implementation (event publishing, WebSocket gateway, React hooks, resilient connections, data visualization, animated displays)
- Component skills reference
- Key patterns (streaming over blocking, additive-only updates, connection status)
- Checklist for complete implementation

## When to Use

- Building trading or financial dashboards
- Monitoring and analytics UIs
- Any dashboard needing live data updates
- Systems with server-to-client push requirements

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/meta/realtime-dashboard
```

### OpenClaw / Moltbot / Clawbot

```bash
npx clawhub@latest install realtime-dashboard
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/meta/realtime-dashboard .cursor/skills/realtime-dashboard
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/meta/realtime-dashboard ~/.cursor/skills/realtime-dashboard
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/meta/realtime-dashboard .claude/skills/realtime-dashboard
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/meta/realtime-dashboard ~/.claude/skills/realtime-dashboard
```

## Related Skills

- `dual-stream-architecture` — Kafka + Redis publishing
- `websocket-hub-patterns` — Scalable WebSocket server
- `realtime-react-hooks` — SSE/WebSocket React hooks
- `resilient-connections` — Retry, circuit breaker
- `financial-data-visualization` — Chart theming
- `animated-financial-display` — Number animations

---

Part of the [Meta](..) skill category.
