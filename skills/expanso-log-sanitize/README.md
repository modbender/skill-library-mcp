# log-sanitize

Sanitize log entries by removing sensitive data patterns like passwords, tokens, and API keys.

## Overview

This skill runs **entirely locally** without any API calls. It uses pattern matching to detect and redact common secret patterns in log files.

## Usage

### CLI Mode

```bash
# Sanitize a log line
echo 'user=admin password=secret123 token=abc456' | \
  expanso-edge run pipeline-cli.yaml

# Sanitize an entire log file
cat /var/log/app.log | expanso-edge run pipeline-cli.yaml
```

### MCP Mode

```bash
# Start server
PORT=8080 expanso-edge run pipeline-mcp.yaml &

# Make request
curl -X POST http://localhost:8080/sanitize \
  -H "Content-Type: application/json" \
  -d '{"log": "password=secret123 api_key=sk-123abc"}'
```

## Output

```json
{
  "sanitized": "user=admin password=***REDACTED*** token=***REDACTED***",
  "redactions": 27,
  "metadata": {
    "skill": "log-sanitize",
    "mode": "cli",
    "trace_id": "abc123...",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## Patterns Detected

| Pattern | Example | Replacement |
|---------|---------|-------------|
| Passwords | `password=secret` | `password=***REDACTED***` |
| API Keys | `api_key=sk-123` | `api_key=***REDACTED***` |
| Tokens | `token=abc123` | `token=***REDACTED***` |
| Bearer Auth | `Bearer eyJ...` | `Bearer ***REDACTED***` |
| AWS Keys | `AKIAIOSFODNN7` | `***AWS_KEY_REDACTED***` |
| JWT Tokens | `eyJ...eyJ...` | `***JWT_REDACTED***` |
| Secrets | `secret=xyz` | `secret=***REDACTED***` |

## Use Cases

- Pre-processing logs before sending to log aggregators
- Sanitizing logs before sharing with support
- Compliance with security policies
- Preparing logs for public documentation
