---
name: freebeat-mcp
description: Generate AI music videos from any MCP client. Turn text prompts into cinematic music videos with multiple styles and modes.
---

# Freebeat MCP — AI Music Video Generator

## Setup

1. Get a free API key at [freebeat.ai/developers](https://freebeat.ai/developers)
2. Set environment variable: `FREEBEAT_API_KEY=your-key`

## Tools

### generate_music_video
Create an AI music video from a text prompt.
- `prompt` (required) — describe the video you want
- `mode` — `singing` | `storytelling` | `auto` (default: auto)
- `duration` — 5-180 seconds (default: 30)
- `style` — visual style (e.g. "cinematic", "anime", "retro VHS")

### check_generation_status
Check progress of a video generation job.
- `job_id` — returned by generate_music_video

### list_styles
Browse all available visual styles.

### get_account_info
Check remaining credits and account status.

## Example

> "Create a cinematic music video about a rainy night in Tokyo"

Returns a video URL + job metadata.
