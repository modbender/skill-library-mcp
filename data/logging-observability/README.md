# Logging & Observability

Structured logging, distributed tracing, and metrics collection patterns for building observable systems across the three pillars: logs, metrics, and traces.

## What's Inside

- Structured JSON logging with required fields and context enrichment
- Log level guidelines (FATAL through TRACE)
- Distributed tracing with OpenTelemetry (setup, spans, context propagation, sampling)
- Metrics collection using RED method (request-driven) and USE method (resource-driven)
- Monitoring stack recommendations (Prometheus, Grafana, Jaeger, Loki)
- Alert design with severity levels and fatigue prevention
- Dashboard patterns (War Room overview, per-service dashboards)
- Observability checklist and anti-patterns

## When to Use

- Implementing logging infrastructure
- Setting up distributed tracing with OpenTelemetry
- Designing metrics collection (RED/USE methods)
- Configuring alerting and dashboards
- Reviewing observability practices
- PII/secret scrubbing in logs

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/tools/logging-observability
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/tools/logging-observability .cursor/skills/logging-observability
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/tools/logging-observability ~/.cursor/skills/logging-observability
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/tools/logging-observability .claude/skills/logging-observability
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/tools/logging-observability ~/.claude/skills/logging-observability
```

---

Part of the [Tools](..) skill category.
