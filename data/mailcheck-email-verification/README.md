# MailCheck Email Verification API

## Quick Start

The MailCheck API provides email verification, bulk processing, and email authenticity analysis capabilities.

## Authentication

All API requests require a Bearer token:
```
Authorization: Bearer sk_live_your_api_key
```

## Core Endpoints

1. **POST /v1/verify** - Single email verification
2. **POST /v1/verify/bulk** - Bulk verification (up to 100 emails)
3. **POST /v1/verify/auth** - Email authenticity analysis
4. **GET /v1/account** - Account details and usage
5. **POST /v1/signup** - Create new account

## Score System

- **Syntax (15 pts)**: Valid email format
- **Disposable (20 pts)**: Not from disposable provider
- **MX Records (30 pts)**: Valid mail server exists
- **SMTP (35 pts)**: Mailbox actually exists

**Scores ≥ 80** = Valid, **50-79** = Medium risk, **< 50** = Invalid

## Usage Examples

### Node.js
```javascript
const result = await fetch('https://api.mailcheck.dev/v1/verify', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${process.env.MAILCHECK_API_KEY}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ email: 'user@example.com' }),
});
const data = await result.json();
console.log(data.valid, data.score, data.reason);
```

### Python
```python
import requests

resp = requests.post(
    'https://api.mailcheck.dev/v1/verify',
    headers={'Authorization': f'Bearer {API_KEY}'},
    json={'email': 'user@example.com'}
)
data = resp.json()
print(data['valid'], data['score'])
```

## Best Practices

- Cache results (cached verifications don't count against quota)
- Use bulk endpoint for lists > 10 emails
- Check risk_level for quick triage
- Handle rate limits with exponential backoff
- Rotate API keys periodically

## Rate Limits

| Plan | Requests/min | Monthly | Features |
|------|-------------|---------|----------|
| Free | 10 | 100 | Basic verification |
| Starter | 60 | 5,000 | All features |
| Pro | 120 | 25,000 | Bulk + webhooks |
| Enterprise | Unlimited | Custom | Dedicated support |

## Support

- Docs: https://api.mailcheck.dev/docs
- Dashboard: https://api.mailcheck.dev/dashboard
- Email: support@mailcheck.dev
