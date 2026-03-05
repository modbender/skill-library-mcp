---
name: api-endpoint-tester
description: CLI tool to test REST API endpoints with various HTTP methods, headers, and payloads.
version: 1.0.0
author: skill-factory
metadata:
  openclaw:
    requires:
      bins:
        - python3
      packages:
        - requests
---

# API Endpoint Tester

## What This Does

A simple CLI tool to send HTTP requests to REST API endpoints and validate responses. Supports GET, POST, PUT, DELETE, PATCH methods with custom headers and request bodies (JSON or form data).

## When To Use

- You need to test API endpoints manually or in scripts
- You want to validate HTTP status codes and response formats
- You're debugging API integrations and need quick requests
- You need to check if an endpoint is reachable and responding correctly

## Usage

Basic GET request:
python3 scripts/main.py run --url "https://api.example.com/users" --method GET

POST with JSON body:
python3 scripts/main.py run --url "https://api.example.com/users" --method POST --body '{"name": "John", "email": "john@example.com"}'

With custom headers:
python3 scripts/main.py run --url "https://api.example.com/users" --method GET --headers '{"Authorization": "Bearer token123"}'

## Examples

### Example 1: Simple GET request

```bash
python3 scripts/main.py run --url "https://jsonplaceholder.typicode.com/posts/1" --method GET
```

Output:
```json
{
  "status": "success",
  "status_code": 200,
  "headers": {
    "content-type": "application/json; charset=utf-8"
  },
  "body": {
    "userId": 1,
    "id": 1,
    "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
    "body": "quia et suscipit\nsuscipit recusandae consequuntur expedita et cum\nreprehenderit molestiae ut ut quas totam\nnostrum rerum est autem sunt rem eveniet architecto"
  },
  "response_time_ms": 245
}
```

### Example 2: POST with validation

```bash
python3 scripts/main.py run --url "https://jsonplaceholder.typicode.com/posts" --method POST --body '{"title": "foo", "body": "bar", "userId": 1}' --expected-status 201
```

## Requirements

- Python 3.x
- `requests` library (install via pip if not available)

## Limitations

- This is a CLI tool, not an auto-integration plugin
- Does not support WebSocket or streaming endpoints
- Limited to HTTP/HTTPS protocols (no gRPC, GraphQL, etc.)
- No built-in authentication beyond headers
- Does not save test suites or history (single request at a time)
- Timeouts default to 10 seconds