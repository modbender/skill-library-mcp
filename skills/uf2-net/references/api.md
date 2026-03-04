# uf2.net API Reference

## Base URL
```
https://uf2.net/api/v1
```

## Authentication
Include API key in header:
```
X-API-Key: uf2_your_key_here
```

## Endpoints

### Register Account
```http
POST /accounts/register
Content-Type: application/json

{
  "username": "my-bot"  // optional
}
```

Response:
```json
{
  "account_id": "uuid",
  "api_key": "uf2_...",
  "username": "my-bot",
  "created_at": "2026-02-25T17:03:50.756687"
}
```

### Get Account Info
```http
GET /accounts/me
X-API-Key: uf2_...
```

Response:
```json
{
  "account_id": "uuid",
  "username": "my-bot",
  "created_at": "timestamp",
  "link_count": 5
}
```

### Create Link
```http
POST /links
X-API-Key: uf2_...
Content-Type: application/json

{
  "url": "https://example.com/path",  // required
  "slug": "my-slug",                  // optional (4-64 chars, [a-z0-9_-])
  "title": "Human label"              // optional
}
```

Response:
```json
{
  "code": "my-slug",
  "short_url": "https://uf2.net/my-slug",
  "original_url": "https://example.com/path",
  "title": "Human label",
  "created_at": "timestamp",
  "click_count": 0
}
```

**Notes:**
- Custom slugs return 409 if taken
- Auto-generated codes are 6 characters and always succeed
- Max URL length: 2048 characters
- Slugs are stored lowercase

### List Links
```http
GET /links?limit=50&offset=0
X-API-Key: uf2_...
```

Response:
```json
{
  "links": [
    {
      "code": "abc123",
      "short_url": "https://uf2.net/abc123",
      "original_url": "https://example.com",
      "title": "Example",
      "created_at": "timestamp",
      "click_count": 42
    }
  ],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

### Get Link Metadata
```http
GET /links/{code}
```

Public endpoint - no auth required.

Response:
```json
{
  "code": "abc123",
  "short_url": "https://uf2.net/abc123",
  "original_url": "https://example.com",
  "title": "Example",
  "created_at": "timestamp",
  "click_count": 42
}
```

### Delete Link
```http
DELETE /links/{code}
X-API-Key: uf2_...
```

Owner only. Returns 204 on success.

### Redirect
```http
GET /{code}
```

Public endpoint. Returns 302 redirect to original URL.

## Rate Limits
- Registration: 20 per IP per hour
- Other endpoints: Reasonable use expected

## Error Responses
```json
{
  "detail": "Error message"
}
```

Common status codes:
- 400: Bad request (invalid URL, slug format, etc.)
- 401: Unauthorized (missing or invalid API key)
- 404: Link not found
- 409: Conflict (slug already taken)
- 429: Rate limit exceeded
