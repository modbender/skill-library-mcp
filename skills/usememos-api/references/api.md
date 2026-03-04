# UseMemos API Reference

Base URL: `https://your-memos-instance.com/api/v1`

Authentication: Bearer token in header
```
Authorization: Bearer <your-access-token>
```

## Endpoints

### Memos

**List Memos**
```
GET /api/v1/memos?pageSize={limit}
```
Query params:
- `page` (int): Page number, default 0
- `pageSize` (int): Items per page, default 10
- `filter` (string): Filter query

Response:
```json
{
  "memos": [...],
  "nextPageToken": "..."
}
```

**Get Memo**
```
GET /api/v1/memos/{id}
```
Note: Use the short ID, not the full name (e.g., `3UZ7uBbHsLEAwdYE5HKhjd`, not `memos/3UZ7uBbHsLEAwdYE5HKhjd`)

**Create Memo**
```
POST /api/v1/memos
```
Body:
```json
{
  "content": "string",
  "visibility": "PRIVATE | PROTECTED | PUBLIC"
}
```

**Update Memo**
```
PATCH /api/v1/memos/{id}
```
Body:
```json
{
  "content": "string",
  "visibility": "PRIVATE | PROTECTED | PUBLIC",
  "attachments": [
    {
      "name": "attachments/{attachment_id}",
      "filename": "string",
      "type": "image/jpeg"
    }
  ]
}
```

**Delete Memo**
```
DELETE /api/v1/memos/{id}
```

### Attachments

**Create Attachment**
```
POST /api/v1/attachments
```
Body:
```json
{
  "filename": "photo.jpg",
  "content": "base64-encoded-content",
  "type": "image/jpeg"
}
```

Response:
```json
{
  "name": "attachments/xyz",
  "createTime": "2026-01-01T00:00:00Z",
  "filename": "photo.jpg",
  "content": "",
  "externalLink": "",
  "type": "image/jpeg",
  "size": "12345"
}
```

**Get Attachment**
```
GET /api/v1/attachments/{id}
```

**Delete Attachment**
```
DELETE /api/v1/attachments/{id}
```

### Tags

**List Tags**
```
GET /api/v1/tags
```

### Users

**Get Current User**
```
GET /api/v1/users/me
```

## Response Format

Standard memo object:
```json
{
  "name": "memos/abc123",
  "state": "NORMAL",
  "creator": "users/1",
  "createTime": "2026-01-01T00:00:00Z",
  "updateTime": "2026-01-01T00:00:00Z",
  "displayTime": "2026-01-01T00:00:00Z",
  "content": "Memo content here",
  "visibility": "PRIVATE",
  "pinned": false,
  "attachments": [],
  "relations": [],
  "tags": [],
  "property": {...}
}
```

Standard attachment object:
```json
{
  "name": "attachments/xyz",
  "createTime": "2026-01-01T00:00:00Z",
  "filename": "photo.jpg",
  "content": "",
  "externalLink": "",
  "type": "image/jpeg",
  "size": "0",
  "memo": "memos/abc"
}
```

## Important Notes

- Memo IDs: Use the short ID in API calls (e.g., `3UZ7uBbHsLEAwdYE5HKhjd`), not the full name (`memos/3UZ7uBbHsLEAwdYE5HKhjd`)
- Attachment content: Send file data as base64 in the `content` field (not `blob`)
