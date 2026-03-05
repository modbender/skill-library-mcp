# YouTube Ready

Prompt:
`Edit ~/Desktop/episode.mp4 as a youtube video.`

If spend confirmation is requested by policy, approve and re-run with:
`confirm_spend: true`

Optional brand consistency step:
`studio_brand` with `action: "update"` and colors (for example `primary_color: "#1a73e8"`).

One-click brand setup alternative:
`studio_brand_import` with `url: "https://youtube.com/@yourchannel"` (preview), then repeat with `apply: true`.

Optional reusable media step:
`studio_assets` with `action: "upload"` and `asset_type: "intro"` (or `outro` / `watermark`) before upload.

Optional automation step:
include `webhook_url: "https://example.com/studio-callback"` on upload to skip polling.

Expected outputs:
- Main edited video
- 3 shorts
- Subtitles
- Transcription
