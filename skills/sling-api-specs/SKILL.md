---
name: sling-api-specs
description: >
  Build REST API specifications for Sling data extraction.
  Use when creating API specs, configuring authentication (OAuth, API key, Bearer token, HMAC), setting up pagination (cursor, offset, page), processing responses, handling rate limits, chaining endpoints with queues, or implementing incremental sync.
---

# API Specifications

API specs are YAML definitions for extracting data from REST APIs. They handle authentication, pagination, response processing, and incremental sync automatically.

## When to Use

- Extract data from REST APIs (GET endpoints only)
- Build incremental sync workflows
- Handle complex pagination patterns
- Process nested JSON responses
- Chain multiple API calls with queues

## Basic Structure

```yaml
name: "My API"
description: "Data extraction from My API"

authentication:
  type: "static"
  headers:
    Authorization: "Bearer {secrets.api_token}"

defaults:
  state:
    base_url: "https://api.example.com/v1"
  request:
    headers:
      Accept: "application/json"

endpoints:
  users:
    description: "Fetch users"
    request:
      url: "{state.base_url}/users"
    response:
      records:
        jmespath: "data[]"
        primary_key: ["id"]
```

## MCP Operations

### Parse a Spec
```json
{
  "action": "parse",
  "input": {"file_path": "/path/to/spec.yaml"}
}
```

### Test Endpoints
```json
{
  "action": "test",
  "input": {
    "connection": "MY_API",
    "endpoints": ["users"],
    "debug": true,
    "limit": 10
  }
}
```

## Topics Reference

This skill includes detailed documentation for each aspect of API specification building:

| Topic | Description |
|-------|-------------|
| [AUTHENTICATION.md](AUTHENTICATION.md) | All 8 authentication types (static, basic, OAuth2, AWS, HMAC, sequence) |
| [ENDPOINTS.md](ENDPOINTS.md) | Endpoint configuration, setup/teardown sequences |
| [REQUEST.md](REQUEST.md) | HTTP request configuration, rate limiting |
| [PAGINATION.md](PAGINATION.md) | All pagination patterns (cursor, offset, page, link header) |
| [RESPONSE.md](RESPONSE.md) | Record extraction, deduplication |
| [PROCESSORS.md](PROCESSORS.md) | Data transformations, aggregations |
| [VARIABLES.md](VARIABLES.md) | Variable scopes, expressions, rendering order |
| [QUEUES.md](QUEUES.md) | Endpoint chaining, iteration |
| [INCREMENTAL.md](INCREMENTAL.md) | Sync state, context variables |
| [DYNAMIC.md](DYNAMIC.md) | Runtime endpoint generation |
| [FUNCTIONS.md](FUNCTIONS.md) | Expression functions reference |
| [RULES.md](RULES.md) | Response rules, retries, error handling |

## Quick Reference

### Authentication Types

| Type | Use Case |
|------|----------|
| `static` | API key, Bearer token |
| `basic` | Username/password |
| `oauth2` | OAuth 2.0 flows (client_credentials, authorization_code, device_code) |
| `aws-sigv4` | AWS services |
| `hmac` | Crypto exchanges, custom signing |
| `sequence` | Multi-step custom auth |

### Pagination Patterns

| Pattern | Example |
|---------|---------|
| Cursor | `starting_after`, `page_token` |
| Offset | `offset` + `limit` |
| Page | `page` number |
| Link header | GitHub-style `rel="next"` |

### Variable Scopes

| Scope | Description |
|-------|-------------|
| `secrets.*` | Credentials from connection |
| `state.*` | Endpoint state variables |
| `sync.*` | Persisted from previous run |
| `response.*` | HTTP response data |
| `record.*` | Current record in processor |
| `queue.*` | Endpoint chaining |

## Full Documentation

See https://docs.slingdata.io/concepts/api-specs.md for complete reference.
