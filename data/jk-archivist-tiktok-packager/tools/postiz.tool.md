# Postiz Tool Notes

## Required Environment Variables

- `POSTIZ_BASE_URL` (default: `https://api.postiz.com/public/v1`)
- `POSTIZ_API_KEY`
- `POSTIZ_TIKTOK_INTEGRATION_ID`

## Endpoints Used

- `POST /upload`
- `POST /posts`

## TikTok Settings Required

- `privacy_level = SELF_ONLY`
- `content_posting_method = UPLOAD`

## Security

Never hardcode API tokens or integration IDs in source files.
