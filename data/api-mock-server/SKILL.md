---
name: api-mock-server
description: Spin up mock API servers from OpenAPI/Swagger specs with
  auto-generated test data.
---


# API Mock Server

Instantly create a mock API server from an OpenAPI/Swagger spec.

## Instructions

### Step 1: Get the Spec
Accept from user:
- File path (JSON/YAML)
- URL to a spec
- Inline endpoint definitions → convert to OpenAPI 3.0

If no spec exists, help define endpoints interactively and generate one.

### Step 2: Start the Mock Server
```bash
# Primary: Prism (Stoplight)
npx @stoplight/prism-cli mock <spec-file> --port ${PORT:-4010} --dynamic

# Alternative: json-server for simple REST
npx json-server --watch db.json --port ${PORT:-4010}
```
- `--dynamic` generates realistic fake data from schema constraints
- Default port: 4010

### Step 3: Verify
```bash
# Test a sample endpoint
curl -s http://localhost:4010/api/resource | jq .

# List all routes (Prism logs them on startup)
```

### Fallback: Custom Express Server
If prism is unavailable, generate a minimal Express server:
```javascript
const express = require('express');
const app = express();
app.use(express.json());
// Auto-generate routes from spec...
```

## Edge Cases

- **CORS**: Add `--cors` flag or set `Access-Control-Allow-Origin: *` for browser testing
- **Auth mocking**: Return 401 for endpoints with security schemes when no token provided
- **Large specs**: Prism handles them fine; json-server may need splitting
- **Port conflicts**: Check with `lsof -i :<port>` before starting

## Security

- Mock servers are for **development only** — never expose to public internet
- Don't include real API keys or credentials in mock responses

## Requirements

- Node.js 16+ (for npx)
- No API keys needed
