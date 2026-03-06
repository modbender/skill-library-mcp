# OpenClaw Sentry Plugin — Implementation Guide

How to build an OpenClaw plugin that sends errors, structured logs, and performance traces to Sentry using `@sentry/node`.

---

## Overview

The plugin hooks into three OpenClaw mechanisms:

| Mechanism | What it captures |
|---|---|
| `@sentry/node` init | Unhandled errors, process crashes |
| `onDiagnosticEvent()` | Performance traces — LLM calls, message processing, webhook errors |
| `registerLogTransport()` | Structured logs from the gateway |

No OpenTelemetry dependencies needed. The Sentry Node SDK handles everything.

---

## Install Dependencies

```bash
npm install @sentry/node @sentry/core
```

> `@sentry/core` is needed for `_INTERNAL_flushLogsBuffer` — Sentry's log buffer doesn't auto-flush until 100 items accumulate, which low-volume services may never hit.

---

## Plugin Code

See the full implementation at https://github.com/sergical/openclaw-plugin-sentry

Key implementation details:

### Diagnostic Events → Sentry Spans

```typescript
import * as Sentry from "@sentry/node";

// model.usage → ai.chat span with GenAI semantic conventions
function recordModelUsage(evt) {
  const endTimeMs = evt.ts;
  const durationMs = evt.durationMs ?? 100;
  const startTimeMs = endTimeMs - durationMs;

  const span = Sentry.startInactiveSpan({
    op: "ai.chat",
    name: `chat ${evt.model}`,
    startTime: startTimeMs,       // Sentry v10 accepts ms (NOT seconds!)
    forceTransaction: true,
    attributes: {
      "gen_ai.operation.name": "chat",
      "gen_ai.system": evt.provider ?? "unknown",
      "gen_ai.request.model": evt.model ?? "unknown",
      "gen_ai.usage.input_tokens": evt.usage.input ?? 0,
      "gen_ai.usage.output_tokens": evt.usage.output ?? 0,
    },
  });
  span?.end(endTimeMs);
}
```

### Log Forwarding with Buffer Flush

```typescript
import { _INTERNAL_flushLogsBuffer } from "@sentry/core";

// In start():
// Sentry buffers logs until 100 items. Flush every 30s for low-volume instances.
const logFlushInterval = setInterval(() => {
  const client = Sentry.getClient();
  if (client) _INTERNAL_flushLogsBuffer(client);
}, 30_000);

// In stop():
clearInterval(logFlushInterval);
// Flush log buffer BEFORE flushing transport — otherwise buffered logs are lost
const client = Sentry.getClient();
if (client) _INTERNAL_flushLogsBuffer(client);
await Sentry.flush(5000);
```

### Log Transport Format

OpenClaw's log transport uses numeric keys as positional args:
- Key `"0"` = subsystem tag (e.g. `{"subsystem":"plugins"}`)
- Key `"1"` = message string
- `_meta` has `logLevelName`, `name`, `date`

```typescript
function forwardLog(logObj: Record<string, unknown>): void {
  const meta = logObj._meta as { logLevelName?: string } | undefined;
  const level = (meta?.logLevelName ?? "INFO").toLowerCase();

  // Extract subsystem and message from positional args
  const numericEntries = Object.entries(logObj)
    .filter(([key]) => /^\d+$/.test(key))
    .sort((a, b) => Number(a[0]) - Number(b[0]));

  let subsystem = "";
  let message = "";

  if (numericEntries.length >= 2) {
    subsystem = String(numericEntries[0][1]);
    message = String(numericEntries[numericEntries.length - 1][1]);
  } else if (numericEntries.length === 1) {
    message = String(numericEntries[0][1]);
  }

  const attrs: Record<string, string> = {};
  if (subsystem) attrs["openclaw.subsystem"] = subsystem;

  // Route to Sentry.logger at appropriate level
  switch (level) {
    case "debug": case "trace": Sentry.logger.debug(message, attrs); break;
    case "warn": Sentry.logger.warn(message, attrs); break;
    case "error": case "fatal": Sentry.logger.error(message, attrs); break;
    default: Sentry.logger.info(message, attrs);
  }
}
```

---

## Configuration

Add to `openclaw.json` — note config goes under `plugins.entries.sentry.config`:

```json
{
  "plugins": {
    "entries": {
      "sentry": {
        "enabled": true,
        "config": {
          "dsn": "https://examplePublicKey@o0.ingest.sentry.io/0",
          "environment": "production",
          "tracesSampleRate": 1.0,
          "enableLogs": true
        }
      }
    }
  }
}
```

| Field | Required | Description |
|---|---|---|
| `dsn` | **yes** | Sentry DSN from your project's Client Keys |
| `environment` | no | `"production"`, `"staging"`, etc. Default: `"production"` |
| `tracesSampleRate` | no | `0.0` – `1.0`. Default: `1.0` (sample everything) |
| `enableLogs` | no | Enable structured log forwarding. Default: `true` |

---

## Gotchas

### Sentry v10 Timestamps
`startTime` and `span.end()` accept **milliseconds** (or Date objects or `[sec, ns]` tuples). Do NOT divide by 1000 — that creates 0ms duration spans.

### Log Buffer
Sentry's structured logs buffer internally (max 100 items). `Sentry.flush()` does NOT flush this buffer. You must call `_INTERNAL_flushLogsBuffer(client)` from `@sentry/core` explicitly, then `Sentry.flush()` to send the resulting envelope.

### Plugin Config Path
Config must be at `plugins.entries.sentry.config.dsn`, not `plugins.entries.sentry.dsn`. The plugin's `configSchema` needs `additionalProperties: true`.

### Module Isolation
OpenClaw's bundler creates separate chunks for gateway and plugin-sdk, so `onDiagnosticEvent` and `registerLogTransport` may use different listener Sets. If events aren't reaching the plugin, check if the `globalThis.__oc_diag` / `globalThis.__oc_log_transports` patches are applied.

---

## What You'll See in Sentry

### Errors
Unhandled exceptions, webhook errors, and session stuck warnings.

### Traces
- `ai.chat` spans with GenAI semantic conventions (`gen_ai.request.model`, `gen_ai.usage.*`)
- `openclaw.message` spans for message processing with duration

### Logs
Structured gateway logs with level mapping and `openclaw.subsystem` attributes. View with:

```bash
sentry log list <org>/<project>
sentry log list <org>/<project> -f    # stream in real-time
```

---

## Docs

- Sentry Node SDK: https://docs.sentry.io/platforms/javascript/guides/node/
- Sentry Structured Logs: https://docs.sentry.io/platforms/javascript/guides/node/logs/
- Sentry CLI Logs: https://cli.sentry.dev/commands/log/
- Plugin source: https://github.com/sergical/openclaw-plugin-sentry
