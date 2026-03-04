# PicSee Short Link API (Authenticated Mode)

## Base URL

```
https://api.pics.ee
```

## Authentication

**Method:** HTTP Bearer Authentication

Add the Authorization header to all requests:
```
Authorization: Bearer YOUR_API_TOKEN
```

**Example:**
```bash
curl -X GET https://api.pics.ee/v2/my/api/status \
  -H "Authorization: Bearer abc123...xyz"
```

## Rate Limits

- **API Status endpoint:** 1 call/sec

## Endpoints

### 1. Get API Plans and Usage

Check current API usage quota and plan status.

**Endpoint:** `GET /v2/my/api/status`

**Rate limit:** 1 call/sec

**Response** (200 OK):
```json
{
  "data": {
    "picseeId": 12345,
    "email": "user@example.com",
    "planName": "advanced",
    "quota": 10000,
    "usage": 150,
    "endTime": "2026-12-31T23:59:59Z"
  }
}
```

**Response Fields:**
- `planName`: Current plan - `"free"`, `"basic"`, or `"advanced"`
- `quota`: Total API calls allowed
- `usage`: Current usage count
- `endTime`: Plan expiration date

---

### 2. Create Short Link (Authenticated)

Create a single short URL with enhanced features.

**Endpoint:** `POST /v1/links`

**Request Body** (JSON):

| Field | Type | Plan | Description |
|-------|------|------|-------------|
| `url` | string (URI) | All | ✅ **Required** - Destination URL |
| `encodeId` | string | All | Custom slug (3-90 chars, alphanumeric/dash/underscore/Chinese) |
| `domain` | string | All | Custom domain (e.g. `pse.is`) |
| `externalId` | string | All | Custom ID for grouping |
| `title` | string | Advanced | Custom preview title |
| `description` | string | Advanced | Custom preview description |
| `imageUrl` | string | Advanced | Custom preview thumbnail URL |
| `tags` | array[string] | Advanced | Tags for organization |
| `targets` | array[object] | Advanced | Device/OS specific redirection (e.g. ios, android) |
| `fbPixel` | string | Advanced | Meta Pixel ID |
| `gTag` | string | Advanced | Google Tag Manager ID |
| `utm` | object | Advanced | UTM parameters (source, medium, campaign, term, content) |
| `pathFormat` | object | Advanced | Parameter routing key |

**Response** (200 OK):
```json
{
  "data": {
    "picseeUrl": "https://pse.is/xxxxx"
  }
}
```

**Example - Basic:**
```bash
curl -X POST https://api.pics.ee/v1/links \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "domain": "pse.is",
    "externalId": "openclaw"
  }'
```

**Example - Advanced (with custom preview):**
```bash
curl -X POST https://api.pics.ee/v1/links \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "domain": "pse.is",
    "externalId": "openclaw",
    "title": "Custom Title",
    "description": "Custom Description",
    "imageUrl": "https://example.com/image.jpg",
    "tags": ["marketing", "campaign"],
    "utm": {
      "source": "openclaw",
      "medium": "api",
      "campaign": "test"
    }
  }'
```

---

### 3. Get Short Link Analytics

View click statistics for a specific short link.

**Endpoint:** `GET /v1/links/{encodeId}/overview`

**Path Parameters:**
- `encodeId` (required): The slug of the short link

**Query Parameters:**
- `format` (optional): `"json"` or `"csv"` (default: `"json"`)
- `dailyClicks` (optional): Return daily click analytics for past 60 days (default: `false`)

**Response** (200 OK):
```json
{
  "data": {
    "id": "abc123",
    "encodeId": "my-link",
    "url": "https://example.com/destination",
    "totalClicks": 1234,
    "uniqueClicks": 567,
    "created": "2026-01-01T12:00:00Z",
    "dailyClicks": [
      {
        "date": "2026-02-24",
        "uniqueClicks": 10,
        "totalClicks": 15
      }
    ]
  }
}
```

**Example:**
```bash
curl -X GET "https://api.pics.ee/v1/links/my-link/overview?dailyClicks=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 4. List Short Links

Retrieve a list of short links with filtering and search.

**Endpoint:** `POST /v2/links/overview`

**Query Parameters:**
- `limit` (optional): Items per page (default: 20, max: 50)
- `startTime` (optional): Query backward from this time (format: `2006-01-02T15:04:05`)
- `isAPI` (optional): `true` for API links only, `false` for non-API links only (default: `true`)
- `isStar` (optional): `true` for Starred links only, `false` for non-Starred links only (default: `false`)

**Request Body** (JSON, optional):

| Field | Plan | Description |
|-------|------|-------------|
| `encodeId` | All | Filter by slug |
| `url` | All | Filter by destination URL |
| `authorId` | All | Filter by author |
| `tags` | Advanced | Filter by tags |
| `keyword` | Advanced | Search in title/description |
| `fbPixel` | Advanced | Filter by Meta Pixel ID |
| `gTag` | Advanced | Filter by Google Tag Manager ID |
| `utm` | Advanced | Filter by UTM parameters |

**Response** (200 OK):
```json
{
  "data": [
    {
      "mapId": "abc123",
      "domain": "pse.is",
      "encodeId": "my-link",
      "url": "https://example.com/destination",
      "title": "My Link",
      "totalClicks": 100,
      "uniqueClicks": 50,
      "createTime": "2026-01-01T12:00:00Z",
      "tags": [
        {"value": "marketing"}
      ]
    }
  ]
}
```

**Example - Basic (list all API links):**
```bash
curl -X POST "https://api.pics.ee/v2/links/overview?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

**Example - Search by keyword (Advanced Plan):**
```bash
curl -X POST https://api.pics.ee/v2/links/overview \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "marketing"
  }'
```

---

### 5. Edit Short Link ⚠️ ADVANCED PLAN ONLY

Update details of an existing short link.

**Endpoint:** `PUT /v2/links/{originalEncodeId}`

**Path Parameters:**
- `originalEncodeId` (required): The current slug of the short link

**Request Body** (JSON):

All fields are optional. Include only the fields you want to update.

| Field | Description |
|-------|-------------|
| `encodeId` | New custom slug |
| `url` | New destination URL |
| `domain` | New domain |
| `title` | New preview title |
| `description` | New preview description |
| `imageUrl` | New preview thumbnail URL |
| `tags` | New tags array |
| `targets` | New device/OS redirection rules |
| `fbPixel` | New Meta Pixel ID |
| `gTag` | New Google Tag Manager ID |
| `utm` | New UTM parameters |
| `expireTime` | Expiration time (ISO 8601 format) |

**Response** (200 OK):
```json
{
  "data": {
    "result": "success"
  }
}
```

**Example - Change destination URL:**
```bash
curl -X PUT https://api.pics.ee/v2/links/old-slug \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://new-destination.com"
  }'
```

**Example - Change slug:**
```bash
curl -X PUT https://api.pics.ee/v2/links/old-slug \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "encodeId": "new-slug"
  }'
```

**⚠️ Important:** Do not use this endpoint if the user is on Free or Basic plan. Check plan status with `/v2/my/api/status` first.

---

### 6. Delete or Recover Short Link

Delete or recover a short link.

**Endpoint:** `POST /v2/links/{encodeId}/delete`

**Path Parameters:**
- `encodeId` (required): The slug of the short link

**Request Body** (JSON):
```json
{
  "value": "delete"  // or "recover"
}
```

**Response** (200 OK):
```json
{
  "data": {
    "result": "success"
  }
}
```

**Example - Delete:**
```bash
curl -X POST https://api.pics.ee/v2/links/my-link/delete \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"value": "delete"}'
```

**Example - Recover:**
```bash
curl -X POST https://api.pics.ee/v2/links/my-link/delete \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"value": "recover"}'
```

---

## Plan Comparison

| Feature | Free | Basic | Advanced |
|---------|------|-------|----------|
| Create short links | ✅ | ✅ | ✅ |
| Custom slug | ✅ | ✅ | ✅ |
| View analytics | ✅ | ✅ | ✅ |
| List links | ✅ | ✅ | ✅ |
| Delete/recover | ✅ | ✅ | ✅ |
| Custom preview (title/desc/image) | ❌ | ❌ | ✅ |
| Tags | ❌ | ❌ | ✅ |
| Device/OS targeting | ❌ | ❌ | ✅ |
| Tracking pixels (FB/GA) | ❌ | ❌ | ✅ |
| UTM parameters | ❌ | ❌ | ✅ |
| Edit short links | ❌ | ❌ | ✅ |
| Search by keyword | ❌ | ❌ | ✅ |

## Notes

- Always check plan status before using Advanced-only features
- API token format: alphanumeric string (e.g., `abc123...xyz`)
- Use `Bearer` prefix in Authorization header
- Default domain is `pse.is`
- Custom slugs must be 3-90 characters (alphanumeric, dash, underscore, or Chinese)
