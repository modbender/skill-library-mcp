# Gmail Provider Guide

Gmail-specific security considerations for AI agents.

## Authentication Headers

Gmail includes authentication results in headers:

```
Authentication-Results: mx.google.com;
       dkim=pass header.i=@example.com header.s=selector1;
       spf=pass (google.com: domain of sender@example.com designates 1.2.3.4 as permitted sender)
       dmarc=pass (p=REJECT sp=REJECT dis=NONE) header.from=example.com
```

Parse the `Authentication-Results` header to verify sender authenticity.

## Gmail API Specifics

### Rate Limits
- 250 quota units per user per second
- 1 billion quota units per day
- Batch requests: 100 requests per batch

### Message Format
Gmail uses modified RFC 5322 with base64url encoding for the `raw` field:

```python
import base64

# Decode Gmail message
raw = message['raw']
decoded = base64.urlsafe_b64decode(raw.encode('ASCII'))
```

### Header Access
Key headers for security validation:

```python
headers = message['payload']['headers']
for header in headers:
    if header['name'] == 'From':
        sender = header['value']
    if header['name'] == 'Authentication-Results':
        auth_results = header['value']
```

## OAuth Security

### Required Scopes (Minimal)
- `gmail.readonly` - Read-only access (preferred)
- `gmail.modify` - If writing operations needed

### Token Security
- Store refresh tokens encrypted
- Rotate tokens periodically
- Monitor for token theft via unusual access patterns

## Gmail-Specific Threats

### Confidential Mode Bypass
Gmail's confidential mode emails may have:
- Expiration dates
- Revoked access

Don't assume email content persists—re-fetch if needed.

### Google Workspace Admin Override
In enterprise environments, admins can:
- Access any user's email
- Delegate access silently

Verify organizational policies if handling sensitive data.

## Recommended Gmail Security Settings

If agent manages Gmail settings, recommend:
- Enable 2FA
- Disable less secure app access
- Review third-party app permissions
- Enable suspicious login alerts
