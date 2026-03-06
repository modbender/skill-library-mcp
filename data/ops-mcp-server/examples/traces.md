# Jaeger Distributed Traces Examples

Investigate distributed traces to understand request flows and identify performance bottlenecks.

## Available Tools

### 1. get-services-from-jaeger

Get list of services with distributed tracing.

**Parameters:** None

### 2. get-operations-from-jaeger

Get operations for a specific service.

**Parameters:**

- `service` (required, string): Service name
- `spanKind` (optional, string): Filter by span kind - `server`, `client`, `producer`, `consumer`, `internal`

### 3. get-trace-from-jaeger

Get trace details by trace ID.

**Parameters:**

- `traceId` (required, string): 32-character hex trace ID
- `startTime` (optional, string): Start time filter (RFC 3339 format: `2024-01-15T10:00:00Z`)
- `endTime` (optional, string): End time filter (RFC 3339 format: `2024-01-15T11:00:00Z`)

### 4. find-traces-from-jaeger

Search for traces based on criteria.

**Parameters:**

- `serviceName` (required, string): Service name to search
- `startTimeMin` (required, string): Start of time interval (RFC 3339: `2024-01-15T10:00:00Z`)
- `startTimeMax` (required, string): End of time interval (RFC 3339: `2024-01-15T11:00:00Z`)
- `operationName` (optional, string): Filter by operation name
- `durationMin` (optional, string): Minimum duration in milliseconds
- `durationMax` (optional, string): Maximum duration in milliseconds
- `searchDepth` (optional, string): Maximum number of results

## Time Format: RFC 3339

All time parameters use RFC 3339 format:

```
2024-01-15T10:30:00Z
2024-01-15T14:30:00+08:00
```

Generate RFC 3339 timestamps:

```bash
# Current time
date -u +"%Y-%m-%dT%H:%M:%SZ"

# Specific time (macOS)
date -u -j -f "%Y-%m-%d %H:%M:%S" "2024-01-15 10:00:00" +"%Y-%m-%dT%H:%M:%SZ"

# 1 hour ago
date -u -v-1H +"%Y-%m-%dT%H:%M:%SZ"
```

## Example 1: List Services

```bash
# List all services
npx mcporter call ops-mcp-server get-services-from-jaeger
```

### Expected Response

```json
{
  "services": [
    "api-gateway",
    "user-service",
    "payment-service",
    "inventory-service",
    "notification-service"
  ]
}
```

## Example 2: List Operations

```bash
# Get all operations
npx mcporter call ops-mcp-server get-operations-from-jaeger service="api-gateway"

# Filter by span kind
npx mcporter call ops-mcp-server get-operations-from-jaeger service="user-service" spanKind="server"
```

### Span Kinds

| Kind | Description | Example |
|------|-------------|---------|
| `server` | Server-side handling of request | HTTP endpoint handler |
| `client` | Client-side request to remote service | HTTP client call, DB query |
| `producer` | Message producer | Kafka producer |
| `consumer` | Message consumer | Kafka consumer |
| `internal` | Internal operation | Function call, algorithm |

## Example 3: Find Traces

```bash
# Find recent traces
npx mcporter call ops-mcp-server find-traces-from-jaeger \
  serviceName="api-gateway" startTimeMin="2024-01-15T10:00:00Z" startTimeMax="2024-01-15T11:00:00Z"

# Find slow traces
npx mcporter call ops-mcp-server find-traces-from-jaeger \
  serviceName="api-gateway" startTimeMin="2024-01-15T09:00:00Z" startTimeMax="2024-01-15T11:00:00Z" durationMin="1000"

# Find traces for operation
npx mcporter call ops-mcp-server find-traces-from-jaeger \
  serviceName="checkout-service" operationName="POST /api/checkout" startTimeMin="2024-01-15T10:00:00Z" startTimeMax="2024-01-15T11:00:00Z" searchDepth="100"
```

## Example 4: Get Trace Details

```bash
# Get trace by ID
npx mcporter call ops-mcp-server get-trace-from-jaeger traceId="abc123def456789012345678901234"

# Get trace with time filter
npx mcporter call ops-mcp-server get-trace-from-jaeger \
  traceId="abc123def456789012345678901234" startTime="2024-01-15T10:00:00Z" endTime="2024-01-15T11:00:00Z"
```

### Trace ID Format

- **Length**: 32 hexadecimal characters
- **Example**: `abc123def456789012345678901234`
- **OpenTelemetry compatible** format

## Example 5: Performance Investigation

```bash
# Find slowest operations
npx mcporter call ops-mcp-server find-traces-from-jaeger \
  serviceName="api-gateway" startTimeMin="2024-01-15T10:00:00Z" startTimeMax="2024-01-15T11:00:00Z" durationMin="1000" searchDepth="10"
```

## Duration Filter (in milliseconds)

Common duration values:

- `100` - 100ms (0.1 seconds)
- `500` - 500ms (0.5 seconds)
- `1000` - 1 second
- `2000` - 2 seconds
- `5000` - 5 seconds

## Search Depth

Limits the number of traces returned:

- Default: varies by Jaeger configuration
- Recommended: `10` to `100` for interactive queries
- Maximum: depends on Jaeger backend settings

## Expected Response Format

### Find Traces Response

```json
{
  "traces": [
    {
      "traceId": "abc123def456789012345678901234",
      "spans": [
        {
          "spanId": "def456789012",
          "operationName": "GET /api/users",
          "startTime": "2024-01-15T10:30:00Z",
          "duration": 1200,
          "service": "api-gateway",
          "tags": {
            "http.method": "GET",
            "http.status_code": 200
          }
        }
      ]
    }
  ]
}
```

### Get Trace Response

Returns both Jaeger and OpenTelemetry formats:

- Original Jaeger format for compatibility
- Converted OpenTelemetry format with standardized IDs

```json
{
  "jaeger": { /* original format */ },
  "opentelemetry": {
    "resourceSpans": [
      {
        "resource": {
          "attributes": [
            {"key": "service.name", "value": {"stringValue": "api-gateway"}}
          ]
        },
        "scopeSpans": [
          {
            "spans": [
              {
                "traceId": "abc123def456789012345678901234",
                "spanId": "def456789012",
                "name": "GET /api/users",
                "kind": "SPAN_KIND_SERVER",
                "startTimeUnixNano": "1705318200000000000",
                "endTimeUnixNano": "1705318201200000000"
              }
            ]
          }
        ]
      }
    ]
  }
}
```

## Troubleshooting

### No Traces Found

**Problem:** find-traces returns empty

**Solutions:**

1. Verify service name: `get-services-from-jaeger`
2. Check time range is correct (RFC 3339 format)
3. Expand time range
4. Remove optional filters (operation, duration)

### Invalid Trace ID

**Problem:** Error getting trace by ID

**Solutions:**

1. Verify trace ID is 32 hex characters
2. Check trace ID from find-traces results
3. Ensure time range includes the trace

### Time Format Error

**Problem:** Invalid time format error

**Solutions:**

1. Use RFC 3339 format: `2024-01-15T10:30:00Z`
2. Include timezone (Z for UTC, or +08:00)
3. Use correct separators (T between date and time)

```bash
# Correct
2024-01-15T10:30:00Z

# Incorrect
2024-01-15 10:30:00
2024/01/15 10:30:00
```

## Best Practices

### 1. Start with Services, Then Operations

```bash
# Step 1: List services
npx mcporter call ops-mcp-server get-services-from-jaeger

# Step 2: List operations
npx mcporter call ops-mcp-server get-operations-from-jaeger service="api-gateway"

# Step 3: Find traces
npx mcporter call ops-mcp-server find-traces-from-jaeger \
  serviceName="api-gateway" operationName="GET /api/users" startTimeMin="2024-01-15T10:00:00Z" startTimeMax="2024-01-15T11:00:00Z"
```

### 2. Use Reasonable Time Ranges

```bash
# Good - specific time window
npx mcporter call ops-mcp-server find-traces-from-jaeger \
  serviceName="api-gateway" startTimeMin="2024-01-15T10:00:00Z" startTimeMax="2024-01-15T11:00:00Z"
```

### 3. Filter by Duration for Performance Issues

```bash
# Good - focus on slow traces
npx mcporter call ops-mcp-server find-traces-from-jaeger \
  serviceName="api-gateway" durationMin="1000" startTimeMin="2024-01-15T10:00:00Z" startTimeMax="2024-01-15T11:00:00Z"
```

### 4. Limit Search Depth for Large Datasets

```bash
# Good - limited results
npx mcporter call ops-mcp-server find-traces-from-jaeger \
  serviceName="api-gateway" searchDepth="50" startTimeMin="2024-01-15T10:00:00Z" startTimeMax="2024-01-15T11:00:00Z"
```

## Real-World Scenarios

### Scenario 1: Investigate Slow API

```bash
# Find slow traces
npx mcporter call ops-mcp-server find-traces-from-jaeger \
  serviceName="api-gateway" durationMin="2000" startTimeMin="2024-01-15T10:00:00Z" startTimeMax="2024-01-15T11:00:00Z"

# Get details of specific trace
npx mcporter call ops-mcp-server get-trace-from-jaeger traceId="abc123def456789012345678901234"
```

### Scenario 2: Debug Payment Failures

```bash
# Find payment operations
npx mcporter call ops-mcp-server get-operations-from-jaeger service="payment-service"

# Find failed traces
npx mcporter call ops-mcp-server find-traces-from-jaeger \
  serviceName="payment-service" startTimeMin="2024-01-14T10:00:00Z" startTimeMax="2024-01-15T10:00:00Z"

# Analyze failure
npx mcporter call ops-mcp-server get-trace-from-jaeger traceId="def789abc123456789012345678901234"
```

### Scenario 3: Service Dependency Mapping

```bash
# Find traces for api-gateway
npx mcporter call ops-mcp-server find-traces-from-jaeger \
  serviceName="api-gateway" startTimeMin="2024-01-15T10:00:00Z" startTimeMax="2024-01-15T11:00:00Z"

# Analyze trace dependencies
npx mcporter call ops-mcp-server get-trace-from-jaeger traceId="abc123def456789012345678901234"
```

## Span Kind Usage

### Server Spans

```bash
# HTTP endpoints, gRPC services
npx mcporter call ops-mcp-server get-operations-from-jaeger service="api-gateway" spanKind="server"
```

### Client Spans

```bash
# HTTP calls, database queries, external API calls
npx mcporter call ops-mcp-server get-operations-from-jaeger service="api-gateway" spanKind="client"
```

### Internal Spans

```bash
# Business logic, algorithms, internal operations
npx mcporter call ops-mcp-server get-operations-from-jaeger service="payment-service" spanKind="internal"
```

## Reference

- **Tools**: `get-services-from-jaeger`, `get-operations-from-jaeger`, `get-trace-from-jaeger`, `find-traces-from-jaeger`
- **OpenTelemetry**: <https://opentelemetry.io/docs/>
- **Jaeger Documentation**: <https://www.jaegertracing.io/docs/>
- **RFC 3339 Format**: <https://datatracker.ietf.org/doc/html/rfc3339#section-5.6>
- **Span Kinds**: <https://opentelemetry.io/docs/concepts/signals/traces/#span-kind>
