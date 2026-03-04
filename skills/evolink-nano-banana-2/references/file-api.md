# Evolink File Hosting API — Image Upload

When MCP tools are not available, use Evolink's file hosting service to upload images and get publicly accessible URLs.

**Base URL:** `https://files-api.evolink.ai`
**Auth:** `Authorization: Bearer $EVOLINK_API_KEY`

## Upload a Local File

```bash
curl -X POST https://files-api.evolink.ai/api/v1/files/upload/stream \
  -H "Authorization: Bearer $EVOLINK_API_KEY" \
  -F "file=@/path/to/image.jpg"
```

## Upload from URL

```bash
curl -X POST https://files-api.evolink.ai/api/v1/files/upload/url \
  -H "Authorization: Bearer $EVOLINK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"file_url": "https://example.com/image.jpg"}'
```

## Response

```json
{
  "data": {
    "file_id": "file_abc123",
    "file_url": "https://...",
    "download_url": "https://...",
    "file_size": 245120,
    "mime_type": "image/jpeg",
    "expires_at": "2025-03-01T10:30:00Z"
  }
}
```

Use `file_url` from the response as a publicly accessible link. Files expire after **72 hours**.

## List Files & Check Quota

```bash
curl https://files-api.evolink.ai/api/v1/files/list?page=1&pageSize=20 \
  -H "Authorization: Bearer $EVOLINK_API_KEY"

curl https://files-api.evolink.ai/api/v1/files/quota \
  -H "Authorization: Bearer $EVOLINK_API_KEY"
```

## Delete a File

```bash
curl -X DELETE https://files-api.evolink.ai/api/v1/files/{file_id} \
  -H "Authorization: Bearer $EVOLINK_API_KEY"
```

**Supported:** Images (JPEG/PNG/GIF/WebP). Max **100MB**. Quota: 100 files (default) / 500 (VIP).
