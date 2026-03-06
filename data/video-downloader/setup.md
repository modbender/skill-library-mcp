# Setup - Video Downloader

Read this silently when `~/video-downloader/` is missing or empty.

## Operating Attitude

Answer the user's immediate download request first.
Keep setup lightweight and optional, then learn preferences from normal usage.

## Priority Order

### Workspace Integration First

Early in the conversation, ask if they want this behavior remembered for future video links.
If yes, store that preference in their local memory file.

### Then Learn Practical Defaults

Infer preferences from repeated requests:
- Preferred quality caps (best, 1080p, 720p)
- Preferred output format (mp4, webm, mkv, mp3)
- Preferred output location

Avoid long onboarding or configuration checklists.

### Keep Progress Visible

When downloading, report:
- URL being processed
- Selected quality and format
- Final saved file path

## Runtime Defaults

Until preferences are known:
- Download mode: single video only
- Quality: `best`
- Format: `mp4`
- Output directory: `~/Downloads`

## Status Labels

Use these status labels in memory:
- `ongoing` for active learning
- `complete` when defaults are stable
- `paused` when user asks to stop preference updates
- `never_ask` when user does not want setup or preference prompts
