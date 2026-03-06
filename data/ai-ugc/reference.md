# RawUGC API – Request/Response Reference

Condensed shapes for agent lookups. Base URL: `https://rawugc.com/api/v1`. Auth: `Authorization: Bearer <RAWUGC_API_KEY>`.

## POST /videos/generate

**Request (application/json)**

- `model` (required): `sora-2-text-to-video` | `sora-2-image-to-video` | `kling-2.6/motion-control` | `veo3` | `veo3_fast`
- `prompt` (optional, required for text-to-video/veo3): string, 1–5000 chars
- `imageUrls` (optional, required for image-to-video/kling): string[], URLs, max 10
- `videoUrls` (optional, required for kling): string[], URLs, max 1
- `aspectRatio` (optional): `portrait` | `landscape` | `16:9` | `9:16` | `Auto`
- `nFrames` (optional): `"10"` | `"15"`
- `selectedCharacter` (optional): string
- `characterOrientation` (optional): `image` | `video`
- `mode` (optional): `720p` | `1080p`

**Response 201 (VideoGenerationResponse)**

- `taskId`: string
- `model`: string
- `status`: `pending` | `processing` | `completed` | `failed`
- `creditsUsed`: number
- `newBalance`: number
- `estimatedCompletionTime`: string
- `createdAt`: number (ms epoch)

## GET /videos/:taskId

**Response 200 (VideoStatusResponse)**

- `taskId`: string
- `status`: `pending` | `processing` | `completed` | `failed`
- `model`: string
- `prompt`: string | undefined
- `creditsUsed`: number
- `resultUrl`: string (URI) | undefined — present when status is `completed`
- `createdAt`: number (ms epoch)
- `completedAt`: number | undefined
- `failCode`: string | undefined
- `failMessage`: string | undefined
- `progress`: number (0–100) | undefined

## GET /videos

**Query**

- `status` (optional): `pending` | `processing` | `completed` | `failed`
- `limit` (optional): number 1–100, default 50
- `page` (optional): number, default 1

**Response 200 (PaginatedVideosResponse)**

- `videos`: array of VideoStatusResponse (same shape as GET /videos/:taskId)
- `pagination`: `{ total: number, page: number, pageSize: number, hasMore: boolean }`

## Error body (ApiError)

All error responses (4xx, 5xx) use RFC 7807:

- `type`: string (URI)
- `title`: string
- `status`: number (HTTP code)
- `detail`: string | undefined
- `instance`: string | undefined
- `errors`: Record<string, string[]> | undefined (validation)

**Status codes**: 400 validation, 401 auth, 402 insufficient credits, 404 not found, 429 rate limit, 500 server error.
