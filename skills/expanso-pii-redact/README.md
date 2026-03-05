# pii-redact

Redact personally identifiable information (PII) from text, replacing it with configurable placeholders.

## Overview

This skill uses AI to detect and redact PII from text. Unlike `pii-detect` which only identifies PII, this skill **transforms** the text by replacing sensitive information with placeholders.

## Usage

### CLI Mode

```bash
# Set your API key (stays local!)
export OPENAI_API_KEY=sk-...

# Redact PII from text
echo "Contact John Smith at john.smith@company.com or 555-123-4567" | \
  expanso-edge run pipeline-cli.yaml

# Custom placeholder
PLACEHOLDER="***" echo "Contact John at john@example.com" | \
  expanso-edge run pipeline-cli.yaml
```

### MCP Mode

```bash
# Start server
PORT=8080 expanso-edge run pipeline-mcp.yaml &

# Make request
curl -X POST http://localhost:8080/redact \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Contact John Smith at john.smith@company.com",
    "placeholder": "[HIDDEN]"
  }'
```

## Output

```json
{
  "redacted_text": "Contact [REDACTED] at [REDACTED] or [REDACTED]",
  "redaction_count": 3,
  "redacted_types": ["name", "email", "phone"],
  "metadata": {
    "skill": "pii-redact",
    "mode": "cli",
    "model": "gpt-4o-mini",
    "placeholder": "[REDACTED]",
    "trace_id": "abc123...",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## PII Types Detected

- Names (first, last, full)
- Email addresses
- Phone numbers
- Social Security Numbers
- Street addresses
- Credit card numbers
- IP addresses
- Dates of birth
- Government IDs

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PLACEHOLDER` | `[REDACTED]` | Text to replace PII with |
| `OPENAI_API_KEY` | - | Required for OpenAI backend |

## Use Cases

- Log sanitization before storage
- Data anonymization for analytics
- Compliance with GDPR/CCPA
- Preparing data for public sharing
