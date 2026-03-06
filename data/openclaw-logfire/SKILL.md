---
name: openclaw-logfire
description: Pydantic Logfire observability — OTEL GenAI traces, tool call spans, token metrics, distributed tracing
version: 0.1.2
homepage: https://github.com/Ultrathink-Solutions/openclaw-logfire
metadata:
  openclaw:
    primaryEnv: LOGFIRE_TOKEN
    requires:
      env:
        - LOGFIRE_TOKEN
---

# OpenClaw Logfire Plugin

Pydantic [Logfire](https://pydantic.dev/logfire) observability plugin for OpenClaw. Traces the full agent lifecycle with [OTEL GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — tool calls, token usage, errors, and optional distributed tracing across services.

## Install

```bash
openclaw plugins install @ultrathink-solutions/openclaw-logfire
```

Set your Logfire write token:

```bash
export LOGFIRE_TOKEN="your-token"
```

Add to `openclaw.json`:

```json
{
  "plugins": {
    "entries": {
      "openclaw-logfire": {
        "enabled": true,
        "config": {}
      }
    }
  }
}
```

Restart OpenClaw. Traces appear in your Logfire dashboard.

## What It Traces

Every agent invocation produces a span tree:

```
invoke_agent chief-of-staff          (root span)
  |-- execute_tool Read              (file read)
  |-- execute_tool exec              (shell command)
  |-- execute_tool Write             (file write)
```

Spans follow OTEL GenAI semantic conventions: `gen_ai.agent.name`, `gen_ai.tool.name`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, etc.

## Metrics

- `gen_ai.client.token.usage` — token count histogram (input/output)
- `gen_ai.client.operation.duration` — agent invocation latency

## Key Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `environment` | `development` | Deployment environment label |
| `serviceName` | `openclaw-agent` | OTEL service name |
| `providerName` | — | GenAI provider (e.g. `anthropic`) |
| `captureToolInput` | `true` | Record tool arguments |
| `redactSecrets` | `true` | Strip API keys and JWTs |
| `distributedTracing.enabled` | `false` | W3C traceparent propagation |

## Security & Privacy

- **Secret redaction** (on by default): Strips API keys, platform tokens, JWTs, and credentials from recorded tool arguments before export
- **Tool output** is not captured by default (`captureToolOutput: false`)
- **Message content** is not captured by default (`captureMessageContent: false`)
- **Data destination**: Traces are exported via OTLP HTTP to Pydantic Logfire (US or EU region). No other external endpoints are contacted.
- **No local persistence**: All data is streamed to Logfire; nothing is written to disk

## External Endpoints

| URL | Data Sent |
|-----|-----------|
| `https://logfire-api.pydantic.dev` (US) | OTLP traces + metrics |
| `https://logfire-api-eu.pydantic.dev` (EU) | OTLP traces + metrics |

By using this plugin, trace and metric data is sent to Pydantic Logfire. Only install if you trust this destination.

## Links

- [GitHub](https://github.com/Ultrathink-Solutions/openclaw-logfire)
- [npm](https://www.npmjs.com/package/@ultrathink-solutions/openclaw-logfire)
- [Logfire](https://pydantic.dev/logfire)
- [Blog: We Put OpenClaw Into Production](https://ultrathinksolutions.com/the-signal/openclaw-to-production/)
