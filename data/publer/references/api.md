# Publer API Reference

## Authentication
Every request requires:
```
Authorization: Bearer-API <API_KEY>
Publer-Workspace-Id: <WORKSPACE_ID>
Content-Type: application/json
```

## Endpoints

### List Accounts
`GET /api/v1/accounts`
Returns connected social accounts with IDs, types, network providers.

### Upload Media (Direct)
`POST /api/v1/media` (multipart/form-data)
- `file`: the file to upload
- `direct_upload`: boolean (optional, default false)
- `in_library`: boolean (optional, default false)

Response includes: `id`, `path`, `thumbnail`, `width`, `height`, `type`, `validity`

### Upload Media (from URL)
`POST /api/v1/media/from-url` (JSON)
```json
{
  "media": [{"url": "...", "name": "..."}],
  "type": "single"
}
```
Returns `job_id` — poll `/api/v1/job_status/{job_id}` until complete.

### Schedule Post
`POST /api/v1/posts/schedule`

### Publish Immediately
`POST /api/v1/posts/schedule/publish`

### Poll Job Status
`GET /api/v1/job_status/{job_id}`

## TikTok Carousel (Multi-Photo) Payload
```json
{
  "bulk": {
    "state": "scheduled",
    "posts": [{
      "accounts": [{"id": "<tiktok_account_id>", "scheduled_at": "ISO8601"}],
      "networks": {
        "tiktok": {
          "type": "photo",
          "title": "max 90 chars",
          "text": "description max 4000 chars",
          "media": [
            {"id": "media_id_1", "caption": "optional"},
            {"id": "media_id_2"}
          ],
          "details": {
            "privacy": "PUBLIC_TO_EVERYONE",
            "comment": true,
            "auto_add_music": true,
            "promotional": false,
            "paid": false
          }
        }
      }
    }]
  }
}
```
For immediate publish: use `/posts/schedule/publish` and omit `scheduled_at`.

## TikTok Video Payload
Same structure but `type: "video"`, single media item, and video-specific details (duet, stitch).

## Notes
- TikTok: one account per post, no duplicate content
- Carousel: up to 35 photos
- Video post URL not available immediately — poll later
- `state` must be `"scheduled"` even for immediate publishing
