# Evolink File Hosting API — Audio Upload for Music Workflows

When MCP tools are not available, use Evolink's file hosting service to upload audio files and get publicly accessible URLs for music continuation or remix workflows.

**Base URL:** `https://files-api.evolink.ai`
**Auth:** `Authorization: Bearer $EVOLINK_API_KEY`

## Upload a Local File

```bash
curl -X POST https://files-api.evolink.ai/api/v1/files/upload/stream \
  -H "Authorization: Bearer $EVOLINK_API_KEY" \
  -F "file=@/path/to/audio.mp3"
```

## Upload from URL

```bash
curl -X POST https://files-api.evolink.ai/api/v1/files/upload/url \
  -H "Authorization: Bearer $EVOLINK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"file_url": "https://example.com/audio.mp3"}'
```

## Response

```json
{
  "data": {
    "file_id": "file_abc123",
    "file_url": "https://...",
    "download_url": "https://...",
    "file_size": 245120,
    "mime_type": "audio/mpeg",
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

**Supported:** Audio (MP3, WAV, FLAC, AAC, OGG, M4A, etc.). Max **100MB**. Quota: 100 files (default) / 500 (VIP).
