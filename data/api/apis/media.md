# Index

| API | Line |
|-----|------|
| Cloudinary | 2 |
| Mux | 66 |
| Bunny.net | 145 |
| UploadThing | 287 |
| Uploadcare | 353 |
| Transloadit | 431 |
| Vimeo | 500 |
| YouTube Data API | 581 |
| Spotify | 654 |
| Unsplash | 742 |
| Pexels | 813 |
| GIPHY | 882 |
| Tenor | 950 |

---

# Cloudinary

Image and video upload, transformation, optimization, and delivery via URL-based API.

## Base URL
`https://api.cloudinary.com/v1_1/{cloud_name}`

## Authentication
HTTP Basic Auth with API Key and Secret.

```bash
curl "https://api.cloudinary.com/v1_1/demo/resources/image" \
  -u "API_KEY:API_SECRET"
```

## Core Endpoints

### Upload an Image
```bash
curl -X POST "https://api.cloudinary.com/v1_1/{cloud_name}/image/upload" \
  -u "API_KEY:API_SECRET" \
  -F "file=@/path/to/image.jpg" \
  -F "upload_preset=preset_name"
```

### List Resources
```bash
curl "https://api.cloudinary.com/v1_1/{cloud_name}/resources/image" \
  -u "API_KEY:API_SECRET"
```

### Get Resource Details
```bash
curl "https://api.cloudinary.com/v1_1/{cloud_name}/resources/image/upload/{public_id}" \
  -u "API_KEY:API_SECRET"
```

### Delete Resource
```bash
curl -X DELETE "https://api.cloudinary.com/v1_1/{cloud_name}/resources/image/upload" \
  -u "API_KEY:API_SECRET" \
  -d "public_ids[]=image1&public_ids[]=image2"
```

### Transform via URL (no API call needed)
```
https://res.cloudinary.com/{cloud_name}/image/upload/w_400,h_300,c_fill/sample.jpg
```

## Rate Limits
- Admin API: 500 requests/hour (varies by plan)
- Upload API: No strict limit, but concurrent uploads limited by plan

## Gotchas
- Transformations are URL-based, not REST endpoints — append params to delivery URL
- `upload_preset` required for unsigned uploads from frontend
- Resource type matters: use `/image/`, `/video/`, or `/raw/` in paths
- Public IDs with special characters must be URL-encoded
- Admin API and Upload API use different base URLs

## Links
- [Docs](https://cloudinary.com/documentation)
- [Admin API](https://cloudinary.com/documentation/admin_api)
- [Upload API](https://cloudinary.com/documentation/image_upload_api_reference)
# Mux

Video streaming infrastructure API for upload, encoding, and playback.

## Base URL
`https://api.mux.com`

## Authentication
HTTP Basic Auth with Access Token ID and Secret.

```bash
curl "https://api.mux.com/video/v1/assets" \
  -u "MUX_TOKEN_ID:MUX_TOKEN_SECRET"
```

## Core Endpoints

### Create Asset (from URL)
```bash
curl -X POST "https://api.mux.com/video/v1/assets" \
  -u "MUX_TOKEN_ID:MUX_TOKEN_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "https://example.com/video.mp4",
    "playback_policy": ["public"]
  }'
```

### Create Direct Upload URL
```bash
curl -X POST "https://api.mux.com/video/v1/uploads" \
  -u "MUX_TOKEN_ID:MUX_TOKEN_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "new_asset_settings": { "playback_policy": ["public"] },
    "cors_origin": "https://yoursite.com"
  }'
```

### List Assets
```bash
curl "https://api.mux.com/video/v1/assets" \
  -u "MUX_TOKEN_ID:MUX_TOKEN_SECRET"
```

### Get Asset
```bash
curl "https://api.mux.com/video/v1/assets/{ASSET_ID}" \
  -u "MUX_TOKEN_ID:MUX_TOKEN_SECRET"
```

### Delete Asset
```bash
curl -X DELETE "https://api.mux.com/video/v1/assets/{ASSET_ID}" \
  -u "MUX_TOKEN_ID:MUX_TOKEN_SECRET"
```

### Create Live Stream
```bash
curl -X POST "https://api.mux.com/video/v1/live-streams" \
  -u "MUX_TOKEN_ID:MUX_TOKEN_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"playback_policy": ["public"], "new_asset_settings": {"playback_policy": ["public"]}}'
```

## Rate Limits
- No published hard limits, but throttling may occur at high volume
- Contact Mux for enterprise rate limits

## Gotchas
- Playback requires a Playback ID, not the Asset ID — get it from `playback_ids[0].id`
- Playback URL format: `https://stream.mux.com/{PLAYBACK_ID}.m3u8`
- Direct uploads return a URL to PUT your file to, not POST
- Assets take time to process — poll status until `status: "ready"`
- Signed URLs needed for `signed` playback policy (requires signing keys)

## Links
- [Docs](https://docs.mux.com)
- [API Reference](https://docs.mux.com/api-reference)
# Bunny.net

CDN, edge storage, and video streaming platform API.

## Base URL
`https://api.bunny.net`

## Authentication
API Key via `AccessKey` header.

```bash
curl "https://api.bunny.net/pullzone" \
  -H "AccessKey: YOUR_API_KEY"
```

## Core Endpoints

### List Pull Zones
```bash
curl "https://api.bunny.net/pullzone" \
  -H "AccessKey: YOUR_API_KEY"
```

### Create Pull Zone
```bash
curl -X POST "https://api.bunny.net/pullzone" \
  -H "AccessKey: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "Name": "my-zone",
    "OriginUrl": "https://origin.example.com"
  }'
```

### Purge Cache
```bash
curl -X POST "https://api.bunny.net/pullzone/{ID}/purgeCache" \
  -H "AccessKey: YOUR_API_KEY"
```

### Storage Zone - Upload File
```bash
curl -X PUT "https://{region}.storage.bunnycdn.com/{storage_zone}/{path}/file.jpg" \
  -H "AccessKey: STORAGE_ZONE_PASSWORD" \
  --data-binary @file.jpg
```

### Storage Zone - List Files
```bash
curl "https://{region}.storage.bunnycdn.com/{storage_zone}/{path}/" \
  -H "AccessKey: STORAGE_ZONE_PASSWORD"
```

### Stream - Create Video Library
```bash
curl -X POST "https://api.bunny.net/videolibrary" \
  -H "AccessKey: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"Name": "my-videos"}'
```

## Rate Limits
- No published limits for most endpoints
- Storage API: Depends on plan

## Gotchas
- Storage API uses different base URL: `{region}.storage.bunnycdn.com`
- Storage zones have separate passwords from account API key
- Pull zone hostnames: `{zone-name}.b-cdn.net`
- Stream API requires separate video library API key
- Region codes: `de`, `ny`, `la`, `sg`, `syd` for storage

## Links
- [Docs](https://docs.bunny.net)
- [API Reference](https://docs.bunny.net/reference/bunnynet-api-overview)
# imgix

Real-time image processing and CDN via URL parameters.

## Base URL
`https://{source}.imgix.net/{path}?{params}`

## Authentication
For Management API: API Key via Bearer token.
For Rendering API: URL signing (optional) with secure token.

```bash
# Management API
curl "https://api.imgix.com/api/v1/sources" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Rendering (no auth for public sources)
https://your-source.imgix.net/image.jpg?w=400&h=300
```

## Core Endpoints

### Rendering API (URL-based transformations)
```bash
# Resize
https://your-source.imgix.net/photo.jpg?w=800&h=600&fit=crop

# Format conversion
https://your-source.imgix.net/photo.jpg?auto=format,compress

# Watermark
https://your-source.imgix.net/photo.jpg?mark=logo.png&mark-w=100

# Face detection crop
https://your-source.imgix.net/photo.jpg?w=200&h=200&fit=facearea&facepad=2
```

### Management API - List Sources
```bash
curl "https://api.imgix.com/api/v1/sources" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Management API - Purge Cache
```bash
curl -X POST "https://api.imgix.com/api/v1/purge" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"data": {"type": "purges", "attributes": {"url": "https://your-source.imgix.net/image.jpg"}}}'
```

## Rate Limits
- Management API: 30 requests/minute by default
- Rendering API: No rate limits (CDN-based)

## Gotchas
- imgix doesn't store images — it processes from your origin (S3, GCS, web folder)
- All transformations are URL params, not REST calls
- Use `auto=format` to serve WebP/AVIF automatically
- Base64 variants available for complex params (append `64` to param name)
- Max canvas size: 8192x8192 pixels
- Secure URLs require HMAC signing if enabled on source

## Links
- [Docs](https://docs.imgix.com)
- [Rendering API Reference](https://docs.imgix.com/apis/rendering)
- [URL Parameters](https://docs.imgix.com/apis/rendering)
# UploadThing

Simple file uploads for JavaScript/TypeScript apps with built-in security.

## Base URL
`https://api.uploadthing.com`

## Authentication
API Token via `x-uploadthing-api-key` header or `UPLOADTHING_TOKEN` env var.

```bash
curl "https://api.uploadthing.com/v6/listFiles" \
  -H "x-uploadthing-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Core Endpoints

### List Files
```bash
curl -X POST "https://api.uploadthing.com/v6/listFiles" \
  -H "x-uploadthing-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"limit": 10}'
```

### Delete Files
```bash
curl -X POST "https://api.uploadthing.com/v6/deleteFiles" \
  -H "x-uploadthing-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"fileKeys": ["file-key-1", "file-key-2"]}'
```

### Get File URLs
```bash
curl -X POST "https://api.uploadthing.com/v6/getFileUrls" \
  -H "x-uploadthing-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"fileKeys": ["file-key-1"]}'
```

### Rename File
```bash
curl -X POST "https://api.uploadthing.com/v6/renameFiles" \
  -H "x-uploadthing-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"updates": [{"fileKey": "file-key-1", "newName": "new-name.jpg"}]}'
```

## Rate Limits
- Free tier: Limited requests (check dashboard)
- Paid plans: Higher limits based on tier

## Gotchas
- Designed for JS/TS frameworks — REST API is secondary to SDK usage
- File routes defined in code, not via API
- Upload flow: SDK generates presigned URL → client uploads directly to storage
- `fileKey` is not the same as the file URL — use `getFileUrls` to convert
- Callbacks (`onUploadComplete`) run server-side after upload succeeds
- All REST endpoints use POST method

## Links
- [Docs](https://docs.uploadthing.com)
- [API Reference](https://docs.uploadthing.com/api-reference/server)
# Uploadcare

File upload, processing, and delivery platform with powerful transformations.

## Base URL
`https://api.uploadcare.com`

## Authentication
Two schemes:
- **Simple** (testing): `Uploadcare.Simple {public_key}:{secret_key}`
- **Secure** (production): `Uploadcare {public_key}:{signature}` with HMAC-SHA1

```bash
# Simple auth
curl "https://api.uploadcare.com/files/" \
  -H "Authorization: Uploadcare.Simple PUBLIC_KEY:SECRET_KEY" \
  -H "Accept: application/vnd.uploadcare-v0.7+json"

# Secure auth requires Date header and signature
curl "https://api.uploadcare.com/files/" \
  -H "Authorization: Uploadcare PUBLIC_KEY:SIGNATURE" \
  -H "Accept: application/vnd.uploadcare-v0.7+json" \
  -H "Date: Mon, 05 Nov 2024 13:14:41 GMT"
```

## Core Endpoints

### List Files
```bash
curl "https://api.uploadcare.com/files/" \
  -H "Authorization: Uploadcare.Simple PUBLIC_KEY:SECRET_KEY" \
  -H "Accept: application/vnd.uploadcare-v0.7+json"
```

### Get File Info
```bash
curl "https://api.uploadcare.com/files/{uuid}/" \
  -H "Authorization: Uploadcare.Simple PUBLIC_KEY:SECRET_KEY" \
  -H "Accept: application/vnd.uploadcare-v0.7+json"
```

### Delete File
```bash
curl -X DELETE "https://api.uploadcare.com/files/{uuid}/" \
  -H "Authorization: Uploadcare.Simple PUBLIC_KEY:SECRET_KEY" \
  -H "Accept: application/vnd.uploadcare-v0.7+json"
```

### Store File (make permanent)
```bash
curl -X PUT "https://api.uploadcare.com/files/{uuid}/storage/" \
  -H "Authorization: Uploadcare.Simple PUBLIC_KEY:SECRET_KEY" \
  -H "Accept: application/vnd.uploadcare-v0.7+json"
```

### Upload via Upload API
```bash
curl -X POST "https://upload.uploadcare.com/base/" \
  -F "UPLOADCARE_PUB_KEY=PUBLIC_KEY" \
  -F "file=@/path/to/file.jpg"
```

## Rate Limits
- Free: 3,000 requests/day
- Paid plans: Higher limits

## Gotchas
- All REST API URLs MUST end with trailing slash `/`
- Accept header with API version is required: `application/vnd.uploadcare-v0.7+json`
- Upload API (`upload.uploadcare.com`) is separate from REST API (`api.uploadcare.com`)
- Files are temporary by default — call store endpoint to make permanent
- Secure auth signature must use Date within 15 minutes of server time
- Transformations are URL-based: `https://ucarecdn.com/{uuid}/-/resize/400x300/`

## Links
- [Docs](https://uploadcare.com/docs/)
- [REST API Reference](https://uploadcare.com/api-refs/rest-api/v0.7.0/)
- [Upload API Reference](https://uploadcare.com/api-refs/upload-api/)
# Transloadit

File processing service for encoding, resizing, and converting media files.

## Base URL
`https://api2.transloadit.com`

## Authentication
Signature-based auth with Auth Key and Secret. Every request needs `signature` and `params`.

```bash
# Params must be JSON with auth_key and template_id/steps
# Signature = HMAC-SHA384 of params JSON

curl -X POST "https://api2.transloadit.com/assemblies" \
  -F "params={\"auth\":{\"key\":\"AUTH_KEY\",\"expires\":\"2024/12/31 23:59:59+00:00\"},\"template_id\":\"TEMPLATE_ID\"}" \
  -F "signature=HMAC_SIGNATURE" \
  -F "file=@/path/to/file.mp4"
```

## Core Endpoints

### Create Assembly (process files)
```bash
curl -X POST "https://api2.transloadit.com/assemblies" \
  -F "params={\"auth\":{\"key\":\"AUTH_KEY\",\"expires\":\"...\"},\"steps\":{\"resize\":{\":robot\":\"/image/resize\",\"width\":400}}}" \
  -F "signature=SIGNATURE" \
  -F "file=@image.jpg"
```

### Get Assembly Status
```bash
curl "https://api2.transloadit.com/assemblies/{ASSEMBLY_ID}?signature=SIGNATURE&params=PARAMS"
```

### Cancel Assembly
```bash
curl -X DELETE "https://api2.transloadit.com/assemblies/{ASSEMBLY_ID}" \
  -d "params=PARAMS&signature=SIGNATURE"
```

### List Templates
```bash
curl "https://api2.transloadit.com/templates?signature=SIGNATURE&params=PARAMS"
```

### Create Template
```bash
curl -X POST "https://api2.transloadit.com/templates" \
  -d "params={\"auth\":{\"key\":\"AUTH_KEY\"},\"name\":\"my-template\",\"template\":{...}}" \
  -d "signature=SIGNATURE"
```

## Rate Limits
- Depends on plan
- Assembly processing is queued, not rate-limited per se

## Gotchas
- Every request requires valid signature — use official SDKs to avoid signature bugs
- `params` must include `auth.expires` timestamp in the future
- Assemblies are async — poll status or use webhooks for completion
- Templates define reusable processing steps (robots)
- Robots are processing steps: `/image/resize`, `/video/encode`, `/file/filter`, etc.
- Results delivered to your S3, GCS, or fetched from assembly result URLs

## Links
- [Docs](https://transloadit.com/docs/)
- [API Reference](https://transloadit.com/docs/api/)
- [Robots](https://transloadit.com/docs/transcoding/)
# Vimeo

Video hosting and streaming platform API.

## Base URL
`https://api.vimeo.com`

## Authentication
OAuth 2.0 Bearer token.

```bash
curl "https://api.vimeo.com/me" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

## Core Endpoints

### Get Authenticated User
```bash
curl "https://api.vimeo.com/me" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

### List My Videos
```bash
curl "https://api.vimeo.com/me/videos" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

### Get Video
```bash
curl "https://api.vimeo.com/videos/{video_id}" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

### Upload Video (tus resumable)
```bash
# Step 1: Create video entry
curl -X POST "https://api.vimeo.com/me/videos" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"upload": {"approach": "tus", "size": 123456789}}'

# Step 2: Upload to returned upload.upload_link using tus protocol
```

### Update Video Metadata
```bash
curl -X PATCH "https://api.vimeo.com/videos/{video_id}" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "New Title", "description": "New description"}'
```

### Delete Video
```bash
curl -X DELETE "https://api.vimeo.com/videos/{video_id}" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

### Search Videos
```bash
curl "https://api.vimeo.com/videos?query=cats&per_page=10" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

## Rate Limits
- Varies by app type and plan
- Typical: 100-500 requests/minute
- Check `X-RateLimit-*` headers in responses

## Gotchas
- Upload uses tus protocol, not simple POST — use Vimeo SDK or tus client
- Video processing takes time after upload — poll `transcode.status`
- Access tokens have scopes — ensure correct scope for endpoint (e.g., `upload` for uploading)
- Embed privacy settings affect where videos can be played
- Pagination uses `page` and `per_page` params, max 100 per page

## Links
- [Docs](https://developer.vimeo.com)
- [API Reference](https://developer.vimeo.com/api/reference)
# YouTube Data API

## Base URL
```
https://www.googleapis.com/youtube/v3
```

## Authentication
```bash
curl "https://www.googleapis.com/youtube/v3/videos?id=VIDEO_ID&part=snippet" \
  -H "Authorization: Bearer $GOOGLE_ACCESS_TOKEN"

# Or with API key (limited)
curl "https://www.googleapis.com/youtube/v3/videos?id=VIDEO_ID&part=snippet&key=$YOUTUBE_API_KEY"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /videos | GET | Get videos |
| /search | GET | Search |
| /channels | GET | Get channels |
| /playlists | GET | Get playlists |
| /playlistItems | GET | Get playlist videos |

## Quick Examples

### Get Video Info
```bash
curl "https://www.googleapis.com/youtube/v3/videos?id=VIDEO_ID&part=snippet,statistics&key=$YOUTUBE_API_KEY"
```

### Search Videos
```bash
curl "https://www.googleapis.com/youtube/v3/search?q=cats&type=video&maxResults=10&key=$YOUTUBE_API_KEY"
```

### Get Channel
```bash
curl "https://www.googleapis.com/youtube/v3/channels?id=CHANNEL_ID&part=snippet,statistics&key=$YOUTUBE_API_KEY"
```

### Get Playlist Items
```bash
curl "https://www.googleapis.com/youtube/v3/playlistItems?playlistId=PLAYLIST_ID&part=snippet&maxResults=50&key=$YOUTUBE_API_KEY"
```

### Get My Channel (OAuth)
```bash
curl "https://www.googleapis.com/youtube/v3/channels?mine=true&part=snippet,statistics" \
  -H "Authorization: Bearer $GOOGLE_ACCESS_TOKEN"
```

## Part Parameter

| Part | Data |
|------|------|
| snippet | Title, description, thumbnails |
| statistics | View count, likes, comments |
| contentDetails | Duration, definition |
| status | Privacy, license |

## Common Traps

- `part` parameter required - specify what data you want
- API key for read-only, OAuth for write/private
- Video ID is 11 characters from URL
- Pagination: use `pageToken` from response
- Quota: 10,000 units/day (search costs 100 units!)

## Official Docs
https://developers.google.com/youtube/v3/docs
# Spotify

## Base URL
```
https://api.spotify.com/v1
```

## Authentication
```bash
# After OAuth flow
curl https://api.spotify.com/v1/me \
  -H "Authorization: Bearer $SPOTIFY_ACCESS_TOKEN"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /me | GET | Current user |
| /me/player | GET | Playback state |
| /me/player/play | PUT | Start playback |
| /search | GET | Search |
| /tracks/:id | GET | Get track |
| /playlists/:id | GET | Get playlist |

## Quick Examples

### Search
```bash
curl "https://api.spotify.com/v1/search?q=artist:coldplay&type=track&limit=10" \
  -H "Authorization: Bearer $SPOTIFY_ACCESS_TOKEN"
```

### Get Track
```bash
curl "https://api.spotify.com/v1/tracks/TRACK_ID" \
  -H "Authorization: Bearer $SPOTIFY_ACCESS_TOKEN"
```

### Get User Playlists
```bash
curl "https://api.spotify.com/v1/me/playlists?limit=20" \
  -H "Authorization: Bearer $SPOTIFY_ACCESS_TOKEN"
```

### Create Playlist
```bash
curl -X POST "https://api.spotify.com/v1/users/$USER_ID/playlists" \
  -H "Authorization: Bearer $SPOTIFY_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "New Playlist", "public": false}'
```

### Add Tracks to Playlist
```bash
curl -X POST "https://api.spotify.com/v1/playlists/$PLAYLIST_ID/tracks" \
  -H "Authorization: Bearer $SPOTIFY_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"uris": ["spotify:track:TRACK_ID1", "spotify:track:TRACK_ID2"]}'
```

### Get Currently Playing
```bash
curl "https://api.spotify.com/v1/me/player/currently-playing" \
  -H "Authorization: Bearer $SPOTIFY_ACCESS_TOKEN"
```

## Search Types

| Type | Description |
|------|-------------|
| track | Songs |
| album | Albums |
| artist | Artists |
| playlist | Playlists |
| show | Podcasts |
| episode | Podcast episodes |

## Common Traps

- OAuth required for all endpoints (no API key mode)
- URIs use format: `spotify:track:ID`
- Player endpoints require Premium account
- Access tokens expire in 1 hour, use refresh token
- Rate limit: varies, typically no issues

## Official Docs
https://developer.spotify.com/documentation/web-api
# Unsplash

Free high-resolution stock photos API.

## Base URL
`https://api.unsplash.com`

## Authentication
Access Key via `Authorization` header or `client_id` query param.

```bash
curl "https://api.unsplash.com/photos" \
  -H "Authorization: Client-ID YOUR_ACCESS_KEY"

# Or via query param
curl "https://api.unsplash.com/photos?client_id=YOUR_ACCESS_KEY"
```

## Core Endpoints

### Search Photos
```bash
curl "https://api.unsplash.com/search/photos?query=nature&per_page=10" \
  -H "Authorization: Client-ID YOUR_ACCESS_KEY"
```

### List Photos
```bash
curl "https://api.unsplash.com/photos?page=1&per_page=10" \
  -H "Authorization: Client-ID YOUR_ACCESS_KEY"
```

### Get Photo
```bash
curl "https://api.unsplash.com/photos/{photo_id}" \
  -H "Authorization: Client-ID YOUR_ACCESS_KEY"
```

### Random Photo
```bash
curl "https://api.unsplash.com/photos/random?query=mountains" \
  -H "Authorization: Client-ID YOUR_ACCESS_KEY"
```

### Download Photo (trigger download event)
```bash
curl "https://api.unsplash.com/photos/{photo_id}/download" \
  -H "Authorization: Client-ID YOUR_ACCESS_KEY"
```

### Get User's Photos
```bash
curl "https://api.unsplash.com/users/{username}/photos" \
  -H "Authorization: Client-ID YOUR_ACCESS_KEY"
```

## Rate Limits
- Demo: 50 requests/hour
- Production: 5,000 requests/hour (requires approval)

## Gotchas
- **Must hotlink images** — use the URLs directly, don't re-host
- **Attribution required** — credit photographer and Unsplash
- Must trigger download endpoint when user downloads (for photographer stats)
- Demo mode is heavily rate-limited — apply for production access
- Use `w` param on image URLs to resize: `photo_url?w=400`
- Response includes multiple image sizes in `urls` object: `raw`, `full`, `regular`, `small`, `thumb`

## Links
- [Docs](https://unsplash.com/documentation)
- [API Guidelines](https://help.unsplash.com/api-guidelines)
# Pexels

Free stock photos and videos API.

## Base URL
`https://api.pexels.com`

## Authentication
API Key via `Authorization` header.

```bash
curl "https://api.pexels.com/v1/search?query=nature" \
  -H "Authorization: YOUR_API_KEY"
```

## Core Endpoints

### Search Photos
```bash
curl "https://api.pexels.com/v1/search?query=ocean&per_page=15&page=1" \
  -H "Authorization: YOUR_API_KEY"
```

### Curated Photos
```bash
curl "https://api.pexels.com/v1/curated?per_page=15&page=1" \
  -H "Authorization: YOUR_API_KEY"
```

### Get Photo
```bash
curl "https://api.pexels.com/v1/photos/{photo_id}" \
  -H "Authorization: YOUR_API_KEY"
```

### Search Videos
```bash
curl "https://api.pexels.com/videos/search?query=sunset&per_page=10" \
  -H "Authorization: YOUR_API_KEY"
```

### Popular Videos
```bash
curl "https://api.pexels.com/videos/popular?per_page=10" \
  -H "Authorization: YOUR_API_KEY"
```

### Get Video
```bash
curl "https://api.pexels.com/videos/videos/{video_id}" \
  -H "Authorization: YOUR_API_KEY"
```

## Rate Limits
- 200 requests/hour
- 20,000 requests/month

## Gotchas
- **Attribution required** — credit Pexels and photographer (link back)
- Photos endpoint: `/v1/` prefix; Videos endpoint: `/videos/` prefix
- Response includes multiple sizes in `src` object: `original`, `large2x`, `large`, `medium`, `small`, `portrait`, `landscape`, `tiny`
- Videos have multiple `video_files` with different qualities
- `per_page` max is 80
- No user authentication needed — API key only
- Locale param available: `locale=en-US` for localized results

## Links
- [Docs](https://www.pexels.com/api/documentation/)
- [API Guidelines](https://www.pexels.com/api/documentation/#guidelines)
# GIPHY

GIF and sticker search API — the largest GIF library.

## Base URL
`https://api.giphy.com/v1`

## Authentication
API Key via `api_key` query parameter.

```bash
curl "https://api.giphy.com/v1/gifs/trending?api_key=YOUR_API_KEY"
```

## Core Endpoints

### Search GIFs
```bash
curl "https://api.giphy.com/v1/gifs/search?api_key=YOUR_API_KEY&q=funny+cat&limit=25&offset=0&rating=g"
```

### Trending GIFs
```bash
curl "https://api.giphy.com/v1/gifs/trending?api_key=YOUR_API_KEY&limit=25&rating=g"
```

### Get GIF by ID
```bash
curl "https://api.giphy.com/v1/gifs/{gif_id}?api_key=YOUR_API_KEY"
```

### Random GIF
```bash
curl "https://api.giphy.com/v1/gifs/random?api_key=YOUR_API_KEY&tag=cat&rating=g"
```

### Search Stickers
```bash
curl "https://api.giphy.com/v1/stickers/search?api_key=YOUR_API_KEY&q=thumbs+up&limit=25"
```

### Trending Stickers
```bash
curl "https://api.giphy.com/v1/stickers/trending?api_key=YOUR_API_KEY&limit=25"
```

### Autocomplete
```bash
curl "https://api.giphy.com/v1/gifs/search/tags?api_key=YOUR_API_KEY&q=fun"
```

## Rate Limits
- Beta keys: 100 requests/hour (apply for production)
- Production: Higher limits (varies)

## Gotchas
- **Must display "Powered By GIPHY"** attribution
- Beta keys are rate-limited — apply for production before launch
- Don't cache responses or media URLs — GIPHY tracks views
- Don't proxy requests — calls must come directly from client
- Use `rating` param: `g`, `pg`, `pg-13`, `r` for content filtering
- Response includes multiple renditions in `images` object — use `fixed_height` or `fixed_width` for previews
- MP4 format available in `images.{size}.mp4` for better performance
- Stickers have transparent backgrounds

## Links
- [Docs](https://developers.giphy.com/docs/api/)
- [API Explorer](https://developers.giphy.com/explorer/)
# Tenor

GIF search API by Google — powers GIF keyboards worldwide.

## Base URL
`https://tenor.googleapis.com/v2`

## Authentication
API Key via `key` query parameter (Google Cloud API key).

```bash
curl "https://tenor.googleapis.com/v2/search?q=excited&key=YOUR_API_KEY&client_key=my_app"
```

## Core Endpoints

### Search GIFs
```bash
curl "https://tenor.googleapis.com/v2/search?q=happy&key=YOUR_API_KEY&client_key=my_app&limit=20"
```

### Trending GIFs
```bash
curl "https://tenor.googleapis.com/v2/featured?key=YOUR_API_KEY&client_key=my_app&limit=20"
```

### Get GIFs by IDs
```bash
curl "https://tenor.googleapis.com/v2/posts?ids=gif_id1,gif_id2&key=YOUR_API_KEY&client_key=my_app"
```

### Trending Search Terms
```bash
curl "https://tenor.googleapis.com/v2/trending_terms?key=YOUR_API_KEY&client_key=my_app&limit=10"
```

### Autocomplete
```bash
curl "https://tenor.googleapis.com/v2/autocomplete?q=exci&key=YOUR_API_KEY&client_key=my_app&limit=5"
```

### Search Suggestions
```bash
curl "https://tenor.googleapis.com/v2/search_suggestions?q=laugh&key=YOUR_API_KEY&client_key=my_app&limit=5"
```

### Categories
```bash
curl "https://tenor.googleapis.com/v2/categories?key=YOUR_API_KEY&client_key=my_app"
```

### Register Share (analytics)
```bash
curl "https://tenor.googleapis.com/v2/registershare?id=GIF_ID&key=YOUR_API_KEY&client_key=my_app&q=original_search"
```

## Rate Limits
- Free tier with Google Cloud quota
- Check Google Cloud Console for current limits

## Gotchas
- **Attribution required** — display "Powered by Tenor" or "Search Tenor"
- `client_key` param recommended — identifies your integration for better results
- Call `registershare` when user shares a GIF — improves search results
- Supports 45+ languages via `locale` param
- Response includes multiple formats in `media_formats`: `gif`, `mp4`, `webp`, `tinygif`, `tinymp4`
- Use smaller formats (`tinygif`, `nanogif`) for previews
- `contentfilter` param: `off`, `low`, `medium`, `high` for safety filtering
- Tenor is part of Google — manage API key in Google Cloud Console

## Links
- [Docs](https://developers.google.com/tenor/guides/quickstart)
- [Endpoints Reference](https://developers.google.com/tenor/guides/endpoints)
