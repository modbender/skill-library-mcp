# @ultrathink-solutions/openclaw-logfire

[![npm version](https://img.shields.io/npm/v/@ultrathink-solutions/openclaw-logfire)](https://www.npmjs.com/package/@ultrathink-solutions/openclaw-logfire)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Pydantic [Logfire](https://pydantic.dev/logfire) observability plugin for [OpenClaw](https://openclaw.ai).

Full agent lifecycle tracing aligned with [OTEL GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — tool calls, token metrics, error stack traces, and optional distributed tracing across services.

> **Real-world context:** We built this plugin as part of deploying OpenClaw into production on the [Ultrathink Axon platform](https://ultrathinksolutions.com/the-signal/openclaw-to-production/). The architecture and design decisions are detailed in that post.

## Quickstart

```bash
npm install @ultrathink-solutions/openclaw-logfire
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

Restart OpenClaw. That's it — traces appear in your Logfire dashboard.

## What You Get

### Span Hierarchy

Every agent invocation produces a trace tree:

```
invoke_agent chief-of-staff          (root span)
  |-- execute_tool Read              (file read)
  |-- execute_tool exec              (shell command)
  |-- execute_tool Write             (file write)
  |-- execute_tool web_search        (web search)
```

### Attributes (OTEL GenAI Semantic Conventions)

| Attribute | Example | Description |
|-----------|---------|-------------|
| `gen_ai.operation.name` | `invoke_agent` | Operation type |
| `gen_ai.agent.name` | `chief-of-staff` | Agent identifier |
| `gen_ai.conversation.id` | `session_abc123` | Session key |
| `gen_ai.tool.name` | `Read` | Tool being called |
| `gen_ai.tool.call.arguments` | `{"path": "/..."}` | Tool input (opt-in) |
| `gen_ai.usage.input_tokens` | `1024` | Prompt tokens |
| `gen_ai.usage.output_tokens` | `512` | Completion tokens |
| `error.type` | `ToolExecutionError` | Error classification |
| `exception.stacktrace` | `Error: ...` | Full stack trace |
| `openclaw.workspace` | `chief-of-staff` | Workspace name |
| `openclaw.channel` | `slack` | Message source |

### Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `gen_ai.client.token.usage` | Histogram | Token counts by type (input/output) |
| `gen_ai.client.operation.duration` | Histogram | Agent invocation latency (seconds) |

### Error Tracing

Tool failures include full OTEL exception events:

- `exception.type` — Error class name
- `exception.message` — Error description
- `exception.stacktrace` — Full stack trace

Errors propagate up the span tree so the root `invoke_agent` span is marked as errored.

## Configuration

All settings are optional. Sensible defaults work out of the box.

```jsonc
{
  "plugins": {
    "entries": {
      "openclaw-logfire": {
        "enabled": true,
        "config": {
          // Logfire project (enables clickable trace links in logs)
          "projectUrl": "https://logfire.pydantic.dev/myorg/myproject",
          "region": "us",           // "us" or "eu"
          "environment": "production",
          "serviceName": "openclaw-agent",

          // GenAI provider name for OTEL compliance
          "providerName": "anthropic",

          // Trace depth controls
          "captureToolInput": true,       // Record tool arguments
          "captureToolOutput": false,     // Record tool results (verbose)
          "toolInputMaxLength": 2048,     // Truncation limit
          "captureStackTraces": true,     // Stack traces on errors
          "captureMessageContent": false, // Record message text (privacy)
          "redactSecrets": true,          // Strip API keys from tool args

          // Distributed tracing (opt-in)
          "distributedTracing": {
            "enabled": false,
            "urlPatterns": ["https://api.mycompany.com/*"]
          },

          // Metrics
          "enableMetrics": true,

          // Trace links
          "enableTraceLinks": true
        }
      }
    }
  }
}
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `LOGFIRE_TOKEN` | Logfire write token (required) |
| `LOGFIRE_ENVIRONMENT` | Deployment environment fallback |
| `LOGFIRE_PROJECT_URL` | Project URL fallback |
| `LOGFIRE_PROVIDER_NAME` | Provider name fallback |

### Secret Redaction

When `redactSecrets: true` (default), the plugin strips values matching common patterns before recording tool arguments:

- API keys (`api_key: sk_live_...`)
- Platform tokens (`ghp_`, `gho_`, `glpat_`, `xoxb-`, etc.)
- JWTs (`eyJ...`)
- Bearer tokens, passwords, credentials

## Distributed Tracing

Connect OpenClaw traces to your backend services. When enabled, the plugin injects `traceparent` headers into HTTP calls made by exec/Bash tools.

```jsonc
{
  "distributedTracing": {
    "enabled": true,
    "injectIntoCommands": true,      // Add traceparent to curl/wget/httpie
    "extractFromWebhooks": true,     // Extract traceparent from inbound webhooks
    "urlPatterns": [                 // Only inject for matching URLs
      "https://api.mycompany.com/*",
      "http://localhost:8000/*"
    ]
  }
}
```

This produces connected traces across services:

```
OpenClaw: invoke_agent chief-of-staff
  |-- execute_tool exec (curl POST /v1/api)
       |-- [Backend] FastAPI: POST /v1/api
            |-- database query
            |-- LLM call
```

Your backend must support W3C trace context extraction (most frameworks do: FastAPI with Logfire, Express with OTEL, etc.).

## Architecture

```
openclaw-logfire/src/
  index.ts              Plugin entry point + hook wiring
  config.ts             Typed configuration with defaults
  otel.ts               OTEL SDK initialization (Logfire OTLP)
  hooks/
    before-agent-start  invoke_agent span creation
    before-tool-call    execute_tool span + context propagation
    tool-result-persist Tool span close + errors + stack traces
    agent-end           Span close + metrics + trace link
    message-received    Channel attribution + inbound context
  context/
    span-store          Session -> active spans (LIFO tool stack)
    propagation         W3C traceparent inject/extract
  metrics/
    genai-metrics       Token usage + operation duration histograms
  events/
    inference-details   Opt-in inference operation event
```

### OpenClaw Hooks Used

| Hook | Purpose |
|------|---------|
| `before_agent_start` | Create root `invoke_agent` span |
| `before_tool_call` | Create `execute_tool` child span |
| `tool_result_persist` | Close tool span, record errors |
| `agent_end` | Close spans, emit metrics |
| `message_received` | Enrich with channel info |

Requires OpenClaw >= 2026.2.1 (`before_tool_call` was wired in that version).

## Development

```bash
git clone https://github.com/Ultrathink-Solutions/openclaw-logfire
cd openclaw-logfire
npm install
npm run typecheck
npm test
```

### Local testing with OpenClaw

```bash
# Symlink into OpenClaw extensions
ln -s $(pwd) ~/.openclaw/extensions/openclaw-logfire

# Or add to openclaw.json
# "plugins": { "load": { "paths": ["./path/to/openclaw-logfire"] } }

export LOGFIRE_TOKEN="your-write-token"
openclaw restart
openclaw plugins list  # Should show "openclaw-logfire" as enabled
```

## Built By

[Ultrathink Solutions](https://ultrathinksolutions.com) — production-grade AI agent infrastructure. We help teams close the gap between AI demos and production systems.

- [We Put OpenClaw Into Production in a Weekend](https://ultrathinksolutions.com/the-signal/openclaw-to-production/) — the architecture behind this plugin
- [The AI Execution Gap](https://ultrathinksolutions.com/the-signal/ai-execution-gap/) — why most AI projects stall between POC and production

## License

MIT
