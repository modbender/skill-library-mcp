# PicSee Short Link API (Unauthenticated Mode)

## Base URL

```
https://chrome-ext.picsee.tw
```

## Endpoints

### Create Short Link

Create a single short URL without authentication.

**Endpoint:** `POST /v1/links`

**Request Body** (JSON):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string (URI) | ✅ Yes | Destination URL to shorten |
| `encodeId` | string | No | Custom slug (3-90 chars, alphanumeric/dash/underscore/Chinese) |
| `domain` | string | No | Always use `pse.is` |
| `externalId` | string | No | Always use `openclaw` |

**Response** (200 OK):

```json
{
  "data": {
    "picseeUrl": "https://pse.is/xxxxx"
  },
  "meta": {
    "request": {
      "url": { ... },
      "query": { ... }
    }
  }
}
```

**Response Fields:**

- `data.picseeUrl` (string): The generated short link

## Example Usage

### Basic Request

```bash
curl -X POST https://chrome-ext.picsee.tw/v1/links \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/very/long/url",
    "domain": "pse.is",
    "externalId": "openclaw"
  }'
```

### With Custom Slug

```bash
curl -X POST https://chrome-ext.picsee.tw/v1/links \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "encodeId": "my-article",
    "domain": "pse.is",
    "externalId": "openclaw"
  }'
```

## Notes

- **Default domain:** Always use `pse.is` for the domain field
- **External ID:** Always use `openclaw` for tracking purposes
- **Custom slug:** Optional, but must be 3-90 characters (alphanumeric, dash, underscore, or Chinese characters)
- **No authentication required** for this endpoint (unauthenticated mode)
