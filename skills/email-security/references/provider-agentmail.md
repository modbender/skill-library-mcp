# AgentMail Provider Guide

AgentMail-specific security considerations for AI agents.

## API Authentication

AgentMail uses API keys (simpler than OAuth):

```python
from agentmail import AgentMail

client = AgentMail(api_key="am_...")
```

### API Key Security
- Use environment variables, never hardcode
- Rotate keys regularly
- Use scoped keys when available (read-only vs. full access)

## Built-in Security Features

AgentMail provides AI-native security:

### Agent Guardrails
Configure content restrictions at the inbox level:

```python
inbox = client.inboxes.create(
    guardrails={
        "block_suspicious_senders": True,
        "max_attachment_size_mb": 25,
        "allowed_domains": ["company.com", "partner.org"]
    }
)
```

### Automatic Labeling
AgentMail can auto-categorize emails:

```python
# Labels applied automatically based on prompts
inbox.configure_labeling(
    labels=["command", "notification", "spam"],
    prompt="Categorize this email..."
)
```

Use labels to pre-filter before processing.

## Webhook Security

AgentMail sends webhooks for new emails:

### Verify Webhook Signatures
```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

### Webhook Best Practices
- Always verify signatures before processing
- Use HTTPS endpoints only
- Implement idempotency (webhooks may retry)

## WebSocket Security

For real-time email streaming:

```python
async with client.websockets.connect() as ws:
    async for message in ws:
        # Validate before processing
        if verify_sender(message):
            process(message)
```

### Connection Security
- Use secure WebSocket (wss://)
- Re-authenticate if connection drops
- Monitor for unexpected disconnections

## Semantic Search Considerations

AgentMail's semantic search can find emails by meaning:

```python
results = client.inboxes.search(
    inbox_id="...",
    query="emails about account password"
)
```

### Search Safety
- Never expose search to untrusted input directly
- Sanitize search queries to prevent prompt injection
- Log search queries for audit

## AgentMail-Specific Headers

AgentMail adds custom headers:

| Header | Description |
|--------|-------------|
| `X-AgentMail-Inbox-ID` | Source inbox identifier |
| `X-AgentMail-Thread-ID` | Thread identifier |
| `X-AgentMail-Spam-Score` | Spam probability (0-100) |
| `X-AgentMail-Verified` | Sender verification status |

Use `X-AgentMail-Verified` and `X-AgentMail-Spam-Score` for quick filtering.

## Rate Limits

AgentMail has generous limits for agents:

| Operation | Limit |
|-----------|-------|
| Send | 1000/hour per inbox |
| Receive | Unlimited |
| API calls | 100/second |

No per-inbox subscription fees—usage-based pricing only.
