# json-validate

Validate JSON syntax and structure with detailed error reporting.

## Overview

This skill validates JSON content locally without any API calls. It parses the JSON and returns whether it's valid, any error messages, and statistics about the structure.

## Usage

### CLI Mode

```bash
# Validate JSON string
echo '{"key": "value"}' | expanso-edge run pipeline-cli.yaml

# Validate JSON file
cat data.json | expanso-edge run pipeline-cli.yaml
```

### MCP Mode

```bash
# Start server
PORT=8080 expanso-edge run pipeline-mcp.yaml &

# Make request
curl -X POST http://localhost:8080/validate \
  -H "Content-Type: application/json" \
  -d '{"json": "{\"key\": \"value\", \"array\": [1, 2, 3]}"}'
```

## Output

### Valid JSON

```json
{
  "valid": true,
  "error": null,
  "parsed": {
    "key": "value",
    "array": [1, 2, 3]
  },
  "stats": {
    "type": "object",
    "length": 35
  },
  "metadata": {
    "skill": "json-validate",
    "mode": "cli",
    "trace_id": "abc123...",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Invalid JSON

```json
{
  "valid": false,
  "error": "Invalid JSON syntax",
  "parsed": null,
  "stats": null,
  "metadata": { ... }
}
```

## Use Cases

- Validating API responses
- Pre-commit hooks for JSON files
- CI/CD pipeline validation
- Data ingestion validation
