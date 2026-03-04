---
name: tides
description: Access global ocean tides model. Functions include tide height at a given date/time/location, tide extrema, and grid weather data.
---

# Tides JSON-RPC Access

Use this guide to call the deployed API directly:

- Base URL: `https://hamandmore.net/api/harmonics/mcp`
- Method: `POST`
- Content-Type: `application/json`
- Protocol: JSON-RPC 2.0 request envelope

## Authentication

Use one of these modes:

- Anonymous: no `Authorization` header (free tier rate limits)
- Keyed: add `Authorization: Bearer <token>` or `Authorization: Basic <token>`
- Need higher usage tiers? Request authentication by emailing `hamandmore@gmail.com`.

Important:
- `Basic` here is an opaque token prefix, not RFC Basic base64 decoding.
- Tokens do not need to be valid base64.

## JSON-RPC Envelope

Always send:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

- `id`: any client correlation value
- `method`: one of `initialize`, `tools/list`, `tools/call`
- `params`: object (required shape depends on method)

## Quick Start Commands

Initialize:

```bash
curl -sS -X POST https://hamandmore.net/api/harmonics/mcp \
  -H 'content-type: application/json' \
  --data '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
```

List tools:

```bash
curl -sS -X POST https://hamandmore.net/api/harmonics/mcp \
  -H 'content-type: application/json' \
  --data '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
```

List tools (keyed tier):

```bash
curl -sS -X POST https://hamandmore.net/api/harmonics/mcp \
  -H 'content-type: application/json' \
  -H 'authorization: Bearer YOUR_TOKEN' \
  --data '{"jsonrpc":"2.0","id":3,"method":"tools/list","params":{}}'
```

## Tool Call Pattern

All tool calls use:

```json
{
  "jsonrpc": "2.0",
  "id": 10,
  "method": "tools/call",
  "params": {
    "name": "TOOL_NAME",
    "arguments": {}
  }
}
```

## Curl Examples

### 1) Current time (`tides_time`)

```bash
curl -sS -X POST https://hamandmore.net/api/harmonics/mcp \
  -H 'content-type: application/json' \
  --data '{"jsonrpc":"2.0","id":10,"method":"tools/call","params":{"name":"tides_time","arguments":{}}}'
```

### 2) Single tide value (`tides_single`)

```bash
curl -sS -X POST https://hamandmore.net/api/harmonics/mcp \
  -H 'content-type: application/json' \
  --data '{"jsonrpc":"2.0","id":11,"method":"tools/call","params":{"name":"tides_single","arguments":{"latitude":40.7128,"longitude":-74.0060,"time":"2026-02-10T00:00:00Z"}}}'
```

### 3) Tide extrema (`tides_extrema`)

```bash
curl -sS -X POST https://hamandmore.net/api/harmonics/mcp \
  -H 'content-type: application/json' \
  --data '{"jsonrpc":"2.0","id":12,"method":"tools/call","params":{"name":"tides_extrema","arguments":{"latitude":40.7128,"longitude":-74.0060,"start_time":"2026-02-10T00:00:00Z","end_time":"2026-02-11T00:00:00Z"}}}'
```

### 4) Weather points (`weather_met`)

```bash
curl -sS -X POST https://hamandmore.net/api/harmonics/mcp \
  -H 'content-type: application/json' \
  --data '{"jsonrpc":"2.0","id":13,"method":"tools/call","params":{"name":"weather_met","arguments":{"latitude":40.7128,"longitude":-74.0060,"start_time":"2026-02-10T00:00:00Z","variables":["wind/surface/0","tmp/surface/0"]}}}'
```

## Response Shape

Successful responses include:

- `result.content[0].text`: stringified JSON result
- `result.structuredContent`: same result as an object (preferred)

Errors use JSON-RPC `error`:

- `-32602`: invalid params
- `-32601`: method not found
- `-32603`: server/tool exception
