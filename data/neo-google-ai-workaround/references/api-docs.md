# Google AI API Reference & Limitations

## API Endpoints

### Gemini Pro
- **Endpoint**: `https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent`
- **Auth**: API key or OAuth2 Bearer token
- **Rate Limits**: 60 RPM (requests per minute) for free tier, 1000 RPM for Pro subscribers

### Gemini Ultra
- **Endpoint**: `https://generativelanguage.googleapis.com/v1/models/gemini-ultra:generateContent`
- **Auth**: OAuth2 Bearer token (Pro/Ultra subscription required)
- **Rate Limits**: 60 RPM standard, configurable with enterprise plans

## Common Response Patterns

### Success (200)
```json
{
  "candidates": [{ "content": { "parts": [{ "text": "..." }] } }]
}
```

### Rate Limited (429)
```json
{
  "error": {
    "code": 429,
    "message": "Resource has been exhausted (e.g. check quota).",
    "status": "RESOURCE_EXHAUSTED"
  }
}
```
Headers: `x-ratelimit-remaining: 0`, `retry-after: <seconds>`

### Access Denied (403)
```json
{
  "error": {
    "code": 403,
    "message": "The caller does not have permission",
    "status": "PERMISSION_DENIED"
  }
}
```

### Token Expired (401)
```json
{
  "error": {
    "code": 401,
    "message": "Request had invalid authentication credentials.",
    "status": "UNAUTHENTICATED"
  }
}
```

### Service Unavailable (503)
```json
{
  "error": {
    "code": 503,
    "message": "The service is currently unavailable.",
    "status": "UNAVAILABLE"
  }
}
```

## Known Restrictions for Automated Clients

1. **User-Agent Filtering**: Automated requests without standard browser User-Agent headers may be flagged.
2. **IP Reputation**: Datacenter IPs are more likely to be restricted than residential IPs.
3. **Request Patterns**: Uniform request intervals (exact timing) may trigger bot detection.
4. **Token Lifecycle**: OAuth tokens expire after 1 hour; refresh tokens are required for long-running sessions.
5. **Concurrent Sessions**: Multiple sessions from the same account may trigger security reviews.

## Rate Limiting Details

| Tier | RPM | TPM (tokens) | Daily Limit |
|------|-----|---------------|-------------|
| Free | 60 | 60,000 | 1,500 |
| Pro | 1,000 | 2,000,000 | Unlimited |
| Ultra | 1,000 | 4,000,000 | Unlimited |

RPM = Requests Per Minute, TPM = Tokens Per Minute
